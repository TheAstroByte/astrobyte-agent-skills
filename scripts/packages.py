"""Resolve declared skill dependencies and check package-contained resources."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote


LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def resolve_selection(catalog: dict[str, Any], requested: list[str]) -> list[str]:
    """Expand hard dependencies only; reject unknown names and dependency cycles."""
    selected: list[str] = []
    active: set[str] = set()
    skills = catalog["skills"]

    def visit(name: str) -> None:
        if name not in skills:
            raise ValueError(f"Unknown skill dependency or selection: {name}")
        if name in active:
            raise ValueError(f"Skill dependency cycle at {name}")
        if name in selected:
            return
        active.add(name)
        dependencies = skills[name].get("dependencies", [])
        if not isinstance(dependencies, list) or any(not isinstance(item, str) for item in dependencies):
            raise ValueError(f"Invalid dependencies for {name}")
        for dependency in dependencies:
            visit(dependency)
        active.remove(name)
        selected.append(name)

    for name in requested:
        visit(name)
    return selected


def validate_package(package: Path, metadata: dict[str, Any]) -> list[str]:
    """Validate a copied package without relying on its source repository."""
    errors: list[str] = []
    root = package.resolve()
    if not (package / "SKILL.md").is_file():
        return [f"{package.name}: missing SKILL.md"]

    def check(raw: str, origin: Path) -> None:
        path = Path(unquote(raw))
        target = (origin.parent / path).resolve()
        if path.is_absolute() or not target.is_relative_to(root):
            errors.append(f"{package.name}/{origin.relative_to(package)}: resource escapes package: {raw}")
        elif not target.is_file():
            errors.append(f"{package.name}/{origin.relative_to(package)}: missing resource: {raw}")

    resources = metadata.get("runtime_resources", [])
    if not isinstance(resources, list) or any(not isinstance(item, str) for item in resources):
        errors.append(f"{package.name}: invalid runtime_resources")
    else:
        for resource in resources:
            check(resource, package / "SKILL.md")
    for document in package.rglob("*.md"):
        # Fenced templates demonstrate project paths rather than package resources.
        text = re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", document.read_text(encoding="utf-8"))
        for raw in LINK_PATTERN.findall(text):
            link = raw.strip().split("#", 1)[0]
            if not link or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", link):
                continue
            check(link, document)
    # Check resources reached by symlinks even if a Markdown pointer omits them.
    for entry in package.rglob("*"):
        if entry.is_symlink() and not entry.resolve().is_relative_to(root):
            errors.append(f"{package.name}: symlink escapes package: {entry.relative_to(package)}")
    return errors


def validate_dependencies(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    skills = catalog["skills"]
    for name, metadata in skills.items():
        try:
            resolve_selection(catalog, [name])
        except ValueError as exc:
            errors.append(str(exc))
        for field in ("conditional_dependencies", "suggestions"):
            values = metadata.get(field, [])
            if not isinstance(values, list):
                errors.append(f"{name}: invalid {field}")
                continue
            for value in values:
                if not isinstance(value, dict) or value.get("skill") not in skills or not isinstance(value.get("when"), str) or not value["when"].strip():
                    errors.append(f"{name}: invalid {field} entry")
    for profile, members in catalog.get("profiles", {}).items():
        try:
            missing = set(resolve_selection(catalog, members)) - set(members)
            if missing:
                errors.append(f"profile {profile} missing hard dependencies: {', '.join(sorted(missing))}")
        except ValueError as exc:
            errors.append(f"profile {profile}: {exc}")
    return errors
