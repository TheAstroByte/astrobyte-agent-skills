#!/usr/bin/env python3
"""Read or save the operator's approved reviewer for one harness.

The review gate asks for a reviewer on first use and saves the approved choice here.
Stored values are data describing a model and route, never commands or credentials.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


def configuration_directory(explicit: Path | None) -> Path:
    """Resolve local state the same way the workflow helper does."""
    if explicit is not None:
        root = explicit.expanduser().resolve()
    elif os.environ.get("ASTROBYTE_CONFIG"):
        selected = Path(os.environ["ASTROBYTE_CONFIG"]).expanduser().resolve()
        if selected.is_dir():
            selected = selected / "config.json"
        if not selected.is_file():
            raise ValueError(f"Explicit ASTROBYTE_CONFIG is unavailable: {selected}")
        root = selected.parent
    else:
        root = Path(os.environ.get("ASTROBYTE_CONFIG_HOME", "~/.config/astrobyte-agent-skills")).expanduser().resolve()
    if root == Path(root.anchor):
        raise ValueError("The reviewer state directory cannot be a filesystem root")
    return root


def text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 for c in value):
        raise ValueError(f"Invalid {name}")
    return value.strip()


def reviewer(value: Any) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) - {"model", "route", "effort"} or not {"model", "route"} <= set(value):
        raise ValueError("Reviewer needs model and route, with optional effort")
    return {key: text(item, f"reviewer {key}") for key, item in value.items()}


def state_path(root: Path, harness: str) -> Path:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", harness):
        raise ValueError("Harness must be a lowercase name")
    return root / "pr-workflows" / "reviewers" / f"{harness}.json"


def save(path: Path, value: dict[str, Any]) -> None:
    serialized = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.is_file() and path.read_text(encoding="utf-8") == serialized:
        return
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = handle.name
            handle.write(serialized)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def run(args: argparse.Namespace) -> dict[str, Any]:
    path = state_path(configuration_directory(args.state_dir), args.harness)
    if args.action == "set":
        loaded = json.loads(args.input.read_text(encoding="utf-8"))
        value = {"schema_version": 1, "harness": args.harness, "reviewer": reviewer(loaded)}
        save(path, value)
        return {"configured": True, **value}
    if not path.exists():
        return {"configured": False, "harness": args.harness}
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(value, dict)
        or set(value) != {"schema_version", "harness", "reviewer"}
        or type(value["schema_version"]) is not int
        or value["schema_version"] != 1
        or value["harness"] != args.harness
    ):
        raise ValueError("Stored reviewer does not match its harness or schema")
    return {"configured": True, "schema_version": 1, "harness": args.harness, "reviewer": reviewer(value["reviewer"])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, help="Override local state location")
    actions = parser.add_subparsers(dest="action", required=True)
    for action in ("show", "set"):
        command = actions.add_parser(action)
        command.add_argument("--harness", required=True)
        if action == "set":
            command.add_argument("--input", required=True, type=Path, help="Approved JSON object with model and route")
    args = parser.parse_args()
    try:
        result = run(args)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Reviewer configuration error: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
