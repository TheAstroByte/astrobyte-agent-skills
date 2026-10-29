"""Load and validate committed operator profiles."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


HANDLE_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DELIVERY_MODES = {"explore", "prototype", "durable", "production"}
MACHINE_DELIVERY_MODES = DELIVERY_MODES | {"ask"}
AUTONOMY_PRESETS = {"exact-scope", "guided-implementation", "bounded-autonomy", "prototype-sprint"}
COMMUNICATION_STYLES = {"strictly-comply", "collaborative-challenge", "actively-challenge"}
EXPLANATION_LEVELS = {"expert-concise", "collaborative", "guided-teaching"}
MACHINE_POLICIES = {"inherit-personal-default", "ask-every-install", "ask-every-project"}
UPDATE_POLICIES = {"manual-only", "notify", "manual-reviewed", "auto-reviewed-pr", "auto-merge-gated"}
GIT_IDENTITY_MODES = {"dual-attribution", "agent-only", "human-with-agent-trailer", "disabled"}
TRAILER_KEY_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9-]*$")


def load_object(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def operator_directory(root: Path, handle: str | None = None) -> Path:
    repository = load_object(root / "config" / "repository.json")
    selected = handle or repository.get("default_operator_profile")
    if not isinstance(selected, str) or not HANDLE_PATTERN.fullmatch(selected):
        raise ValueError("config/repository.json has an invalid default_operator_profile")
    return root / "profiles" / selected


def load_operator(root: Path, handle: str | None = None) -> tuple[dict[str, Any], dict[str, Any], Path]:
    directory = operator_directory(root, handle)
    profile = load_object(directory / "profile.json")
    registry_name = profile.get("machine_registry", "machines.json")
    if not isinstance(registry_name, str) or Path(registry_name).name != registry_name:
        raise ValueError("machine_registry must name a file in the operator profile directory")
    registry_path = directory / registry_name
    registry = load_object(registry_path)
    return profile, registry, directory


def validate_operator(
    profile: dict[str, Any],
    registry: dict[str, Any],
    profile_dir: Path,
    catalog: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    handle = profile.get("handle")
    if not isinstance(handle, str) or not HANDLE_PATTERN.fullmatch(handle):
        errors.append("profile handle must use lowercase kebab-case")
    elif profile_dir.name != handle:
        errors.append(f"profile directory {profile_dir.name!r} does not match handle {handle!r}")

    if profile.get("schema_version") != 1:
        errors.append("profile schema_version must be 1")
    if profile.get("identity_mode") not in {"handle", "full-rename"}:
        errors.append("identity_mode must be handle or full-rename")
    if profile.get("skill_profile") not in catalog.get("profiles", {}):
        errors.append(f"unknown skill_profile: {profile.get('skill_profile')!r}")

    working_agreement = profile.get("working_agreement")
    if (
        not isinstance(working_agreement, str)
        or Path(working_agreement).name != working_agreement
        or not (profile_dir / working_agreement).is_file()
    ):
        errors.append("working_agreement must name a file in the operator profile directory")
    machine_registry = profile.get("machine_registry")
    if (
        not isinstance(machine_registry, str)
        or Path(machine_registry).name != machine_registry
        or not (profile_dir / machine_registry).is_file()
    ):
        errors.append("machine_registry must name a file in the operator profile directory")

    defaults = profile.get("defaults")
    if not isinstance(defaults, dict):
        errors.append("defaults must be an object")
    else:
        choices = {
            "autonomy_preset": AUTONOMY_PRESETS,
            "communication_style": COMMUNICATION_STYLES,
            "explanation_level": EXPLANATION_LEVELS,
            "delivery_mode": DELIVERY_MODES,
            "machine_delivery_policy": MACHINE_POLICIES,
            "git_workflow": {"branch", "worktree", "current-tree"},
            "issue_tracker": {"local", "github", "linear", "none"},
            "skill_update_policy": UPDATE_POLICIES,
        }
        for key, allowed in choices.items():
            if defaults.get(key) not in allowed:
                errors.append(f"invalid defaults.{key}: {defaults.get(key)!r}")
        if not isinstance(defaults.get("ci_validation"), bool):
            errors.append("defaults.ci_validation must be a boolean")

    skills = profile.get("skills")
    if not isinstance(skills, dict):
        errors.append("skills must be an object")
    else:
        required = skills.get("required")
        if not isinstance(required, list) or "unslop" not in required:
            errors.append("skills.required must include unslop")
        selected_profile = catalog.get("profiles", {}).get(profile.get("skill_profile"), [])
        missing = sorted(set(required) - set(selected_profile)) if isinstance(required, list) else []
        if missing:
            errors.append(f"required skills missing from selected profile: {', '.join(missing)}")
        if not isinstance(skills.get("require_independent_feedback"), bool):
            errors.append("skills.require_independent_feedback must be a boolean")

    repository = profile.get("repository")
    if not isinstance(repository, dict):
        errors.append("repository must be an object")
    else:
        if repository.get("visibility") not in {"private", "public"}:
            errors.append("repository.visibility must be private or public")
        if repository.get("publication") not in {"independent-copy", "github-fork", "local-only"}:
            errors.append("repository.publication has an invalid value")
        if repository.get("initial_change") not in {"pull-request", "direct-main", "local-only"}:
            errors.append("repository.initial_change has an invalid value")

    errors.extend(validate_git_identity(profile.get("git_identity"), require_human=False))

    errors.extend(validate_registry(registry))
    machine_policy = profile.get("machine_policy")
    if not isinstance(machine_policy, dict):
        errors.append("machine_policy must be an object")
    else:
        for key in ("synchronize_registry", "require_production_capable"):
            if not isinstance(machine_policy.get(key), bool):
                errors.append(f"machine_policy.{key} must be a boolean")
        if machine_policy.get("require_production_capable") and not any(
            machine.get("production_capable") is True for machine in registry.get("machines", [])
        ):
            errors.append("machine policy requires at least one production-capable machine")
    return errors


def validate_identity(value: Any, field: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{field} must be an object"]
    errors: list[str] = []
    name = value.get("name")
    email = value.get("email")
    if not isinstance(name, str) or not name.strip() or any(char in name for char in "\r\n<>"):
        errors.append(f"{field}.name is invalid")
    if (
        not isinstance(email, str)
        or "@" not in email
        or email.startswith("@")
        or email.endswith("@")
        or any(char in email for char in "\r\n<> ")
    ):
        errors.append(f"{field}.email is invalid")
    return errors


def validate_git_identity(
    value: Any,
    *,
    require_human: bool,
    active_harnesses: list[str] | None = None,
) -> list[str]:
    if not isinstance(value, dict):
        return ["git_identity must be an object"]
    errors: list[str] = []
    mode = value.get("mode")
    if mode not in GIT_IDENTITY_MODES:
        errors.append(f"git_identity.mode has an invalid value: {mode!r}")
    trailer_key = value.get("trailer_key")
    if not isinstance(trailer_key, str) or not TRAILER_KEY_PATTERN.fullmatch(trailer_key):
        errors.append("git_identity.trailer_key is invalid")
    if not isinstance(value.get("verify_before_push"), bool):
        errors.append("git_identity.verify_before_push must be a boolean")
    if require_human and mode != "disabled":
        errors.extend(validate_identity(value.get("human"), "git_identity.human"))
    if not require_human and value.get("human_identity_source") != "machine":
        errors.append("git_identity.human_identity_source must be machine")

    agents = value.get("agents")
    if not isinstance(agents, dict) or not agents:
        errors.append("git_identity.agents must contain at least one agent product")
        return errors
    for harness, identity in agents.items():
        if not isinstance(harness, str) or not HANDLE_PATTERN.fullmatch(harness):
            errors.append("git_identity.agents keys must use lowercase kebab-case")
            continue
        errors.extend(validate_identity(identity, f"git_identity.agents.{harness}"))
    if active_harnesses and mode != "disabled":
        missing = sorted(set(active_harnesses) - set(agents))
        if missing:
            errors.append(f"git_identity.agents is missing active harnesses: {', '.join(missing)}")
    return errors


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("schema_version") != 1:
        errors.append("machine registry schema_version must be 1")
    machines = registry.get("machines")
    if not isinstance(machines, list) or not machines:
        return errors + ["machine registry must contain at least one machine"]

    aliases: list[str] = []
    for index, machine in enumerate(machines):
        prefix = f"machines[{index}]"
        if not isinstance(machine, dict):
            errors.append(f"{prefix} must be an object")
            continue
        alias = machine.get("alias")
        if not isinstance(alias, str) or not HANDLE_PATTERN.fullmatch(alias):
            errors.append(f"{prefix}.alias must use lowercase kebab-case")
        else:
            aliases.append(alias)
        if machine.get("default_delivery_mode") not in MACHINE_DELIVERY_MODES:
            errors.append(f"{prefix}.default_delivery_mode has an invalid value")
        if not isinstance(machine.get("production_capable"), bool):
            errors.append(f"{prefix}.production_capable must be a boolean")
        allowed = machine.get("allowed_delivery_modes")
        if not isinstance(allowed, list) or not allowed or not set(allowed) <= DELIVERY_MODES:
            errors.append(f"{prefix}.allowed_delivery_modes has an invalid value")
        elif len(allowed) != len(set(allowed)):
            errors.append(f"{prefix}.allowed_delivery_modes has duplicates")
        if not isinstance(machine.get("capabilities"), list) or not all(
            isinstance(item, str) and item for item in machine.get("capabilities", [])
        ):
            errors.append(f"{prefix}.capabilities must contain strings")
        if machine.get("setup_status") not in {"pending", "configured"}:
            errors.append(f"{prefix}.setup_status must be pending or configured")

    duplicates = sorted({alias for alias in aliases if aliases.count(alias) > 1})
    if duplicates:
        errors.append(f"machine registry has duplicate aliases: {', '.join(duplicates)}")
    return errors


def find_machine(registry: dict[str, Any], alias: str) -> dict[str, Any] | None:
    return next((item for item in registry.get("machines", []) if item.get("alias") == alias), None)
