#!/usr/bin/env python3
"""Generate Claude Code plugin packages from the canonical skills.

Each package in catalog.json `packages` becomes `plugins/<package>/` with real copies of its
skills, a `.claude-plugin/plugin.json`, and the overlays in `plugins/overlays.json`. The
repository root `.claude-plugin/marketplace.json` lists every package. Overlays apply only to
the copies; `skills/` stays canonical. Run with `--check` to verify without writing.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    from scripts.packages import validate_package
except ModuleNotFoundError:
    from packages import validate_package

REPO_ROOT = Path(__file__).resolve().parents[1]
MAX_DESCRIPTION = 200
MARKETPLACE = "astrobyte-skills"
FETCH_NOTICE = (
    "> Packaged copy: commands below assume tools already installed in the project. "
    "Run them with `npx --no-install` or the project's own scripts; do not fetch and run missing packages.\n\n"
)
HIDE = "disable-model-invocation: true"
GENERATED_FILES = (".claude-plugin/plugin.json",)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def description(text: str) -> str:
    head = text[4:].split("\n---\n", 1)[0]
    match = re.search(r"(?m)^description:\s*(.+)$", head)
    return match.group(1).strip().strip('"').strip("'") if match else ""


def set_visibility(text: str, visible: bool) -> str:
    """Make model invocation match the package's visibility list, in the copy only."""
    head, sep, body = text[4:].partition("\n---\n")
    lines = [line for line in head.split("\n") if not re.match(r"^disable-model-invocation:", line)]
    if not visible:
        index = next(i for i, line in enumerate(lines) if line.startswith("description:"))
        lines.insert(index + 1, HIDE)
    return "---\n" + "\n".join(lines) + sep + body


def add_after_frontmatter(text: str, block: str) -> str:
    if text.startswith("---\n") and "\n---\n" in text[4:]:
        head, sep, body = text[4:].partition("\n---\n")
        return "---\n" + head + sep + "\n" + block + body.lstrip("\n")
    return block + text


def apply_overlays(package_skill: Path, edits: dict[str, list[dict[str, str]]]) -> None:
    for relative, replacements in edits.items():
        path = package_skill / relative
        text = path.read_text(encoding="utf-8")
        for item in replacements:
            count = text.count(item["find"])
            if count != 1:
                raise ValueError(f"overlay for {package_skill.name}/{relative} matched {count} times: {item['find'][:60]!r}")
            text = text.replace(item["find"], item["replace"])
        path.write_text(text, encoding="utf-8")


def plan(catalog: dict[str, Any]) -> list[str]:
    """Return package definition errors before anything is written."""
    errors: list[str] = []
    packages = catalog.get("packages", {})
    skills = catalog["skills"]
    owner: dict[str, str] = {}
    for name, package in packages.items():
        members = package.get("skills", [])
        for skill in members:
            if skill not in skills:
                errors.append(f"package {name}: unknown skill {skill}")
            elif skill in owner:
                errors.append(f"package {name}: {skill} is already in {owner[skill]}")
            else:
                owner[skill] = name
        for skill in package.get("visible", members):
            if skill not in members:
                errors.append(f"package {name}: visible skill {skill} is not a member")
        dependencies = package.get("depends_on", [])
        provided = set(members) | {s for dep in dependencies for s in packages.get(dep, {}).get("skills", [])}
        for dep in dependencies:
            if dep not in packages:
                errors.append(f"package {name}: unknown dependency {dep}")
        # A trimmed copy may drop hard dependencies that only its removed branches need.
        dropped = catalog.get("package_dependency_overrides", {}).get(name, {})
        for skill in members:
            if skill not in skills:
                continue
            needed = set(skills[skill].get("dependencies", [])) - set(dropped.get(skill, []))
            for dependency in sorted(needed - provided):
                errors.append(f"package {name}: {skill} needs {dependency}, which is not in the package or its dependencies")
    return errors


def build(root: Path, output: Path) -> list[str]:
    catalog = load_json(root / "catalog.json")
    overlays = load_json(root / "plugins" / "overlays.json")
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    errors = plan(catalog)
    if errors:
        return errors
    marketplace = {"name": MARKETPLACE, "owner": {"name": "TheAstroByte"}, "plugins": []}
    for name, package in catalog["packages"].items():
        members = package["skills"]
        visible = set(package.get("visible", members))
        target = output / "plugins" / name
        for skill in members:
            destination = target / "skills" / skill
            shutil.copytree(root / "skills" / skill, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            apply_overlays(destination, overlays.get("skills", {}).get(skill, {}))
            for relative in overlays.get("remove", {}).get(skill, []):
                (destination / relative).unlink()
            skill_md = destination / "SKILL.md"
            text = set_visibility(skill_md.read_text(encoding="utf-8"), skill in visible)
            notice = overlays.get("notices", {}).get(skill)
            if notice:
                text = add_after_frontmatter(text, f"> {notice}\n\n")
            skill_md.write_text(text, encoding="utf-8")
            for document in sorted(destination.rglob("*.md")):
                content = document.read_text(encoding="utf-8")
                if re.search(r"(?m)\bnpx (?!--no-install)", content):
                    document.write_text(add_after_frontmatter(content, FETCH_NOTICE), encoding="utf-8")
            text = skill_md.read_text(encoding="utf-8")
            if len(description(text)) > MAX_DESCRIPTION:
                errors.append(f"plugins/{name}/skills/{skill}: description exceeds {MAX_DESCRIPTION} characters")
            metadata = dict(catalog["skills"][skill])
            metadata["runtime_resources"] = [
                item for item in metadata.get("runtime_resources", [])
                if item not in overlays.get("remove", {}).get(skill, [])
            ]
            errors.extend(f"plugins/{name}/{e}" for e in validate_package(destination, metadata))
            for raw in re.findall(r"`(references/[\w./-]+\.(?:md|json))`", text):
                if not (destination / raw).is_file():
                    errors.append(f"plugins/{name}/skills/{skill}: missing backtick resource {raw}")
        # depends_on is checked above but not emitted: core is installed natively (see README),
        # so an optional plugin must not pull a second, plugin copy of core into the session.
        manifest = {"name": name, "version": version, "description": package["description"]}
        (target / ".claude-plugin").mkdir(parents=True, exist_ok=True)
        (target / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        marketplace["plugins"].append({"name": name, "source": f"./plugins/{name}", "description": package["description"]})
    (output / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (output / ".claude-plugin" / "marketplace.json").write_text(json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")
    return errors


def tree(root: Path, skip: set[Path]) -> dict[str, tuple[str, bytes | str]]:
    """Map each relative path to its type and content without following symlinks."""
    entries: dict[str, tuple[str, bytes | str]] = {}
    for path in sorted(root.rglob("*")):
        if path in skip or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            entries[relative] = ("symlink", str(path.readlink()))
        elif path.is_dir():
            entries[relative] = ("dir", "")
        elif path.is_file():
            entries[relative] = ("file", path.read_bytes())
        else:
            entries[relative] = ("other", "")
    return entries


def compare(expected: Path, actual: Path) -> list[str]:
    differences: list[str] = []
    for relative in ("plugins", ".claude-plugin"):
        if not (actual / relative).exists():
            differences.append(f"{relative}: missing")
            continue
        want = tree(expected / relative, set())
        have = tree(actual / relative, {actual / "plugins" / "overlays.json"})
        for path in sorted(want.keys() | have.keys()):
            if path not in have:
                differences.append(f"{relative}/{path}: missing")
            elif path not in want:
                differences.append(f"{relative}/{path}: unexpected")
            elif want[path][0] != have[path][0]:
                differences.append(f"{relative}/{path}: is a {have[path][0]}, expected a {want[path][0]}")
            elif want[path] != have[path]:
                differences.append(f"{relative}/{path}: stale")
    return differences


def check(root: Path = REPO_ROOT) -> list[str]:
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        (output / "plugins").mkdir()
        errors = build(root, output)
        if errors:
            return errors
        return [f"{item}; run python3 scripts/plugin_packages.py" for item in compare(output, root)]


def write(root: Path = REPO_ROOT) -> list[str]:
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        (output / "plugins").mkdir()
        errors = build(root, output)
        if errors:
            return errors
        packages = load_json(root / "catalog.json")["packages"]
        for existing in sorted((root / "plugins").iterdir()) if (root / "plugins").is_dir() else []:
            if existing.name in packages or not existing.is_dir():
                continue
            if not (existing / ".claude-plugin" / "plugin.json").is_file():
                return [f"plugins/{existing.name}: not a generated package; remove or move it before regenerating"]
            shutil.rmtree(existing)
        for name in packages:
            shutil.rmtree(root / "plugins" / name, ignore_errors=True)
            shutil.copytree(output / "plugins" / name, root / "plugins" / name)
        (root / ".claude-plugin").mkdir(exist_ok=True)
        shutil.copy2(output / ".claude-plugin" / "marketplace.json", root / ".claude-plugin" / "marketplace.json")
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check generated packages without writing")
    args = parser.parse_args()
    errors = check() if args.check else write()
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if not errors:
        print("Plugin packages match the catalog." if args.check else "Generated plugin packages.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
