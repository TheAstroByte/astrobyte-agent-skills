#!/usr/bin/env python3
"""Read workflow policy and save approved, local first-use selections."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any


PACKAGE = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = {"review_method": "baseline", "council_round_limit": 3, "t3": False}


def object_file(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def fields(value: dict[str, Any], allowed: set[str], required: set[str]) -> None:
    if set(value) - allowed or required - set(value):
        raise ValueError("Unexpected or missing configuration fields")


def text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 for c in value):
        raise ValueError(f"Invalid {name}")
    return value.strip()


def council(value: dict[str, Any]) -> dict[str, Any]:
    fields(value, {"members"}, {"members"})
    members = value["members"]
    if not isinstance(members, list) or len(members) < 2:
        raise ValueError("Council requires at least two approved members")
    result = []
    seen = set()
    for member in members:
        if not isinstance(member, dict):
            raise ValueError("Council members must be objects")
        fields(member, {"model", "route", "label", "provider"}, {"model", "route"})
        normalized = {key: text(item, f"member {key}") for key, item in member.items()}
        key = (normalized["model"], normalized["route"])
        if key in seen:
            raise ValueError("Council members must have distinct model and route pairs")
        seen.add(key)
        result.append(normalized)
    return {"members": result}


def repository_policy(value: dict[str, Any]) -> dict[str, Any]:
    fields(value, {"required_bots", "advisory_bots"}, {"required_bots", "advisory_bots"})
    result: dict[str, list[str]] = {}
    for field in ("required_bots", "advisory_bots"):
        if not isinstance(value[field], list):
            raise ValueError(f"{field} must be a list")
        names = [text(item, field) for item in value[field]]
        if len({name.casefold() for name in names}) != len(names):
            raise ValueError(f"{field} must contain distinct names")
        result[field] = names
    if {name.casefold() for name in result["required_bots"]} & {name.casefold() for name in result["advisory_bots"]}:
        raise ValueError("A bot cannot be both required and advisory")
    return result


def configuration_directory(explicit: Path | None) -> Path:
    if explicit is not None:
        root = explicit.expanduser().resolve()
    elif os.environ.get("ASTROBYTE_CONFIG"):
        selected = Path(os.environ["ASTROBYTE_CONFIG"]).expanduser().resolve()
        if selected.is_dir():
            selected = selected / "config.json"
        if not selected.is_file():
            raise ValueError(f"Explicit ASTROBYTE_CONFIG is unavailable: {selected}")
        object_file(selected)
        root = selected.parent
    else:
        root = Path(os.environ.get("ASTROBYTE_CONFIG_HOME", "~/.config/astrobyte-agent-skills")).expanduser().resolve()
    if root == Path(root.anchor):
        raise ValueError("The workflow state directory cannot be a filesystem root")
    return root


def policy(project: Path) -> dict[str, Any]:
    runtime = PACKAGE.parent / "astrobyte-mode" / "scripts" / "runtime_config.py"
    if not runtime.is_file():
        raise ValueError("Missing astrobyte-mode runtime; install the workflow's declared dependencies")
    spec = importlib.util.spec_from_file_location("_astrobyte_workflow_runtime", runtime)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load the installed Astrobyte runtime resolver")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(runtime.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    result = module.resolve(runtime.parents[1], project.resolve(), Path.home())
    return {
        "pr_workflows": {**DEFAULT_POLICY, **result.get("pr_workflows", {})},
        "sources": result.get("pr_workflow_sources", {}),
    }


def state_key(args: argparse.Namespace) -> tuple[Path, dict[str, str]]:
    root = configuration_directory(args.state_dir) / "pr-workflows"
    if args.kind == "council":
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", args.harness):
            raise ValueError("Harness must be a lowercase name")
        return root / "councils" / f"{args.harness}.json", {"harness": args.harness}
    parts = args.repo.split("/")
    if len(parts) == 2:
        parts.insert(0, "github.com")
    if len(parts) != 3 or not re.fullmatch(r"[A-Za-z0-9.-]+(?::[0-9]+)?", parts[0]):
        raise ValueError("Repository must be [HOST/]OWNER/REPO")
    if any(not re.fullmatch(r"[A-Za-z0-9_.-]+", item) or item in {".", ".."} for item in parts[1:]):
        raise ValueError("Invalid repository owner or name")
    repo = "/".join(parts).lower()
    base = text(args.base, "base branch")
    if any(c.isspace() for c in base):
        raise ValueError("Base branch cannot contain whitespace")
    identity = {"repository": repo, "base": base}
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    return root / "repositories" / f"{digest}.json", identity


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
    if args.kind == "policy":
        return policy(args.project)
    path, identity = state_key(args)
    payload_key = "council" if args.kind == "council" else "policy"
    validate = council if args.kind == "council" else repository_policy
    if args.action == "set":
        value = {"schema_version": 1, **identity, payload_key: validate(object_file(args.input))}
        save(path, value)
    elif path.exists():
        value = object_file(path)
        fields(value, {"schema_version", *identity, payload_key}, {"schema_version", *identity, payload_key})
        if type(value["schema_version"]) is not int or value["schema_version"] != 1 or any(value[key] != item for key, item in identity.items()):
            raise ValueError("Stored workflow state does not match its requested key or schema")
        if not isinstance(value[payload_key], dict):
            raise ValueError("Invalid stored workflow configuration")
        value[payload_key] = validate(value[payload_key])
    else:
        return {"configured": False, **identity}
    return {"configured": True, **value}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, help="Override local state location; does not change runtime policy precedence")
    commands = parser.add_subparsers(dest="kind", required=True)
    selection = commands.add_parser("policy", help="Read effective personal workflow options through the installed router")
    selection.add_argument("--project", type=Path, default=Path.cwd())
    for name in ("council", "repository"):
        group = commands.add_parser(name, help=f"Read or save approved local {name} selection")
        actions = group.add_subparsers(dest="action", required=True)
        for action in ("show", "set"):
            command = actions.add_parser(action)
            if name == "council":
                command.add_argument("--harness", required=True)
            else:
                command.add_argument("--repo", required=True, help="[HOST/]OWNER/REPO")
                command.add_argument("--base", required=True)
            if action == "set":
                command.add_argument("--input", required=True, type=Path, help="Approved JSON object; stored route values are data, never commands")
    args = parser.parse_args()
    try:
        result = run(args)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"Workflow configuration error: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
