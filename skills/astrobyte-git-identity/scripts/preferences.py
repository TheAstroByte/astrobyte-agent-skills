"""Validate reusable baseline overrides without importing machine configuration."""

from __future__ import annotations

import re
from typing import Any


DEFAULT_CHOICES = {
    "delivery_mode": {"explore", "prototype", "durable", "production", "ask"},
    "autonomy_preset": {"exact-scope", "guided-implementation", "bounded-autonomy", "prototype-sprint"},
    "communication_style": {"strictly-comply", "collaborative-challenge", "actively-challenge"},
    "explanation_level": {"expert-concise", "collaborative", "guided-teaching"},
    "git_workflow": {"branch", "worktree", "current-tree"},
    "issue_tracker": {"local", "github", "linear", "none"},
    "skill_update_policy": {"manual-only", "notify", "manual-reviewed", "auto-reviewed-pr", "auto-merge-gated"},
    "external_actions": {"ask", "reversible-only", "allow-configured"},
    "unattended_external_actions": {"ask", "reversible-only", "allow-configured"},
}
BOOL_DEFAULTS = {"ci_validation", "unattended_runs"}


def validate_pr_workflows(value: Any) -> None:
    """Validate reusable workflow choices, never model routes or authority."""
    if not isinstance(value, dict) or set(value) - {"review_method", "council_round_limit", "t3"}:
        raise ValueError("Invalid pr_workflows preferences")
    if "review_method" in value and value["review_method"] not in ("baseline", "sol-loop"):
        raise ValueError("Invalid pr_workflows review_method")
    if "council_round_limit" in value and (type(value["council_round_limit"]) is not int or not 1 <= value["council_round_limit"] <= 20):
        raise ValueError("pr_workflows council_round_limit must be an integer from 1 to 20")
    if "t3" in value and type(value["t3"]) is not bool:
        raise ValueError("pr_workflows t3 must be a boolean")


def inherited_values(config: dict[str, Any]) -> dict[str, Any]:
    record = config.get("baseline_inheritance", {})
    if not isinstance(record, dict) or not isinstance(record.get("values", {}), dict):
        raise ValueError("Invalid baseline inheritance")
    return record.get("values", {})


def validate_defaults(values: Any) -> None:
    if not isinstance(values, dict):
        raise ValueError("Preference defaults must be an object")
    allowed = set(DEFAULT_CHOICES) | BOOL_DEFAULTS | {"max_parallel_workers", "experiment_budget"}
    unknown = set(values) - allowed
    if unknown:
        raise ValueError(f"Nonportable or unknown preference fields: {', '.join(sorted(unknown))}")
    for key, value in values.items():
        if key in DEFAULT_CHOICES and (not isinstance(value, str) or value not in DEFAULT_CHOICES[key]):
            raise ValueError(f"Invalid preference {key}")
        if key in BOOL_DEFAULTS and type(value) is not bool:
            raise ValueError(f"Invalid preference {key}")
        if key == "max_parallel_workers" and (type(value) is not int or not 1 <= value <= 32):
            raise ValueError("Invalid preference max_parallel_workers")
        if key == "experiment_budget" and (not isinstance(value, str) or not value.strip()):
            raise ValueError("Invalid preference experiment_budget")


def validate_preferences(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or type(value.get("schema_version")) is not int or value.get("schema_version") != 1:
        raise ValueError("Preferences must use schema_version 1")
    if set(value) - {"schema_version", "baseline", "overrides", "working_agreement"}:
        raise ValueError("Preferences contain nonportable or unknown fields")
    baseline = value.get("baseline")
    if not isinstance(baseline, dict) or set(baseline) != {"handle", "repository_version"}:
        raise ValueError("Preferences must name their baseline handle and repository_version")
    if baseline["handle"] != "astrobyte" or not isinstance(baseline["repository_version"], str) or not baseline["repository_version"].strip():
        raise ValueError("Preferences must extend a versioned Astrobyte baseline")
    overrides = value.get("overrides")
    if not isinstance(overrides, dict) or set(overrides) - {"defaults", "review", "git_identity", "skill_profile", "optional_skills", "pr_workflows"}:
        raise ValueError("Invalid preference overrides")
    validate_defaults(overrides.get("defaults", {}))
    if "skill_profile" in overrides and (not isinstance(overrides["skill_profile"], str) or overrides["skill_profile"] not in {"core", "builder", "full"}):
        raise ValueError("Invalid preference skill_profile")
    if "optional_skills" in overrides:
        names = overrides["optional_skills"]
        if not isinstance(names, list) or any(not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) for name in names):
            raise ValueError("Preference optional_skills must contain lowercase skill names")
        if len(names) != len(set(names)):
            raise ValueError("Preference optional_skills must not contain duplicates")
    if "pr_workflows" in overrides:
        validate_pr_workflows(overrides["pr_workflows"])
    if "review" in overrides:
        review = overrides["review"]
        if not isinstance(review, dict) or set(review) != {"instructions"} or not isinstance(review["instructions"], str) or not review["instructions"].strip():
            raise ValueError("Review overrides must contain approved instructions")
    if "git_identity" in overrides:
        identity = overrides["git_identity"]
        if not isinstance(identity, dict) or set(identity) - {"mode", "trailer_key", "verify_before_push"}:
            raise ValueError("Portable Git overrides exclude human identity and machine facts")
        if "mode" in identity and (not isinstance(identity["mode"], str) or identity["mode"] not in {"dual-attribution", "agent-only", "human-with-agent-trailer", "disabled"}):
            raise ValueError("Invalid Git preference mode")
        if "trailer_key" in identity and (not isinstance(identity["trailer_key"], str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*", identity["trailer_key"])):
            raise ValueError("Invalid Git preference trailer_key")
        if "verify_before_push" in identity and type(identity["verify_before_push"]) is not bool:
            raise ValueError("Invalid Git preference verify_before_push")
    if "working_agreement" in value and (not isinstance(value["working_agreement"], str) or not value["working_agreement"].strip()):
        raise ValueError("Working agreement overrides must contain approved normalized rules")
    return value
