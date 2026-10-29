#!/usr/bin/env python3
"""Install the shared profile, with an optional machine setup interview."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

try:
    from scripts import routing
    from scripts.preferences import inherited_values, validate_preferences, validate_pr_workflows
    from scripts.packages import resolve_selection, validate_package
except ModuleNotFoundError:
    import routing  # type: ignore[no-redef]
    from preferences import inherited_values, validate_preferences, validate_pr_workflows
    from packages import resolve_selection, validate_package

try:
    from scripts.profile import (
        AUTONOMY_PRESETS,
        COMMUNICATION_STYLES,
        DELIVERY_MODES,
        EXPLANATION_LEVELS,
        HANDLE_PATTERN,
        find_machine,
        load_operator,
        validate_git_identity,
        validate_identity,
    )
except ModuleNotFoundError:  # Direct execution from scripts/install.py.
    from profile import (  # type: ignore[no-redef]
        AUTONOMY_PRESETS,
        COMMUNICATION_STYLES,
        DELIVERY_MODES,
        EXPLANATION_LEVELS,
        HANDLE_PATTERN,
        find_machine,
        load_operator,
        validate_git_identity,
        validate_identity,
    )


REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPO_ROOT / "catalog.json"
DEFAULTS_PATH = REPO_ROOT / "config" / "defaults.json"
MANIFEST_SCHEMA = 3
STATE_FILES = (
    "install-manifest.json",
    "config.json",
    "preferences.json",
    "operator-profile.json",
    "machine-registry.json",
    "working-agreement.md",
)


@dataclass(frozen=True)
class Harness:
    name: str
    command: str
    markers: tuple[str, ...]
    destination: Callable[[Path], Path]


HARNESSES: dict[str, Harness] = {
    "codex": Harness("codex", "codex", (".codex",), lambda home: home / ".agents" / "skills"),
    "opencode": Harness("opencode", "opencode", (".config/opencode",), lambda home: home / ".agents" / "skills"),
    "cursor": Harness("cursor", "cursor", (".cursor",), lambda home: home / ".cursor" / "skills"),
    "claude": Harness("claude", "claude", (".claude",), lambda home: routing.claude_root(home) / "skills"),
    "hermes": Harness("hermes", "hermes", (".hermes",), lambda home: home / ".hermes" / "skills" / "astrobyte"),
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def detect_harnesses(home: Path) -> list[str]:
    found: list[str] = []
    for name, harness in HARNESSES.items():
        command_found = shutil.which(harness.command) is not None
        marker_found = any((home / marker).exists() for marker in harness.markers)
        if command_found or marker_found:
            found.append(name)
    return found


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or (default or "")


def ask_choice(prompt: str, choices: Iterable[str], default: str) -> str:
    allowed = list(choices)
    while True:
        value = ask(f"{prompt} ({'/'.join(allowed)})", default)
        if value in allowed:
            return value
        print(f"Choose one of: {', '.join(allowed)}")


def ask_bool(prompt: str, default: bool) -> bool:
    marker = "Y/n" if default else "y/N"
    while True:
        value = ask(f"{prompt} ({marker})").lower()
        if not value:
            return default
        if value in {"y", "yes", "true", "1"}:
            return True
        if value in {"n", "no", "false", "0"}:
            return False
        print("Answer yes or no.")


def ask_int(prompt: str, default: int, minimum: int, maximum: int) -> int:
    while True:
        raw = ask(prompt, str(default))
        try:
            value = int(raw)
        except ValueError:
            print(f"Enter a whole number from {minimum} to {maximum}.")
            continue
        if minimum <= value <= maximum:
            return value
        print(f"Enter a whole number from {minimum} to {maximum}.")


def ask_harnesses(detected: list[str]) -> list[str]:
    default = ",".join(detected) if detected else "codex"
    while True:
        raw = ask("Active harnesses, comma-separated", default)
        selected = [item.strip().lower() for item in raw.split(",") if item.strip()]
        unknown = [item for item in selected if item not in HARNESSES]
        if selected and not unknown:
            return list(dict.fromkeys(selected))
        if unknown:
            print(f"Unknown harnesses: {', '.join(unknown)}")
        else:
            print("Select at least one harness.")


def ask_optional_skills(names: list[str], previous: list[str]) -> list[str]:
    if not names:
        return []
    while True:
        raw = ask(f"Optional skills ({', '.join(names)}; comma-separated, '-' to clear)", ",".join(previous))
        if raw == "-":
            return []
        selected = [item.strip() for item in raw.split(",") if item.strip()]
        if len(selected) == len(set(selected)) and set(selected) <= set(names):
            return selected
        print("Select distinct names from the listed optional skills.")


def ask_machine_alias(registry: dict[str, Any], default: str) -> str:
    known = [item["alias"] for item in registry.get("machines", [])]
    while True:
        prompt = "Machine alias"
        if known:
            prompt += f" ({', '.join(known)}, or a new lowercase alias)"
        value = ask(prompt, default)
        if HANDLE_PATTERN.fullmatch(value):
            return value
        print("Use lowercase kebab-case, for example primary-dev.")


def git_global_value(key: str) -> str:
    result = subprocess.run(
        ["git", "config", "--global", "--get", key],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def ask_git_identity(
    operator_profile: dict[str, Any],
    prior_config: dict[str, Any],
    harnesses: list[str],
) -> dict[str, Any]:
    template = operator_profile.get("git_identity", {})
    prior = prior_config.get("git_identity", {})
    mode_default = prior.get("mode", template.get("mode", "dual-attribution"))
    mode = ask_choice(
        "Git attribution for agent-created commits",
        ("dual-attribution", "agent-only", "human-with-agent-trailer", "disabled"),
        str(mode_default),
    )
    agents = template.get("agents", {})
    trailer_key = str(template.get("trailer_key", "Agent"))
    verify_before_push = bool(template.get("verify_before_push", True))
    if mode == "disabled":
        return {
            "mode": mode,
            "trailer_key": trailer_key,
            "verify_before_push": verify_before_push,
            "agents": agents,
        }

    prior_human = prior.get("human", {}) if isinstance(prior, dict) else {}
    human_name_default = str(
        prior_human.get("name")
        or git_global_value("user.name")
        or operator_profile.get("display_name")
        or operator_profile.get("handle")
        or ""
    )
    human_email_default = str(prior_human.get("email") or git_global_value("user.email") or "")
    while True:
        human = {
            "name": ask("Human Git author name", human_name_default or None),
            "email": ask("Human Git author email", human_email_default or None),
        }
        errors = validate_identity(human, "git_identity.human")
        if not errors:
            break
        for error in errors:
            print(error)

    selected_agents: dict[str, Any] = {}
    prior_agents = prior.get("agents", {}) if isinstance(prior, dict) else {}
    for harness in harnesses:
        default_identity = prior_agents.get(harness) or agents.get(harness) or {
            "name": HARNESSES[harness].name,
            "email": f"{harness}@local.invalid",
        }
        while True:
            identity = {
                "name": ask(f"Agent Git committer name for {harness}", str(default_identity.get("name", harness))),
                "email": ask(
                    f"Agent Git committer email for {harness}",
                    str(default_identity.get("email", f"{harness}@local.invalid")),
                ),
            }
            errors = validate_identity(identity, f"git_identity.agents.{harness}")
            if not errors:
                selected_agents[harness] = identity
                break
            for error in errors:
                print(error)

    return {
        "mode": mode,
        "human": human,
        "trailer_key": trailer_key,
        "verify_before_push": verify_before_push,
        "agents": selected_agents,
    }


def interactive_answers(
    home: Path,
    operator_profile: dict[str, Any] | None = None,
    machine_registry: dict[str, Any] | None = None,
    preferences: dict[str, Any] | None = None,
) -> dict[str, Any]:
    defaults = load_json(DEFAULTS_PATH)
    profile_defaults = operator_profile.get("defaults", {}) if operator_profile else {}
    overrides = validate_preferences(preferences)["overrides"] if preferences is not None else {}
    defaults.update(overrides.get("defaults", {}))
    profile_defaults = {**profile_defaults, **overrides.get("defaults", {})}
    registry = machine_registry or {"machines": []}
    detected = detect_harnesses(home)
    print("Astrobyte setup interview")
    if operator_profile:
        print(f"Operator profile: {operator_profile['handle']}")
    print(f"Detected harnesses: {', '.join(detected) if detected else 'none'}")
    harnesses = ask_harnesses(detected)
    preferred_default = defaults["primary_harness"] if defaults["primary_harness"] in harnesses else harnesses[0]
    primary = ask_choice("Preferred harness", harnesses, preferred_default)
    profile = ask_choice(
        "Skill profile",
        ("core", "builder", "full"),
        overrides.get("skill_profile", str(operator_profile.get("skill_profile", defaults["profile"])) if operator_profile else defaults["profile"]),
    )
    model_environment = ask_choice("Model environment", ("frontier", "local", "mixed"), defaults["model_environment"])
    max_parallel = ask_int("Maximum parallel workers", defaults["max_parallel_workers"], 1, 32)
    unattended_runs = ask_bool("Allow bounded unattended or overnight runs", defaults["unattended_runs"])
    external_actions = ask_choice(
        "Interactive external actions",
        ("ask", "reversible-only", "allow-configured"),
        defaults["external_actions"],
    )
    unattended_external_actions = "ask"
    if unattended_runs:
        unattended_external_actions = ask_choice(
            "External actions during unattended runs",
            ("ask", "reversible-only", "allow-configured"),
            defaults["unattended_external_actions"],
        )

    prior_config_path = config_dir(home) / "config.json"
    prior_config = load_json(prior_config_path) if prior_config_path.exists() else {}
    optional_names = sorted(name for name, info in load_json(CATALOG_PATH)["skills"].items() if info.get("tier") == "optional")
    optional_default = overrides.get("optional_skills", prior_config.get("optional_skills", defaults.get("optional_skills", [])))
    if not isinstance(optional_default, list) or not all(isinstance(name, str) for name in optional_default):
        raise ValueError("Existing optional_skills must be a list of names")
    optional_skills = ask_optional_skills(optional_names, optional_default)
    identity_profile = dict(operator_profile or {})
    identity_profile["git_identity"] = {**identity_profile.get("git_identity", {}), **overrides.get("git_identity", {})}
    git_identity = ask_git_identity(identity_profile, prior_config, harnesses)
    known_aliases = [item["alias"] for item in registry.get("machines", [])]
    alias_default = prior_config.get("machine_alias")
    if not isinstance(alias_default, str) or not HANDLE_PATTERN.fullmatch(alias_default):
        configured = [item["alias"] for item in registry.get("machines", []) if item.get("setup_status") == "configured"]
        alias_default = configured[0] if configured else (known_aliases[0] if known_aliases else "primary-dev")
    machine_alias = ask_machine_alias(registry, alias_default)
    machine = find_machine(registry, machine_alias)
    personal_delivery = str(profile_defaults.get("delivery_mode", defaults.get("delivery_mode", "durable")))
    delivery_default = str(machine.get("default_delivery_mode", personal_delivery)) if machine else personal_delivery
    delivery_policy = profile_defaults.get("machine_delivery_policy", "inherit-personal-default")
    if delivery_policy == "ask-every-project":
        delivery_mode = "ask"
    elif delivery_policy == "ask-every-install" or delivery_default == "ask":
        delivery_mode = ask_choice(
            "Default delivery mode for this machine",
            ("explore", "prototype", "durable", "production", "ask"),
            delivery_default,
        )
    else:
        delivery_mode = delivery_default

    production_capable = bool(machine.get("production_capable")) if machine else ask_bool(
        "Can this machine be used for production-standard work", False
    )
    autonomy_default = str(profile_defaults.get("autonomy_preset", "guided-implementation"))
    autonomy_preset = ask_choice("Machine autonomy preset", sorted(AUTONOMY_PRESETS), autonomy_default)

    return {
        "operator_handle": operator_profile.get("handle") if operator_profile else None,
        "machine_alias": machine_alias,
        "delivery_mode": delivery_mode,
        "production_capable": production_capable,
        "autonomy_preset": autonomy_preset,
        "communication_style": profile_defaults.get("communication_style", "collaborative-challenge"),
        "explanation_level": profile_defaults.get("explanation_level", "collaborative"),
        "git_identity": git_identity,
        "harnesses": harnesses,
        "primary_harness": primary,
        "profile": profile,
        "optional_skills": optional_skills,
        "model_environment": model_environment,
        "max_parallel_workers": max_parallel,
        "unattended_runs": unattended_runs,
        "external_actions": external_actions,
        "unattended_external_actions": unattended_external_actions,
        "git_workflow": ask_choice(
            "Preferred Git isolation",
            ("branch", "worktree", "current-tree"),
            str(profile_defaults.get("git_workflow", defaults["git_workflow"])),
        ),
        "issue_tracker": ask_choice(
            "Issue tracker",
            ("local", "github", "linear", "none"),
            str(profile_defaults.get("issue_tracker", defaults["issue_tracker"])),
        ),
        "docs_path": ask("Default project documentation path", defaults["docs_path"]),
        "compute": ask_choice("Compute environment", ("apple-silicon", "nvidia", "cpu", "cloud", "mixed"), defaults["compute"]),
        "experiment_budget": ask("Default experiment budget rule", defaults["experiment_budget"]),
        "browser_automation": ask_bool("Is browser automation available", defaults["browser_automation"]),
        "containers": ask_bool("Are Docker or compatible containers available", defaults["containers"]),
        "archive_duplicates": ask_bool("Archive duplicate catalog skills from legacy harness directories", defaults["archive_duplicates"]),
        "archive_superseded": ask_bool("Archive known superseded workflow skills", defaults["archive_superseded"]),
    }


def validate_optional_skills(names: Any, catalog: dict[str, Any]) -> list[str]:
    if not isinstance(names, list) or not all(isinstance(item, str) for item in names):
        raise ValueError("optional_skills must be a list of skill names")
    if len(names) != len(set(names)):
        raise ValueError("optional_skills must not contain duplicates")
    allowed = {name for name, info in catalog["skills"].items() if info.get("tier") == "optional"}
    unknown = sorted(set(names) - allowed)
    if unknown:
        raise ValueError(f"Unknown optional_skills: {', '.join(unknown)}")
    return names


def validate_answers(answers: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    required = {
        "harnesses",
        "primary_harness",
        "profile",
        "model_environment",
        "max_parallel_workers",
        "unattended_runs",
        "external_actions",
        "unattended_external_actions",
        "git_workflow",
        "issue_tracker",
        "docs_path",
        "compute",
        "experiment_budget",
        "browser_automation",
        "containers",
        "archive_duplicates",
        "archive_superseded",
    }
    missing = sorted(required - answers.keys())
    if missing:
        raise ValueError(f"Missing setup answers: {', '.join(missing)}")
    harnesses = answers["harnesses"]
    if not isinstance(harnesses, list) or not harnesses:
        raise ValueError("harnesses must be a non-empty list")
    if not all(isinstance(item, str) for item in harnesses):
        raise ValueError("harnesses must contain only strings")
    unknown = sorted(set(harnesses) - HARNESSES.keys())
    if unknown:
        raise ValueError(f"Unknown harnesses: {', '.join(unknown)}")
    if len(harnesses) != len(set(harnesses)):
        raise ValueError("harnesses must not contain duplicates")
    if answers["primary_harness"] not in harnesses:
        raise ValueError("primary_harness must be one of the selected harnesses")
    if answers["profile"] not in catalog["profiles"]:
        raise ValueError(f"Unknown profile: {answers['profile']}")
    answers["optional_skills"] = validate_optional_skills(answers.get("optional_skills", []), catalog)
    if "pr_workflows" in answers:
        validate_pr_workflows(answers["pr_workflows"])
    workers = answers["max_parallel_workers"]
    if isinstance(workers, bool) or not isinstance(workers, int) or not 1 <= workers <= 32:
        raise ValueError("max_parallel_workers must be an integer from 1 to 32")

    choices = {
        "model_environment": {"frontier", "local", "mixed"},
        "external_actions": {"ask", "reversible-only", "allow-configured"},
        "unattended_external_actions": {"ask", "reversible-only", "allow-configured"},
        "git_workflow": {"branch", "worktree", "current-tree"},
        "issue_tracker": {"local", "github", "linear", "none"},
        "compute": {"apple-silicon", "nvidia", "cpu", "cloud", "mixed"},
    }
    for key, allowed in choices.items():
        if answers[key] not in allowed:
            raise ValueError(f"Invalid {key}: {answers[key]!r}")
    for key in ("unattended_runs", "browser_automation", "containers", "archive_duplicates", "archive_superseded"):
        if not isinstance(answers[key], bool):
            raise ValueError(f"{key} must be a boolean")
    if "portable_preferences" in answers and type(answers["portable_preferences"]) is not bool:
        raise ValueError("portable_preferences must be a boolean")
    for key in ("docs_path", "experiment_budget"):
        if not isinstance(answers[key], str) or not answers[key].strip():
            raise ValueError(f"{key} must be a non-empty string")
    optional_choices = {
        "delivery_mode": DELIVERY_MODES | {"ask"},
        "autonomy_preset": AUTONOMY_PRESETS,
        "communication_style": COMMUNICATION_STYLES,
        "explanation_level": EXPLANATION_LEVELS,
    }
    for key, allowed in optional_choices.items():
        if key in answers and answers[key] not in allowed:
            raise ValueError(f"Invalid {key}: {answers[key]!r}")
    for key in ("operator_handle", "machine_alias"):
        if key in answers and answers[key] is not None:
            if not isinstance(answers[key], str) or not HANDLE_PATTERN.fullmatch(answers[key]):
                raise ValueError(f"{key} must use lowercase kebab-case")
    if "production_capable" in answers and not isinstance(answers["production_capable"], bool):
        raise ValueError("production_capable must be a boolean")
    if "git_identity" in answers:
        git_identity_errors = validate_git_identity(
            answers["git_identity"],
            require_human=answers["git_identity"].get("human_identity_source") != "machine",
            active_harnesses=harnesses,
        )
        if git_identity_errors:
            raise ValueError("Invalid Git identity: " + "; ".join(git_identity_errors))
    return answers


def quick_answers(home: Path, operator_profile: dict[str, Any], harnesses: list[str], preferences: dict[str, Any] | None = None) -> dict[str, Any]:
    """Inherit the shared baseline while retaining explicit local preferences."""
    defaults = load_json(DEFAULTS_PATH)
    prior_path = config_dir(home) / "config.json"
    prior = load_json(prior_path) if prior_path.exists() else {}
    inherited = inherited_values(prior)
    prior = {key: value for key, value in prior.items() if key not in inherited or inherited[key] != value}
    delta = validate_preferences(preferences) if preferences is not None else None
    selected_defaults = delta["overrides"].get("defaults", {}) if delta else {}
    base_identity = dict(operator_profile["git_identity"])
    if delta:
        base_identity.update(delta["overrides"].get("git_identity", {}))
    baseline_values = {
        **defaults,
        **{key: value for key, value in operator_profile["defaults"].items() if key != "machine_delivery_policy"},
        "profile": delta["overrides"].get("skill_profile", operator_profile["skill_profile"]) if delta else operator_profile["skill_profile"],
        "git_identity": base_identity,
        **selected_defaults,
    }
    answers = {
        **baseline_values,
        "operator_handle": operator_profile["handle"],
        "machine_alias": None,
        **prior,
        "harnesses": list(dict.fromkeys([*prior.get("harnesses", []), *harnesses])),
        "archive_duplicates": False,
        "archive_superseded": False,
    }
    if delta and "optional_skills" in delta["overrides"]:
        answers["optional_skills"] = list(delta["overrides"]["optional_skills"])
        answers["_removed_optional_skills"] = sorted(set(prior.get("optional_skills", [])) - set(answers["optional_skills"]))
    if answers["primary_harness"] not in answers["harnesses"]:
        answers["primary_harness"] = harnesses[0]
    identity = dict(answers.get("git_identity", operator_profile["git_identity"]))
    if identity.get("mode") != "disabled":
        identity["agents"] = {**operator_profile["git_identity"]["agents"], **identity.get("agents", {})}
    answers["git_identity"] = identity
    policy_keys = set(operator_profile["defaults"]) - {"machine_delivery_policy"}
    policy_keys |= {"profile", "git_identity", "max_parallel_workers", "unattended_runs", "external_actions", "unattended_external_actions", "experiment_budget"}
    answers["_baseline_values"] = {key: baseline_values[key] for key in policy_keys if key in baseline_values and answers.get(key) == baseline_values[key]}
    answers["_preferences"] = delta
    answers["portable_preferences"] = prior.get("portable_preferences", False)
    if answers["operator_handle"] != operator_profile["handle"] and not all(
        (config_dir(home) / name).is_file() for name in ("operator-profile.json", "working-agreement.md")
    ):
        raise ValueError("Existing personal profile files are missing; use that profile's source checkout")
    return answers


def resolve_install_answers(
    home: Path,
    operator_profile: dict[str, Any],
    harnesses: list[str],
    preferences: dict[str, Any] | None,
    machine_answers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Combine a reviewed personal delta and explicit machine choices once."""
    answers = quick_answers(home, operator_profile, harnesses, preferences)
    if machine_answers is not None:
        previous_optional = set(answers.get("optional_skills", []))
        answers.update(machine_answers)
        if "profile" in machine_answers and "selected_skills" not in machine_answers:
            answers.pop("selected_skills", None)
        for key in machine_answers:
            answers.get("_baseline_values", {}).pop(key, None)
        answers["_removed_optional_skills"] = sorted(previous_optional - set(answers.get("optional_skills", [])))
    return answers


def tree_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if not item.is_file() or item.name in {".DS_Store"} or "__pycache__" in item.parts:
            continue
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def package_hash(path: Path, preferences_json: str | None) -> str:
    if preferences_json is None:
        return tree_hash(path)
    files = {item.relative_to(path).as_posix(): item.read_bytes() for item in path.rglob("*")
             if item.is_file() and item.name != ".DS_Store" and "__pycache__" not in item.parts}
    files["references/preferences.json"] = preferences_json.encode()
    digest = hashlib.sha256()
    for name, content in sorted(files.items()):
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return digest.hexdigest()


def config_dir(home: Path) -> Path:
    override = os.environ.get("ASTROBYTE_CONFIG_HOME")
    path = Path(override).expanduser() if override else home / ".config" / "astrobyte-agent-skills"
    resolved = path.resolve()
    if resolved == Path(resolved.anchor):
        raise ValueError("The Astrobyte configuration directory cannot be a filesystem root")
    return resolved


def destination_groups(harnesses: list[str], home: Path) -> dict[Path, list[str]]:
    groups: dict[Path, list[str]] = {}
    for name in harnesses:
        destination = HARNESSES[name].destination(home)
        groups.setdefault(destination, []).append(name)
    return groups


def legacy_roots(harnesses: list[str], home: Path) -> list[Path]:
    roots: list[Path] = []
    if "codex" in harnesses or "opencode" in harnesses:
        roots.append(home / ".agents" / "skills")
    if "codex" in harnesses:
        roots.append(home / ".codex" / "skills")
    if "opencode" in harnesses:
        roots.append(home / ".config" / "opencode" / "skills")
    if "cursor" in harnesses:
        roots.append(home / ".cursor" / "skills")
    if "claude" in harnesses:
        roots.append(routing.claude_root(home) / "skills")
    return list(dict.fromkeys(roots))


def manifest_path(home: Path) -> Path:
    return config_dir(home) / "install-manifest.json"


def read_manifest(home: Path) -> dict[str, Any]:
    path = manifest_path(home)
    return load_json(path) if path.exists() else {"targets": {}}


def git_output(*args: str) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=False, text=True, capture_output=True)
    except OSError:
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def canonical_source_url() -> str:
    repository = load_json(REPO_ROOT / "config" / "repository.json")["upstream"]["repository"]
    return f"https://github.com/{repository}.git"


def source_provenance() -> dict[str, Any]:
    url = git_output("remote", "get-url", "origin")
    return {
        "path": str(REPO_ROOT),
        "url": re.sub(r"^(https?://)[^/@]+@", r"\1", url) if url else None,
        "version": (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "commit": git_output("rev-parse", "HEAD"),
    }


def source_recovery(manifest: dict[str, Any]) -> list[str]:
    """Explain how to restore a missing recorded checkout without cloning anything."""
    source = manifest.get("source") or {}
    recorded = source.get("path")
    if not recorded or Path(recorded).exists():
        return []
    lines = [
        f"recorded source checkout is missing: {recorded}",
        f"  This check compared against {REPO_ROOT}. To restore the recorded source, choose a destination and run:",
        f"    git clone {source.get('url') or canonical_source_url()} <destination>",
    ]
    if source.get("commit"):
        lines.append(f"    git -C <destination> checkout {source['commit']}")
    lines.append("    python3 <destination>/scripts/install.py --check")
    return lines


def new_backup_root(home: Path) -> Path:
    return config_dir(home) / "backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def build_plan(answers: dict[str, Any], home: Path, catalog: dict[str, Any], *, prune: bool = True) -> list[dict[str, Any]]:
    requested = answers.get("selected_skills", catalog["profiles"][answers["profile"]])
    if not isinstance(requested, list) or not requested or any(not isinstance(name, str) for name in requested):
        raise ValueError("selected_skills must be a nonempty list of catalog names")
    selected = resolve_selection(catalog, [*requested, *answers.get("optional_skills", [])])
    prior_targets = read_manifest(home).get("targets", {})
    plan: list[dict[str, Any]] = []
    for destination, harnesses in destination_groups(answers["harnesses"], home).items():
        for skill in selected:
            source = REPO_ROOT / "skills" / skill
            if not source.is_dir():
                raise FileNotFoundError(f"Cataloged skill is missing: {source}")
            errors = validate_package(source, catalog["skills"][skill])
            if errors:
                raise ValueError("Invalid skill package: " + "; ".join(errors))
            target = destination / skill
            preferences_json = None
            accepts_preferences = skill in {"astrobyte-mode", "astrobyte-review", "astrobyte-git-identity"} or catalog["skills"][skill].get("portable_preferences") is True
            if answers.get("portable_preferences") and answers.get("_preferences") and accepts_preferences:
                preferences_json = json.dumps(answers["_preferences"], indent=2, sort_keys=True) + "\n"
            source_hash = package_hash(source, preferences_json)
            prior = prior_targets.get(str(target), {})
            if not target.exists():
                status = "new"
            else:
                target_hash = tree_hash(target)
                if target_hash == source_hash:
                    status = "same"
                elif prior.get("hash") == target_hash:
                    status = "update"
                else:
                    status = "conflict"
            plan.append(
                {
                    "skill": skill,
                    "source": str(source),
                    "target": str(target),
                    "hash": source_hash,
                    "source_hash": tree_hash(source),
                    "status": status,
                    "harnesses": harnesses,
                    "preferences_json": preferences_json,
                }
            )

    planned_targets = {Path(item["target"]) for item in plan}
    current_destinations = set(destination_groups(answers["harnesses"], home))
    for raw_target, metadata in prior_targets.items():
        removed_optional = metadata.get("skill") in answers.get("_removed_optional_skills", []) and catalog.get("skills", {}).get(metadata.get("skill"), {}).get("tier") == "optional"
        if not prune and not removed_optional:
            continue
        target = Path(raw_target)
        if target in planned_targets or target.parent not in current_destinations or not target.exists():
            continue
        skill = metadata.get("skill")
        if skill not in catalog.get("skills", {}):
            continue
        plan.append(
            {
                "skill": skill,
                "source": None,
                "target": str(target),
                "hash": None,
                "status": "archive-optional" if removed_optional else "archive-profile",
                "harnesses": [],
            }
        )
    if answers["archive_duplicates"]:
        for root in legacy_roots(answers["harnesses"], home):
            for skill in selected:
                target = root / skill
                if target in planned_targets or not target.exists():
                    continue
                plan.append(
                    {
                        "skill": skill,
                        "source": None,
                        "target": str(target),
                        "hash": None,
                        "status": "archive-duplicate",
                        "harnesses": [],
                    }
                )
    if answers["archive_superseded"]:
        roots = legacy_roots(answers["harnesses"], home) + list(destination_groups(answers["harnesses"], home))
        for root in dict.fromkeys(roots):
            for skill in catalog.get("superseded_skills", []):
                target = root / skill
                if target.exists():
                    plan.append(
                        {
                            "skill": skill,
                            "source": None,
                            "target": str(target),
                            "hash": None,
                            "status": "archive-superseded",
                            "harnesses": [],
                        }
                    )
    return plan


def print_plan(answers: dict[str, Any], plan: list[dict[str, Any]], home: Path) -> None:
    print("\nInstallation plan")
    if answers.get("operator_handle"):
        print(f"  Operator: {answers['operator_handle']}")
    if answers.get("machine_alias"):
        print(f"  Machine: {answers['machine_alias']}")
    if answers.get("delivery_mode"):
        print(f"  Delivery default: {answers['delivery_mode']}")
    git_identity = answers.get("git_identity")
    if isinstance(git_identity, dict):
        print(f"  Git attribution: {git_identity.get('mode')}")
        human = git_identity.get("human")
        if isinstance(human, dict):
            print(f"  Human Git author: {human.get('name')} <{human.get('email')}>")
        for harness, identity in git_identity.get("agents", {}).items():
            print(f"  {harness} Git committer: {identity.get('name')} <{identity.get('email')}>")
    print(f"  Profile: {answers['profile']}")
    if answers.get("selected_skills"):
        print(f"  Requested skills: {', '.join(answers['selected_skills'])}")
        expanded = sorted({item['skill'] for item in plan if not item['status'].startswith('archive-')})
        print(f"  With hard dependencies: {', '.join(expanded)}")
    if answers.get("_preferences"):
        print("  Personalization: reviewed differences from the Astrobyte baseline")
        print(f"  Portable preferences: {bool(answers.get('portable_preferences'))}")
        options = answers["_preferences"]["overrides"].get("pr_workflows")
        if options:
            print(f"  Personal PR workflows: {json.dumps(options, sort_keys=True)}")
    print(f"  Optional skills: {', '.join(answers.get('optional_skills', [])) or 'none'}")
    print(f"  Primary harness: {answers['primary_harness']}")
    print(f"  Active harnesses: {', '.join(answers['harnesses'])}")
    print(f"  Machine config: {config_dir(home) / 'config.json'}")
    for destination, harnesses in destination_groups(answers["harnesses"], home).items():
        print(f"  Destination: {destination} ({', '.join(harnesses)})")
    statuses = ("new", "update", "conflict", "same", "archive-profile", "archive-duplicate", "archive-superseded")
    if any(item["status"] == "archive-optional" for item in plan):
        statuses += ("archive-optional",)
    counts = {status: sum(item["status"] == status for item in plan) for status in statuses}
    print("  Changes: " + ", ".join(f"{key}={value}" for key, value in counts.items()))
    archived = [item["target"] for item in plan if item["status"] == "conflict" or item["status"].startswith("archive-")]
    if archived:
        print("  Existing skill directories will be backed up:")
        for target in archived:
            print(f"    {target}")


def atomic_json_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def atomic_text_write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(value)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def apply_plan(
    answers: dict[str, Any],
    plan: list[dict[str, Any]],
    home: Path,
    *,
    preserve_existing: bool = False,
    routing_items: list[dict[str, Any]] | None = None,
    routing_state: dict[str, Any] | None = None,
) -> list[str]:
    state_dir = config_dir(home)
    backup_root = new_backup_root(home)
    backups: list[str] = []
    prior_manifest = read_manifest(home)
    prior_targets = prior_manifest.get("targets", {})
    targets: dict[str, Any] = dict(prior_targets) if preserve_existing else {}

    for item in plan:
        target = Path(item["target"])
        if item["status"].startswith("archive-"):
            targets.pop(str(target), None)
            if target.exists():
                relative = Path(*target.parts[1:]) if target.is_absolute() else target
                backup = backup_root / relative
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), str(backup))
                backups.append(str(backup))
            continue
        source = Path(item["source"])
        if item["status"] != "same":
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                relative = Path(*target.parts[1:]) if target.is_absolute() else target
                backup = backup_root / relative
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), str(backup))
                backups.append(str(backup))
            shutil.copytree(source, target)
            if item.get("preferences_json") is not None:
                (target / "references").mkdir(exist_ok=True)
                atomic_text_write(target / "references/preferences.json", item["preferences_json"])
        owners = list(item["harnesses"])
        if preserve_existing:
            owners = list(dict.fromkeys([*prior_targets.get(str(target), {}).get("harnesses", []), *owners]))
        targets[str(target)] = {
            "skill": item["skill"],
            "hash": item["hash"],
            "source_hash": item["source_hash"],
            "harnesses": owners,
        }

    machine_config = {key: value for key, value in answers.items() if not key.startswith("_")}
    if "_baseline_values" in answers:
        machine_config["baseline_inheritance"] = {"schema_version": 1, "values": answers["_baseline_values"]}
    machine_config.update(
        {
            "schema_version": 2,
            "repository_version": load_json(CATALOG_PATH)["repository_version"],
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "host": socket.gethostname(),
            "os": platform.system().lower(),
        }
    )
    atomic_json_write(state_dir / "config.json", machine_config)
    if answers.get("_preferences") is not None:
        preference_path = state_dir / "preferences.json"
        if preference_path.exists() and load_json(preference_path) != answers["_preferences"]:
            backup = backup_root / "preferences.json"
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(preference_path, backup)
            backups.append(str(backup))
        atomic_json_write(preference_path, answers["_preferences"])
    operator_handle = answers.get("operator_handle")
    if operator_handle:
        profile_path = state_dir / "operator-profile.json"
        agreement_target = state_dir / "working-agreement.md"
        if not preserve_existing or (operator_handle != "astrobyte" and not (profile_path.exists() and agreement_target.exists())):
            operator_profile, registry, operator_dir = load_operator(REPO_ROOT, str(operator_handle))
            if not preserve_existing or not profile_path.exists():
                atomic_json_write(profile_path, operator_profile)
            if not preserve_existing:
                atomic_json_write(state_dir / "machine-registry.json", registry)
            if not preserve_existing or not agreement_target.exists():
                agreement_path = operator_dir / str(operator_profile["working_agreement"])
                atomic_text_write(agreement_target, agreement_path.read_text(encoding="utf-8"))

    routing_records = dict(prior_manifest.get("routing", {}))
    if routing_items:
        written, routing_backups = routing.apply_install(routing_items, backup_root)
        routing_records.update(written)
        backups.extend(routing_backups)
    state = {key: prior_manifest[key] for key in ("routing_mode", "routing_declined", "workspace_roots") if key in prior_manifest}
    state.update(routing_state or {})
    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "repository": str(REPO_ROOT),
        "repository_version": machine_config["repository_version"],
        "source": source_provenance(),
        "profile": answers["profile"],
        "operator_handle": operator_handle,
        "targets": targets,
        "routing": routing_records,
        **{key: value for key, value in state.items() if value is not None},
    }
    atomic_json_write(manifest_path(home), manifest)
    return backups


def check_install(home: Path) -> int:
    path = manifest_path(home)
    if not path.exists():
        print(f"No install manifest at {path}")
        return 1
    manifest = load_json(path)
    errors: list[str] = []
    notes: list[str] = []
    targets = manifest.get("targets", {})
    for raw_target, metadata in targets.items():
        target = Path(raw_target)
        if not target.exists():
            errors.append(f"missing: {target}")
        elif tree_hash(target) != metadata.get("hash"):
            errors.append(f"drifted: {target}")
    if manifest.get("schema_version", 0) < MANIFEST_SCHEMA:
        errors.append("source provenance unknown; reinstall to migrate")
    else:
        source_hashes: dict[str, str | None] = {}
        differing: set[str] = set()
        unknown: set[str] = set()
        for metadata in targets.values():
            skill = str(metadata.get("skill"))
            if "source_hash" not in metadata:
                unknown.add(skill)
                continue
            if skill not in source_hashes:
                source = REPO_ROOT / "skills" / skill
                source_hashes[skill] = tree_hash(source) if source.is_dir() else None
            if source_hashes[skill] is None:
                differing.add(f"{skill} (absent from this checkout)")
            elif source_hashes[skill] != metadata.get("source_hash"):
                differing.add(skill)
        if differing:
            errors.append("differs from this checkout: " + ", ".join(sorted(differing)))
        if unknown:
            notes.append("source provenance unknown for skills kept from an earlier install: " + ", ".join(sorted(unknown)) + "; reinstall them to record it")
        notes.extend(source_recovery(manifest))
        owners = {owner for metadata in targets.values() for owner in metadata.get("harnesses", [])}
        for name in sorted(owners & HARNESSES.keys()):
            destination = HARNESSES[name].destination(home)
            if not any(Path(raw).parent.resolve() == destination.resolve() for raw, metadata in targets.items() if name in metadata.get("harnesses", [])):
                errors.append(f"skills not at the active {name} location: {destination}; reinstall to move them")
    routing_errors, routing_notes = routing.check(home, manifest.get("routing", {}), manifest.get("workspace_roots", []))
    errors.extend(routing_errors)
    notes.extend(routing_notes)
    mode = manifest.get("routing_mode")
    if mode == "migration-required":
        notes.append("routing decision pending: rerun the installer with --routing to add it, or with --skills-only to decline it")
    for note in notes:
        print(note if note.startswith(" ") else f"Note: {note}")
    if errors:
        print("Installation check failed:")
        for error in errors:
            print(f"  {error}")
        return 1
    print(f"Installation matches {path}")
    print(f"Routing: {mode or 'not installed'}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--quick", action="store_true", help="Install shared defaults without an interview (default)")
    modes.add_argument("--interview", action="store_true", help="Run the optional machine setup interview")
    parser.add_argument("--harnesses", help="Comma-separated agent products for quick installation")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--skills", help="Comma-separated skills; automatically include hard dependencies")
    selection.add_argument("--profile", choices=("core", "builder", "full"), help="Select a catalog profile instead of a saved subset")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan without writing")
    routing_choice = parser.add_mutually_exclusive_group()
    routing_choice.add_argument("--routing", action="store_true", help="Install or restore always-loaded routing and approve its migrations and conflicts")
    routing_choice.add_argument("--skills-only", action="store_true", help="Install or update skills without adding routing")
    parser.add_argument("--workspace-root", action="append", type=Path, default=[], help="Add a managed routing block to this directory's AGENTS.md (repeatable)")
    operations = parser.add_mutually_exclusive_group()
    operations.add_argument("--check", action="store_true", help="Check the recorded installation for drift, source differences, and inactive routing")
    operations.add_argument("--remove-routing", action="store_true", help="Remove routing for --harnesses, or for every harness; skills stay installed")
    operations.add_argument("--uninstall", action="store_true", help="Remove managed skills and routing for --harnesses or --all")
    operations.add_argument("--purge-state", action="store_true", help="Remove local Astrobyte state after a complete uninstall")
    operations.add_argument("--remove-workspace-root", action="append", type=Path, help="Remove the managed block from a recorded workspace root (repeatable)")
    parser.add_argument("--all", action="store_true", help="With --uninstall, remove every managed skill and routing target")
    parser.add_argument("--answers", type=Path, help="Use a reviewed JSON answer file instead of prompting")
    parser.add_argument("--operator", help="Use the named committed operator profile")
    parser.add_argument("--preferences", type=Path, help="Apply approved baseline override JSON locally")
    export_modes = parser.add_mutually_exclusive_group()
    export_modes.add_argument("--portable-preferences", action="store_true", help="Include approved reusable preferences in installed runtime skills for sync")
    export_modes.add_argument("--local-preferences", action="store_true", help="Keep preferences local and remove their managed portable copies")
    parser.add_argument("--yes", action="store_true", help="Apply the selected plan without a final prompt")
    parser.add_argument("--home", type=Path, default=Path.home(), help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def parse_harness_list(raw: str) -> list[str]:
    harnesses = list(dict.fromkeys(name.strip().lower() for name in raw.split(",") if name.strip()))
    unknown = sorted(set(harnesses) - HARNESSES.keys())
    if unknown:
        raise ValueError(f"Unknown harnesses: {', '.join(unknown)}")
    if not harnesses:
        raise ValueError("Select at least one harness")
    return harnesses


def routing_decision(args: argparse.Namespace, manifest: dict[str, Any], manifest_exists: bool, selected: set[str]) -> tuple[bool, str | None, str]:
    """Return whether to write routing, the mode to record, and the reason."""
    prior = manifest.get("routing_mode")
    if prior is None and manifest_exists and manifest.get("schema_version", 0) < MANIFEST_SCHEMA:
        prior = "migration-required"
    missing = sorted(routing.REQUIRED_SKILLS - selected)
    if args.skills_only:
        return False, prior if prior == "enabled" else "disabled", "skipped by --skills-only"
    if missing:
        return False, prior, f"skipped because the selection lacks {', '.join(missing)}"
    if args.routing:
        return True, "enabled", "enabled by --routing"
    if prior == "migration-required":
        return False, prior, "skipped because this installation predates routing; rerun with --routing to add it"
    if prior == "disabled":
        return False, prior, "skipped because routing is disabled; rerun with --routing to enable it"
    return True, "enabled", "enabled"


def print_routing_items(items: list[dict[str, Any]]) -> None:
    for item in items:
        print(f"    {item['status']}: {item['path']} ({item['harness']})")
        for note in item.get("notes", []):
            print(f"      {note}")
        if item.get("approval"):
            print(f"      needs approval: {item['approval']}")
        if item.get("diff"):
            print(textwrap.indent(item["diff"].rstrip("\n"), "      "))


def confirm_routing_approvals(args: argparse.Namespace, items: list[dict[str, Any]]) -> set[str]:
    """Ask for each approval interactively; --yes approves only with --routing."""
    pending = [item for item in items if item.get("approval")]
    if args.yes:
        return {item["path"] for item in pending} if getattr(args, "routing", False) else set()
    return {item["path"] for item in pending if ask_bool(f"Approve: {item['approval']}", False)}


def update_config_harnesses(home: Path, removed: set[str]) -> None:
    path = config_dir(home) / "config.json"
    if not path.exists():
        return
    config = load_json(path)
    remaining = [name for name in config.get("harnesses", []) if name not in removed]
    config["harnesses"] = remaining
    if config.get("primary_harness") in removed and remaining:
        config["primary_harness"] = remaining[0]
    atomic_json_write(path, config)


def finish_removal(manifest: dict[str, Any], removed: list[str]) -> dict[str, Any]:
    records = {path: record for path, record in manifest.get("routing", {}).items() if path not in removed}
    roots = [root for root in manifest.get("workspace_roots", []) if str(routing.workspace_location(Path(root)).path) in records]
    return {**manifest, "routing": records, "workspace_roots": roots}


def report_removal(removed: list[str], kept: list[str], backups: list[str], home: Path) -> int:
    print(f"Removed routing from {len(backups)} file(s); {len(removed)} routing location(s) no longer managed.")
    if backups:
        print(f"Backups: {config_dir(home) / 'backups'}")
    for path in kept:
        print(f"Kept edited routing at {path}; approve its removal interactively or edit it by hand.")
    return 1 if kept else 0


def remove_routing_command(args: argparse.Namespace, home: Path) -> int:
    manifest_exists = manifest_path(home).exists()
    manifest = read_manifest(home)
    records = manifest.get("routing", {})
    harnesses = parse_harness_list(args.harnesses) if args.harnesses else list(routing.ROUTING_HARNESSES)
    unsupported = [name for name in harnesses if name not in routing.ROUTING_HARNESSES]
    if unsupported:
        raise ValueError(f"No installer-managed routing exists for: {', '.join(unsupported)}")
    scope = {*harnesses} if args.harnesses else {*harnesses, "workspace"}
    locations = [routing.harness_location(name, home) for name in harnesses]
    locations += [routing.record_location(path, record) for path, record in records.items() if record.get("harness") in scope]
    if not args.harnesses:
        locations += [routing.workspace_location(Path(root)) for root in manifest.get("workspace_roots", [])]
    items = routing.plan_remove(locations, records)
    print("\nRouting removal plan (skills are unchanged)")
    print_routing_items(items)
    if args.dry_run:
        print("Dry run complete. No files changed.")
        return 0
    if not args.yes and not ask_bool("Remove this routing", False):
        print("Routing removal cancelled. No files changed.")
        return 0
    removed, kept, backups = routing.apply_remove(items, new_backup_root(home), confirm_routing_approvals(args, items))
    if manifest_exists:
        updated = finish_removal(manifest, removed)
        if args.harnesses:
            updated["routing_declined"] = sorted({*manifest.get("routing_declined", []), *harnesses})
        else:
            updated["routing_mode"] = "disabled"
            updated["routing_declined"] = []
        atomic_json_write(manifest_path(home), updated)
    return report_removal(removed, kept, backups, home)


def remove_workspace_command(args: argparse.Namespace, home: Path) -> int:
    manifest_exists = manifest_path(home).exists()
    manifest = read_manifest(home)
    records = manifest.get("routing", {})
    roots = manifest.get("workspace_roots", [])
    locations = []
    for raw in args.remove_workspace_root:
        root = raw.expanduser().resolve()
        location = routing.workspace_location(root)
        if str(root) not in roots and str(location.path) not in records:
            raise ValueError(f"{root} is not a recorded workspace root")
        locations.append(location)
    items = routing.plan_remove(locations, records)
    print("\nWorkspace routing removal plan")
    print_routing_items(items)
    if args.dry_run:
        print("Dry run complete. No files changed.")
        return 0
    if not args.yes and not ask_bool("Remove this workspace routing", False):
        print("Workspace routing removal cancelled. No files changed.")
        return 0
    removed, kept, backups = routing.apply_remove(items, new_backup_root(home), set())
    if manifest_exists:
        atomic_json_write(manifest_path(home), finish_removal(manifest, removed))
    return report_removal(removed, kept, backups, home)


def uninstall_command(args: argparse.Namespace, home: Path) -> int:
    path = manifest_path(home)
    if not path.exists():
        print(f"No install manifest at {path}")
        return 1
    manifest = read_manifest(home)
    targets = manifest.get("targets", {})
    records = manifest.get("routing", {})
    harnesses = set(HARNESSES) if args.all else set(parse_harness_list(args.harnesses))
    skill_items: list[dict[str, Any]] = []
    for raw_target, metadata in sorted(targets.items()):
        owners = list(metadata.get("harnesses", []))
        remaining = [] if args.all else [name for name in owners if name not in harnesses]
        if remaining == owners and not args.all:
            continue
        target = Path(raw_target)
        status = "release" if remaining else ("remove" if target.exists() else "forget")
        edited = status == "remove" and tree_hash(target) != metadata.get("hash")
        skill_items.append({"target": raw_target, "status": status, "remaining": remaining, "edited": edited})
    locations = [routing.record_location(raw, record) for raw, record in records.items() if args.all or record.get("harness") in harnesses]
    locations += [routing.harness_location(name, home) for name in sorted(harnesses) if name in routing.ROUTING_HARNESSES]
    if args.all:
        locations += [routing.workspace_location(Path(root)) for root in manifest.get("workspace_roots", [])]
    routing_items = routing.plan_remove(locations, records)

    print("\nUninstall plan")
    print(f"  Harnesses: {'all' if args.all else ', '.join(sorted(harnesses))}")
    for item in skill_items:
        detail = f" (still used by {', '.join(item['remaining'])})" if item["remaining"] else ""
        detail += " (edited since installation; backed up)" if item["edited"] else ""
        print(f"    {item['status']}: {item['target']}{detail}")
    print("  Routing:")
    print_routing_items(routing_items)
    print(f"  Backups and local state stay under {config_dir(home)}")
    if args.dry_run:
        print("Dry run complete. No files changed.")
        return 0
    if not args.yes and not ask_bool("Apply this uninstall plan", False):
        print("Uninstall cancelled. No files changed.")
        return 0

    backup_root = new_backup_root(home)
    remaining_targets = dict(targets)
    moved = 0
    for item in skill_items:
        target = Path(item["target"])
        if item["status"] == "release":
            remaining_targets[item["target"]] = {**targets[item["target"]], "harnesses": item["remaining"]}
            continue
        if item["status"] == "remove" and target.exists():
            backup = routing.backup_path(backup_root, target)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), str(backup))
            moved += 1
        remaining_targets.pop(item["target"], None)
    removed, kept, backups = routing.apply_remove(routing_items, backup_root, confirm_routing_approvals(args, routing_items))
    updated = finish_removal({**manifest, "targets": remaining_targets}, removed)
    if args.all:
        for key in ("routing_mode", "routing_declined"):
            updated.pop(key, None)
    atomic_json_write(path, updated)
    update_config_harnesses(home, harnesses)
    print(f"Moved {moved} skill copies to {backup_root}.")
    return report_removal(removed, kept, backups, home)


def purge_state_command(args: argparse.Namespace, home: Path) -> int:
    state = config_dir(home)
    manifest = read_manifest(home)
    if manifest.get("targets") or manifest.get("routing"):
        print("Managed skills or routing remain. Run --uninstall --all first; --purge-state only removes local state.")
        return 1
    marked, unsafe = routing.marked_locations(home, {}, manifest.get("workspace_roots", []))
    if marked or unsafe:
        print("Astrobyte routing markers remain outside the manifest. Run --uninstall --all, or remove them by hand, before purging state:")
        for entry in [*map(str, marked), *unsafe]:
            print(f"  {entry}")
        return 1
    files = [state / name for name in STATE_FILES if (state / name).exists()]
    if not files:
        print(f"No Astrobyte state files under {state}.")
        return 0
    print("\nState purge plan")
    for file in files:
        print(f"    remove: {file}")
    print(f"  Backups under {state / 'backups'} stay; remove them yourself when you no longer need them.")
    if args.dry_run:
        print("Dry run complete. No files changed.")
        return 0
    if not args.yes and not ask_bool("Remove these state files", False):
        print("State purge cancelled. No files changed.")
        return 0
    for file in files:
        file.unlink()
    print(f"Removed {len(files)} state file(s).")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        return run(argv)
    except routing.RoutingError as exc:
        print(f"Routing error: {exc}")
        return 1


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    home = args.home.expanduser().resolve()
    if home == Path(home.anchor):
        raise ValueError("The installation home cannot be a filesystem root")
    if args.check:
        return check_install(home)
    operation = args.remove_routing or args.uninstall or args.purge_state or bool(args.remove_workspace_root)
    install_flags = {
        "--quick": args.quick,
        "--interview": args.interview,
        "--answers": args.answers,
        "--skills": args.skills is not None,
        "--profile": args.profile,
        "--operator": args.operator,
        "--preferences": args.preferences,
        "--portable-preferences": args.portable_preferences,
        "--local-preferences": args.local_preferences,
        "--routing": args.routing,
        "--skills-only": args.skills_only,
        "--workspace-root": args.workspace_root,
    }
    used = [flag for flag, value in install_flags.items() if value]
    if operation and used:
        raise ValueError(f"{', '.join(used)} only apply to installation")
    if args.all and not args.uninstall:
        raise ValueError("--all only applies to --uninstall")
    if args.uninstall and bool(args.all) == bool(args.harnesses):
        raise ValueError("Use --uninstall with exactly one of --harnesses or --all")
    if (args.purge_state or args.remove_workspace_root) and args.harnesses:
        raise ValueError("--harnesses does not apply to this operation")
    if args.remove_routing:
        return remove_routing_command(args, home)
    if args.remove_workspace_root:
        return remove_workspace_command(args, home)
    if args.uninstall:
        return uninstall_command(args, home)
    if args.purge_state:
        return purge_state_command(args, home)
    if args.harnesses and (args.interview or args.answers):
        raise ValueError("--harnesses is for quick installation; use interview or answer-file selections otherwise")
    if args.quick and args.answers:
        raise ValueError("Choose --quick or --answers")
    if (args.skills is not None or args.profile) and (args.interview or args.answers):
        raise ValueError("--skills and --profile are quick-install choices")

    catalog = load_json(CATALOG_PATH)
    operator_profile, machine_registry, _ = load_operator(REPO_ROOT, args.operator)
    preference_path = args.preferences or config_dir(home) / "preferences.json"
    preferences = validate_preferences(load_json(preference_path)) if preference_path.exists() else None
    if args.preferences and preferences is None:
        raise ValueError("Explicit preferences file is unavailable")
    if preferences and "optional_skills" in preferences["overrides"]:
        validate_optional_skills(preferences["overrides"]["optional_skills"], catalog)
    if args.portable_preferences and preferences is None:
        raise ValueError("Approve a preferences file before enabling portable preference export")
    machine_answers = None
    if args.answers:
        machine_answers = load_json(args.answers)
        validate_answers(dict(machine_answers), catalog)
        harnesses = machine_answers["harnesses"]
        print(f"Using reviewed setup answers from {args.answers}")
    elif args.interview:
        machine_answers = interactive_answers(home, operator_profile, machine_registry, preferences)
        harnesses = machine_answers["harnesses"]
    else:
        harnesses = args.harnesses.split(",") if args.harnesses else detect_harnesses(home)
        harnesses = list(dict.fromkeys(name.strip().lower() for name in harnesses))
        if not harnesses:
            harnesses = ask_harnesses([])
        unknown = sorted(set(harnesses) - HARNESSES.keys())
        if unknown:
            raise ValueError(f"Unknown harnesses: {', '.join(unknown)}")
    answers = resolve_install_answers(home, operator_profile, harnesses, preferences, machine_answers)
    if machine_answers is None:
        print(f"Quick installation: shared {operator_profile['handle']} baseline; no onboarding interview")
        if answers["git_identity"].get("mode") == "disabled":
            print("Git attribution is disabled; configure your own Git identity before enabling it.")
    if args.portable_preferences:
        answers["portable_preferences"] = True
    elif args.local_preferences:
        answers["portable_preferences"] = False
    if preferences is not None:
        answers["_preferences"] = preferences
    if args.skills is not None:
        answers["selected_skills"] = list(dict.fromkeys(name.strip() for name in args.skills.split(",")))
    elif args.profile:
        answers["profile"] = args.profile
        answers.pop("selected_skills", None)
        answers.get("_baseline_values", {}).pop("profile", None)
    answers = validate_answers(answers, catalog)
    quick_mode = not args.interview and not args.answers
    plan = build_plan(answers, home, catalog, prune=not quick_mode)
    print_plan(answers, plan, home)

    manifest_exists = manifest_path(home).exists()
    manifest = read_manifest(home)
    selected = {item["skill"] for item in plan if not item["status"].startswith("archive-")}
    write_routing, routing_mode, routing_reason = routing_decision(args, manifest, manifest_exists, selected)
    new_roots = []
    for raw in args.workspace_root:
        root = raw.expanduser().resolve()
        if not root.is_dir():
            raise ValueError(f"--workspace-root must be an existing directory: {root}")
        new_roots.append(str(root))
    if new_roots and not write_routing:
        raise ValueError(f"--workspace-root needs routing, which was {routing_reason}")
    declined = set(manifest.get("routing_declined", []))
    if args.routing:
        declined -= set(answers["harnesses"])
    workspace_roots = list(dict.fromkeys([*manifest.get("workspace_roots", []), *new_roots]))
    routing_harnesses = [name for name in answers["harnesses"] if name in routing.ROUTING_HARNESSES and name not in declined]
    routing_items = routing.plan_install(home, routing_harnesses, [Path(root) for root in workspace_roots], manifest.get("routing", {})) if write_routing else []
    print(f"  Routing: {routing_reason}")
    print_routing_items(routing_items)
    for name in answers["harnesses"]:
        if name in declined and name in routing.ROUTING_HARNESSES:
            print(f"    skipped: routing for {name} was removed; rerun with --routing to restore it")
    for raw_path, record in manifest.get("routing", {}).items():
        if record.get("harness") not in {*answers["harnesses"], "workspace"}:
            print(f"    preserved: {raw_path} ({record.get('harness')} is no longer selected; remove it with --remove-routing --harnesses {record.get('harness')})")
    hermes_warning = "hermes" in answers["harnesses"]
    if hermes_warning:
        print("    Hermes has no automatic routing; invoke astrobyte-mode explicitly there.")

    pending = [item for item in routing_items if item.get("approval")]
    if args.dry_run:
        print("Dry run complete. No files changed.")
        return 0
    if pending and args.yes and not args.routing:
        print("Routing needs explicit approval:")
        for item in pending:
            print(f"  {item['approval']}")
        print("Rerun with --routing to approve, without --yes to confirm each item, or with --skills-only to skip routing. No files changed.")
        return 1
    if not args.yes and not ask_bool("Apply this installation plan", False):
        print("Installation cancelled. No files changed.")
        return 0
    approved = confirm_routing_approvals(args, routing_items)
    for item in pending:
        if item["path"] not in approved:
            item["status"] = "declined"
            if item["harness"] != "workspace":
                declined.add(item["harness"])

    routing_state: dict[str, Any] = {"routing_mode": routing_mode}
    if write_routing:
        routing_state["routing_declined"] = sorted(declined)
        routing_state["workspace_roots"] = [root for root in workspace_roots if not any(
            item["status"] == "declined" and item["path"] == str(routing.workspace_location(Path(root)).path) for item in routing_items
        )]
    backups = apply_plan(answers, plan, home, preserve_existing=quick_mode, routing_items=routing_items, routing_state=routing_state)
    installed = sum(not item["status"].startswith("archive-") for item in plan)
    print(f"Installed {installed} skill copies across {len(destination_groups(answers['harnesses'], home))} destination(s).")
    written = [item for item in routing_items if item["status"] not in {"same", "declined"}]
    if routing_items:
        print(f"Routing: {len(written)} written, {sum(item['status'] == 'same' for item in routing_items)} unchanged, "
              f"{sum(item['status'] == 'declined' for item in routing_items)} declined.")
    if hermes_warning:
        print("Hermes: automatic routing is unavailable; invoke astrobyte-mode explicitly for substantial work.")
    print(f"Machine config: {config_dir(home) / 'config.json'}")
    print(f"Install manifest: {manifest_path(home)}")
    if backups:
        print(f"Backed up {len(backups)} replaced items under {config_dir(home) / 'backups'}")
    return check_install(home)


if __name__ == "__main__":
    raise SystemExit(main())
