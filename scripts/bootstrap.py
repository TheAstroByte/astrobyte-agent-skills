#!/usr/bin/env python3
"""Install the explicit adoption entry point before full machine setup."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    from scripts import install
except ModuleNotFoundError:  # Direct execution from scripts/bootstrap.py.
    import install  # type: ignore[no-redef]


ENTRY_SKILLS = ("adopt-skill-stack", "unslop")


def bootstrap_answers(harnesses: list[str], home: Path) -> dict[str, Any]:
    profile, _, _ = install.load_operator(install.REPO_ROOT)
    preference_path = install.config_dir(home) / "preferences.json"
    preferences = install.load_json(preference_path) if preference_path.exists() else None
    answers = install.resolve_install_answers(home, profile, harnesses, preferences)
    return install.validate_answers(answers, install.load_json(install.CATALOG_PATH))


def build_bootstrap_plan(harnesses: list[str], home: Path) -> list[dict[str, Any]]:
    # Limit this run, without saving the bootstrap subset as an adoption choice.
    answers = {
        **bootstrap_answers(harnesses, home),
        "harnesses": harnesses,
        "selected_skills": list(ENTRY_SKILLS),
        "optional_skills": [],
        "_removed_optional_skills": [],
    }
    return install.build_plan(answers, home, install.load_json(install.CATALOG_PATH), prune=False)


def print_bootstrap_plan(plan: list[dict[str, Any]], home: Path) -> None:
    print("\nBootstrap plan")
    for item in plan:
        labels = ", ".join(item["harnesses"])
        print(f"  {item['status']:8} {item['skill']} -> {item['target']} ({labels})")
    conflicts = [item for item in plan if item["status"] == "conflict"]
    if conflicts:
        print(f"  Conflicts will be backed up under {install.config_dir(home) / 'backups'}")


def apply_bootstrap_plan(plan: list[dict[str, Any]], home: Path) -> list[Path]:
    harnesses = list(dict.fromkeys(name for item in plan for name in item["harnesses"]))
    answers = bootstrap_answers(harnesses, home)
    return [Path(path) for path in install.apply_plan(answers, plan, home, preserve_existing=True)]


def parse_harnesses(raw: str) -> list[str]:
    harnesses = list(dict.fromkeys(item.strip().lower() for item in raw.split(",") if item.strip()))
    unknown = sorted(set(harnesses) - install.HARNESSES.keys())
    if not harnesses:
        raise ValueError("Select at least one harness")
    if unknown:
        raise ValueError(f"Unknown harnesses: {', '.join(unknown)}")
    return harnesses


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harnesses", help="Comma-separated known harnesses")
    parser.add_argument("--dry-run", action="store_true", help="Print the bootstrap plan without writing")
    parser.add_argument("--yes", action="store_true", help="Apply the bootstrap plan without a final prompt")
    parser.add_argument("--home", type=Path, default=Path.home(), help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    home = args.home.expanduser().resolve()
    if home == Path(home.anchor):
        raise ValueError("The bootstrap home cannot be a filesystem root")

    if args.harnesses:
        harnesses = parse_harnesses(args.harnesses)
    else:
        detected = install.detect_harnesses(home)
        print(f"Detected harnesses: {', '.join(detected) if detected else 'none'}")
        harnesses = install.ask_harnesses(detected)

    plan = build_bootstrap_plan(harnesses, home)
    print_bootstrap_plan(plan, home)
    if args.dry_run:
        print("Dry run complete. No files changed.")
        return 0
    if not args.yes and not install.ask_bool("Install the adoption entry point", False):
        print("Bootstrap cancelled. No files changed.")
        return 0

    backups = apply_bootstrap_plan(plan, home)
    print("Bootstrap installed adopt-skill-stack and required unslop instructions.")
    if backups:
        print(f"Backed up {len(backups)} conflicting skill directories.")
    print('Say "Adopt this skill stack" in any selected agent product.')
    print("Explicit forms: $adopt-skill-stack in Codex; /adopt-skill-stack where slash invocation is used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
