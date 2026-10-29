#!/usr/bin/env python3
"""Install the explicit adoption entry point before full machine setup."""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts import install
except ModuleNotFoundError:  # Direct execution from scripts/bootstrap.py.
    import install  # type: ignore[no-redef]


ENTRY_SKILLS = ("adopt-skill-stack", "unslop")


def build_bootstrap_plan(harnesses: list[str], home: Path) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    for destination, destination_harnesses in install.destination_groups(harnesses, home).items():
        for skill in ENTRY_SKILLS:
            source = install.REPO_ROOT / "skills" / skill
            target = destination / skill
            source_hash = install.tree_hash(source)
            if not target.exists():
                status = "new"
            elif install.tree_hash(target) == source_hash:
                status = "same"
            else:
                status = "conflict"
            plan.append(
                {
                    "skill": skill,
                    "source": source,
                    "target": target,
                    "hash": source_hash,
                    "status": status,
                    "harnesses": destination_harnesses,
                }
            )
    return plan


def print_bootstrap_plan(plan: list[dict[str, Any]], home: Path) -> None:
    print("\nBootstrap plan")
    for item in plan:
        labels = ", ".join(item["harnesses"])
        print(f"  {item['status']:8} {item['skill']} -> {item['target']} ({labels})")
    conflicts = [item for item in plan if item["status"] == "conflict"]
    if conflicts:
        print(f"  Conflicts will be backed up under {install.config_dir(home) / 'backups'}")


def apply_bootstrap_plan(plan: list[dict[str, Any]], home: Path) -> list[Path]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_root = install.config_dir(home) / "backups" / f"bootstrap-{timestamp}"
    backups: list[Path] = []
    for item in plan:
        if item["status"] == "same":
            continue
        source = Path(item["source"])
        target = Path(item["target"])
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            relative = Path(*target.parts[1:]) if target.is_absolute() else target
            backup = backup_root / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), str(backup))
            backups.append(backup)
        shutil.copytree(source, target)
    return backups


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
