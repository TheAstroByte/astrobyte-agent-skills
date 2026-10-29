#!/usr/bin/env python3
"""Validate the Astrobyte catalog and portable skill packages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    from scripts.profile import load_object, load_operator, validate_operator
    from scripts.portable_profile import validate_resources
    from scripts.preferences import validate_preferences
    from scripts.packages import validate_dependencies, validate_package
    from scripts.routing import TEMPLATE_RELATIVE, validate_template_text
except ModuleNotFoundError:  # Direct execution from scripts/validate.py.
    from routing import TEMPLATE_RELATIVE, validate_template_text  # type: ignore[no-redef]
    from profile import load_object, load_operator, validate_operator  # type: ignore[no-redef]
    from portable_profile import validate_resources  # type: ignore[no-redef]
    from preferences import validate_preferences
    from packages import validate_dependencies, validate_package


REPO_ROOT = Path(__file__).resolve().parents[1]
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("missing YAML frontmatter")
    raw = text.split("\n---\n", 1)[0][4:]
    values: dict[str, str] = {}
    for line in raw.splitlines():
        match = re.match(r"^(name|description):\s*(.+)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip('"').strip("'")
    return values


def frontmatter_keys(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    raw = text.split("\n---\n", 1)[0][4:]
    return {
        match.group(1)
        for line in raw.splitlines()
        if (match := re.match(r"^([A-Za-z0-9_-]+):(?:\s|$)", line))
    }


def validate_repository(root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    catalog_path = root / "catalog.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"catalog.json: {exc}"]

    version_path = root / "VERSION"
    try:
        version = version_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        errors.append(f"VERSION: {exc}")
        version = ""
    if catalog.get("repository_version") != version:
        errors.append("catalog repository_version does not match VERSION")
    if catalog.get("sources", {}).get("astrobyte", {}).get("version") != version:
        errors.append("catalog sources.astrobyte.version does not match VERSION")
    try:
        template_version = load_object(root / "templates/preferences.json").get("baseline", {}).get("repository_version")
    except (OSError, ValueError, json.JSONDecodeError):
        template_version = None
    if template_version != version:
        errors.append("templates/preferences.json baseline repository_version does not match VERSION")
    try:
        errors.extend(f"{TEMPLATE_RELATIVE}: {error}" for error in validate_template_text((root / TEMPLATE_RELATIVE).read_text(encoding="utf-8")))
    except OSError as exc:
        errors.append(f"{TEMPLATE_RELATIVE}: {exc}")

    skills_root = root / "skills"
    errors.extend(validate_dependencies(catalog))
    directories = sorted(path.name for path in skills_root.iterdir() if path.is_dir() and (path / "SKILL.md").exists())
    cataloged = sorted(catalog.get("skills", {}).keys())
    if directories != cataloged:
        missing = sorted(set(cataloged) - set(directories))
        extra = sorted(set(directories) - set(cataloged))
        if missing:
            errors.append(f"cataloged skills missing from disk: {', '.join(missing)}")
        if extra:
            errors.append(f"skill directories missing from catalog: {', '.join(extra)}")

    for profile, members in catalog.get("profiles", {}).items():
        unknown = sorted(set(members) - set(cataloged))
        duplicates = sorted({name for name in members if members.count(name) > 1})
        if unknown:
            errors.append(f"profile {profile} has unknown skills: {', '.join(unknown)}")
        if duplicates:
            errors.append(f"profile {profile} has duplicates: {', '.join(duplicates)}")
        optional = sorted(name for name in members if catalog.get("skills", {}).get(name, {}).get("tier") == "optional")
        if optional:
            errors.append(f"profile {profile} includes optional skills: {', '.join(optional)}")
        missing_required = sorted(set(catalog.get("required_skills", [])) - set(members))
        if missing_required:
            errors.append(f"profile {profile} is missing required skills: {', '.join(missing_required)}")

    for name in directories:
        path = skills_root / name / "SKILL.md"
        errors.extend(validate_package(path.parent, catalog.get("skills", {}).get(name, {})))
        try:
            metadata = frontmatter(path)
        except ValueError as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            continue
        declared_name = metadata.get("name", "")
        description = metadata.get("description", "")
        if declared_name != name:
            errors.append(f"{path.relative_to(root)}: name {declared_name!r} does not match directory")
        if not NAME_PATTERN.fullmatch(declared_name):
            errors.append(f"{path.relative_to(root)}: invalid skill name")
        if len(declared_name) > 64:
            errors.append(f"{path.relative_to(root)}: skill name exceeds 64 characters")
        if not 1 <= len(description) <= 1024:
            errors.append(f"{path.relative_to(root)}: description must be 1 to 1024 characters")
        if "<" in description or ">" in description:
            errors.append(f"{path.relative_to(root)}: description contains an angle bracket")
        text = path.read_text(encoding="utf-8")
        if catalog.get("skills", {}).get(name, {}).get("explicit_only"):
            if not re.search(r"(?m)^disable-model-invocation:\s*true\s*$", text.split("\n---\n", 1)[0]):
                errors.append(f"{path.relative_to(root)}: explicit-only skill must disable model invocation")
        if name.startswith("astrobyte-") or name == "setup-astrobyte-skills":
            allowed_keys = {"name", "description", "license", "allowed-tools", "metadata"}
            if catalog.get("skills", {}).get(name, {}).get("explicit_only"):
                allowed_keys.add("disable-model-invocation")
            unexpected = frontmatter_keys(path) - allowed_keys
            if unexpected:
                errors.append(f"{path.relative_to(root)}: unexpected frontmatter keys: {', '.join(sorted(unexpected))}")
            if "TODO" in text:
                errors.append(f"{path.relative_to(root)}: unresolved TODO")
        if len(text.splitlines()) > 500:
            errors.append(f"{path.relative_to(root)}: SKILL.md exceeds 500 lines")
        for raw_link in LINK_PATTERN.findall(text):
            link = raw_link.split("#", 1)[0]
            if not link or "://" in link or link.startswith("mailto:"):
                continue
            target = (path.parent / link).resolve()
            if not target.exists():
                errors.append(f"{path.relative_to(root)}: missing linked file {raw_link}")

        openai_yaml = path.parent / "agents" / "openai.yaml"
        if openai_yaml.exists():
            content = openai_yaml.read_text(encoding="utf-8")
            prompts = [line for line in content.splitlines() if "default_prompt:" in line]
            if prompts and f"${name}" not in prompts[0]:
                errors.append(f"{openai_yaml.relative_to(root)}: default_prompt must mention ${name}")

    for source, metadata in catalog.get("sources", {}).items():
        if source == "astrobyte":
            continue
        if not metadata.get("commit"):
            errors.append(f"source {source} has no pinned commit")

    repository_path = root / "config" / "repository.json"
    try:
        repository = load_object(repository_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"config/repository.json: {exc}")
        repository = {}
    default_operator = repository.get("default_operator_profile")
    profile_directories = sorted(
        path for path in (root / "profiles").iterdir() if path.is_dir() and (path / "profile.json").exists()
    )
    if default_operator not in {path.name for path in profile_directories}:
        errors.append("config/repository.json points to a missing default operator profile")
    ci = repository.get("ci")
    if not isinstance(ci, dict) or not isinstance(ci.get("enabled"), bool):
        errors.append("config/repository.json ci.enabled must be a boolean")
    elif ci["enabled"] and not (root / ".github" / "workflows" / "ci.yml").is_file():
        errors.append("CI is enabled but .github/workflows/ci.yml is missing")

    for directory in profile_directories:
        try:
            operator, registry, _ = load_operator(root, directory.name)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{directory.relative_to(root)}: {exc}")
            continue
        for error in validate_operator(operator, registry, directory, catalog):
            errors.append(f"{directory.relative_to(root)}: {error}")

    for template in ("operator-profile.json", "machines.json"):
        try:
            load_object(root / "templates" / template)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"templates/{template}: {exc}")

    errors.extend(validate_resources(root))
    try:
        validate_preferences(load_object(root / "templates/preferences.json"))
    except (OSError, ValueError) as exc:
        errors.append(f"templates/preferences.json: {exc}")
    return errors


def main() -> int:
    errors = validate_repository()
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"  {error}")
        return 1
    count = len(json.loads((REPO_ROOT / "catalog.json").read_text(encoding="utf-8"))["skills"])
    print(f"Validated {count} skills and all catalog profiles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
