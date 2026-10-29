#!/usr/bin/env python3
"""Resolve installed runtime preferences without importing the source repository."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

try:
    from scripts.preferences import inherited_values, validate_preferences, validate_pr_workflows
except ModuleNotFoundError:
    from preferences import inherited_values, validate_preferences, validate_pr_workflows


EXPLICIT_POLICY_TYPES = {
    "max_parallel_workers": int,
    "unattended_runs": bool,
    "external_actions": str,
    "unattended_external_actions": str,
    "experiment_budget": str,
}


def object_file(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def resolve(skill: Path, project: Path, home: Path) -> dict[str, Any]:
    """Resolve file preferences; task instructions and repository evidence stay agent-owned."""
    reference = skill / "references"
    baseline_path = reference / ("baseline.json" if (reference / "baseline.json").exists() else "review-policy.json")
    baseline = object_file(baseline_path)
    preferences = dict(baseline["defaults"])
    sources = {key: "baseline" for key in preferences}
    review_instructions = baseline.get("review", {}).get("instructions")
    pr_workflows: dict[str, Any] = {}
    pr_workflow_sources: dict[str, str] = {}
    agreement_overrides: list[str] = []
    agreement_layers: list[dict[str, Any]] = []
    portable = reference / "preferences.json"
    raw_config = os.environ.get("ASTROBYTE_CONFIG")
    raw_config_home = os.environ.get("ASTROBYTE_CONFIG_HOME")
    config_home = Path(raw_config_home).expanduser() if raw_config_home else home / ".config/astrobyte-agent-skills"
    machine = Path(raw_config).expanduser() if raw_config else config_home / "config.json"
    if machine.is_dir():
        machine = machine / "config.json"
    if raw_config and not machine.is_file():
        raise ValueError(f"Explicit ASTROBYTE_CONFIG is unavailable: {machine}")
    personal = machine.parent / "operator-profile.json"
    agreement = machine.parent / "working-agreement.md"
    # This resolver exports policy only, never credentials or machine facts.
    # Existing profile snapshots stay explicit preferences until migrated.
    for label, path, nested in (
        ("portable-personal", portable, False),
        ("personal", personal, True),
        ("personal-delta", machine.parent / "preferences.json", False),
        ("machine", machine, False),
        ("project", project / ".astrobyte/config.json", False),
    ):
        if label == "personal" and agreement.is_file():
            agreement_layers.append({"source": "personal", "path": str(agreement)})
        if not path.exists():
            continue
        values = object_file(path)
        if label == "machine":
            inherited = inherited_values(values)
            values = {key: value for key, value in values.items() if key not in inherited or value != inherited[key] or key not in preferences}
        if label in {"portable-personal", "personal-delta"}:
            delta = validate_preferences(values)
            layer = {"source": label}
            if "working_agreement" in delta:
                agreement_overrides.append(delta["working_agreement"])
                layer["rules"] = delta["working_agreement"]
            review_instructions = delta["overrides"].get("review", {}).get("instructions", review_instructions)
            if "review" in delta["overrides"]:
                layer["review_instructions"] = review_instructions
            if len(layer) > 1:
                agreement_layers.append(layer)
            options = delta["overrides"].get("pr_workflows", {})
            values = delta["overrides"].get("defaults", {})
        else:
            options = values.get("pr_workflows", {})
        validate_pr_workflows(options)
        pr_workflows.update(options)
        pr_workflow_sources.update({key: label for key in options})
        if nested:
            values = values.get("defaults", {})
            if not isinstance(values, dict):
                raise ValueError(f"Expected defaults object in {path}")
        for key in set(baseline["defaults"]) | set(EXPLICIT_POLICY_TYPES):
            if key in values:
                expected_type = EXPLICIT_POLICY_TYPES.get(key, type(baseline["defaults"].get(key)))
                if type(values[key]) is not expected_type:
                    raise ValueError(f"Invalid type for {key} in {path}")
                if key == "delivery_mode" and values[key] not in {"explore", "prototype", "durable", "production", "ask"}:
                    raise ValueError(f"Invalid delivery_mode in {path}")
                if key == "max_parallel_workers" and not 1 <= values[key] <= 32:
                    raise ValueError(f"Invalid max_parallel_workers in {path}")
                preferences[key] = values[key]
                sources[key] = label
    packaged_agreement = reference / "working-agreement.md"
    result = {
        "baseline": baseline["baseline"],
        "preferences": preferences,
        "sources": sources,
        "packaged_working_agreement": str(packaged_agreement) if packaged_agreement.is_file() else None,
        "local_working_agreement": str(agreement) if agreement.is_file() else None,
        "working_agreement_overrides": agreement_overrides,
        "working_agreement_layers": agreement_layers,
        "review_instructions": review_instructions,
    }
    if pr_workflows:
        result["pr_workflows"] = pr_workflows
        result["pr_workflow_sources"] = pr_workflow_sources
        if pr_workflows.get("review_method") == "sol-loop":
            instruction = (
                "Use the selected Sol-loop method from "
                "../astrobyte-pr-workflows/references/sol-loop.md, resolved from this skill directory. "
                "Keep the configured reviewer, read-only dispatch, literal PASS requirement, and existing review gate. "
                "A missing optional package leaves this requested method pending; do not silently substitute."
            )
            result["review_instructions"] = f"{review_instructions}\n\n{instruction}" if review_instructions else instruction
            agreement_layers.append({"source": pr_workflow_sources["review_method"], "review_instructions": instruction})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        result = resolve(Path(__file__).resolve().parents[1], args.project, Path.home())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Runtime configuration error: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
