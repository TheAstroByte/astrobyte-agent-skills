#!/usr/bin/env python3
"""Create and audit Git commits with configured human and agent attribution."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from preferences import inherited_values, validate_preferences


TRAILER_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9-]*$")


@dataclass(frozen=True)
class Identity:
    name: str
    email: str

    @property
    def display(self) -> str:
        return f"{self.name} <{self.email}>"


@dataclass(frozen=True)
class Policy:
    mode: str
    trailer_key: str
    human: Identity
    agent: Identity
    harness: str

    @property
    def trailer(self) -> str:
        return f"{self.trailer_key}: {self.agent.display}"


def load_object(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def config_path(raw: Path | None) -> Path:
    if raw:
        candidate = raw.expanduser()
        return (candidate / "config.json" if candidate.is_dir() else candidate).resolve()
    override = os.environ.get("ASTROBYTE_CONFIG")
    if override:
        candidate = Path(override).expanduser()
        return (candidate / "config.json" if candidate.is_dir() else candidate).resolve()
    return Path.home() / ".config" / "astrobyte-agent-skills" / "config.json"


def parse_identity(value: Any, field: str) -> Identity:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    name = value.get("name")
    email = value.get("email")
    if not isinstance(name, str) or not name.strip() or any(char in name for char in "\r\n<>"):
        raise ValueError(f"{field}.name is invalid")
    if (
        not isinstance(email, str)
        or "@" not in email
        or email.startswith("@")
        or email.endswith("@")
        or any(char in email for char in "\r\n<> ")
    ):
        raise ValueError(f"{field}.email is invalid")
    return Identity(name.strip(), email)


def environment_identity() -> Identity:
    values: dict[str, str] = {}
    for field, variable in (("name", "GIT_AUTHOR_NAME"), ("email", "GIT_AUTHOR_EMAIL")):
        if variable in os.environ:
            values[field] = os.environ[variable]
        else:
            result = run_git(["config", "--get", f"user.{field}"], capture=True)
            if result.returncode not in {0, 1}:
                raise ValueError(result.stderr.strip() or "Cannot resolve effective Git identity")
            values[field] = result.stdout.strip()
    try:
        return parse_identity(values, "environment Git author")
    except ValueError as exc:
        raise ValueError("Configure your own Git author name and email in this environment before committing") from exc


def load_policy(path: Path, harness: str, *, explicit: bool = False) -> Policy:
    reference = Path(__file__).resolve().parents[1] / "references"
    baseline_policy = load_object(reference / "git-policy.json")["git_identity"]
    for preferences_path in (reference / "preferences.json", path.parent / "preferences.json"):
        if preferences_path.exists():
            delta = validate_preferences(load_object(preferences_path))
            baseline_policy.update(delta["overrides"].get("git_identity", {}))
    if path.exists():
        config = load_object(path)
        inherited = inherited_values(config)
        if config.get("git_identity") == inherited.get("git_identity"):
            config.pop("git_identity", None)
    elif explicit:
        raise ValueError(f"Explicit Git config is unavailable: {path}")
    else:
        config = {}
    git_identity = config.get("git_identity", baseline_policy)
    if not isinstance(git_identity, dict):
        raise ValueError(f"No git_identity object in {path}")
    mode = git_identity.get("mode")
    if mode not in {"dual-attribution", "agent-only", "human-with-agent-trailer"}:
        raise ValueError(f"git_identity.mode does not enable agent attribution: {mode!r}")
    trailer_key = git_identity.get("trailer_key", "Agent")
    if not isinstance(trailer_key, str) or not TRAILER_PATTERN.fullmatch(trailer_key):
        raise ValueError("git_identity.trailer_key is invalid")
    agents = git_identity.get("agents")
    if not isinstance(agents, dict) or harness not in agents:
        raise ValueError(f"No Git identity configured for harness {harness!r}")
    return Policy(
        mode=mode,
        trailer_key=trailer_key,
        human=parse_identity(git_identity["human"], "git_identity.human") if "human" in git_identity else environment_identity(),
        agent=parse_identity(agents[harness], f"git_identity.agents.{harness}"),
        harness=harness,
    )


def run_git(args: Sequence[str], *, env: dict[str, str] | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        check=False,
        text=True,
        env=env,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def identity_args(identity: Identity) -> list[str]:
    return ["-c", f"user.name={identity.name}", "-c", f"user.email={identity.email}"]


def commit(policy: Policy, commit_args: list[str]) -> int:
    if commit_args and commit_args[0] == "--":
        commit_args = commit_args[1:]
    if not commit_args:
        raise ValueError("Pass Git commit arguments after --")
    guarded = {"--author", "--reset-author", "--trailer"}
    if any(argument in guarded or any(argument.startswith(f"{item}=") for item in guarded) for argument in commit_args):
        raise ValueError("Commit arguments cannot override author or attribution trailers")

    amended_author = None
    if "--amend" in commit_args:
        name, email, _, _, _ = read_commit("HEAD")
        amended_author = parse_identity({"name": name, "email": email}, "existing commit author")

    environment = os.environ.copy()
    if policy.mode == "dual-attribution":
        environment["GIT_AUTHOR_NAME"] = policy.human.name
        environment["GIT_AUTHOR_EMAIL"] = policy.human.email
        committer = policy.agent
    elif policy.mode == "agent-only":
        environment["GIT_AUTHOR_NAME"] = policy.agent.name
        environment["GIT_AUTHOR_EMAIL"] = policy.agent.email
        committer = policy.agent
    else:
        environment["GIT_AUTHOR_NAME"] = policy.human.name
        environment["GIT_AUTHOR_EMAIL"] = policy.human.email
        committer = policy.human

    # Ambient committer variables otherwise override the command-local Git
    # configuration. Attribution owns this command, not the caller's shell.
    environment["GIT_COMMITTER_NAME"] = committer.name
    environment["GIT_COMMITTER_EMAIL"] = committer.email
    if amended_author is not None:
        environment["GIT_AUTHOR_NAME"] = amended_author.name
        environment["GIT_AUTHOR_EMAIL"] = amended_author.email

    trailer_position = commit_args.index("--") if "--" in commit_args else len(commit_args)
    attributed_args = [
        *commit_args[:trailer_position],
        "--trailer",
        policy.trailer,
        *(["--trailer", f"{policy.trailer_key}-Original-Author: {amended_author.display}"] if amended_author is not None else []),
        *commit_args[trailer_position:],
    ]
    result = run_git([*identity_args(committer), "commit", *attributed_args], env=environment)
    if result.returncode != 0:
        return result.returncode
    return verify_head(policy, quiet=False, author=amended_author, allow_preserved=amended_author is not None)


def read_commit(revision: str) -> tuple[str, str, str, str, str]:
    result = run_git(
        ["show", "-s", "--format=%an%x00%ae%x00%cn%x00%ce%x00%B", revision],
        capture=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() if result.stderr else f"Cannot read {revision}"
        raise ValueError(message)
    fields = result.stdout.split("\0", 4)
    if len(fields) != 5:
        raise ValueError(f"Unexpected Git metadata for {revision}")
    return fields[0], fields[1], fields[2], fields[3], fields[4]


def expected_parties(policy: Policy) -> tuple[Identity, Identity]:
    if policy.mode == "dual-attribution":
        return policy.human, policy.agent
    if policy.mode == "agent-only":
        return policy.agent, policy.agent
    return policy.human, policy.human


def author_matches(policy: Policy, name: str, email: str, message: str, *, allow_preserved: bool = True) -> bool:
    expected, _ = expected_parties(policy)
    if (name, email) == (expected.name, expected.email):
        return True
    # The agent records the existing author when amending. This travels with
    # the commit, including through a fresh clone without dangling old objects.
    return allow_preserved and f"{policy.trailer_key}-Original-Author: {name} <{email}>" in message.splitlines()


def verify_head(policy: Policy, *, quiet: bool, author: Identity | None = None, allow_preserved: bool = True) -> int:
    author_name, author_email, committer_name, committer_email, message = read_commit("HEAD")
    expected_author, expected_committer = expected_parties(policy)
    if author is not None:
        expected_author = author
    errors: list[str] = []
    if not author_matches(policy, author_name, author_email, message, allow_preserved=allow_preserved):
        errors.append(f"author is {author_name} <{author_email}>, expected {expected_author.display}")
    elif author is None:
        expected_author = Identity(author_name, author_email)
    if (committer_name, committer_email) != (expected_committer.name, expected_committer.email):
        errors.append(f"committer is {committer_name} <{committer_email}>, expected {expected_committer.display}")
    if policy.trailer not in message.splitlines():
        errors.append(f"missing trailer {policy.trailer!r}")
    if errors:
        for error in errors:
            print(f"invalid: {error}", file=sys.stderr)
        return 1
    if not quiet:
        print(f"author: {expected_author.display}")
        print(f"committer: {expected_committer.display}")
        print(f"trailer: {policy.trailer}")
    return 0


def default_audit_range() -> str:
    result = run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"], capture=True)
    if result.returncode != 0:
        raise ValueError("No upstream branch. Pass an explicit audit range, such as origin/main..HEAD")
    return f"{result.stdout.strip()}..HEAD"


def audit(policy: Policy, revision_range: str | None) -> int:
    selected_range = revision_range or default_audit_range()
    result = run_git(
        ["log", "--reverse", "--format=%H%x00%an%x00%ae%x00%cn%x00%ce%x00%B%x00%x1e", selected_range],
        capture=True,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or f"Cannot audit {selected_range}")
    expected_author, expected_committer = expected_parties(policy)
    invalid = 0
    records = [record for record in result.stdout.split("\x1e") if record.strip("\n\0")]
    if not records:
        print(f"No commits in {selected_range}")
        return 0
    for record in records:
        fields = record.strip("\n\0").split("\0", 5)
        if len(fields) != 6:
            raise ValueError(f"Unexpected Git log metadata in {selected_range}")
        revision, author_name, author_email, committer_name, committer_email, message = fields
        committer_matches = (committer_name, committer_email) == (policy.agent.name, policy.agent.email)
        trailer_matches = policy.trailer in message.splitlines()
        expected_matches = (
            author_matches(policy, author_name, author_email, message)
            and (committer_name, committer_email) == (expected_committer.name, expected_committer.email)
            and trailer_matches
        )
        if expected_matches:
            label = f"agent:{policy.harness}"
        elif committer_matches or trailer_matches:
            label = "invalid"
            invalid += 1
        else:
            label = "human-or-other"
        print(f"{label:16} {revision[:12]} {author_name} -> {committer_name}")
    return 1 if invalid else 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Machine config path")
    parser.add_argument("--harness", required=True, help="Active agent product key")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show", help="Show the configured attribution")
    subparsers.add_parser("verify-head", help="Verify HEAD against the configured attribution")
    audit_parser = subparsers.add_parser("audit", help="Audit an unpublished commit range")
    audit_parser.add_argument("revision_range", nargs="?", help="Git revision range; defaults to upstream..HEAD")
    commit_parser = subparsers.add_parser("commit", help="Create a commit with configured attribution")
    commit_parser.add_argument("commit_args", nargs=argparse.REMAINDER)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        path = config_path(args.config)
        policy = load_policy(path, args.harness, explicit=args.config is not None or bool(os.environ.get("ASTROBYTE_CONFIG")))
        if args.command == "show":
            author, committer = expected_parties(policy)
            print(f"author: {author.display}")
            print(f"committer: {committer.display}")
            print(f"trailer: {policy.trailer}")
            return 0
        if args.command == "verify-head":
            return verify_head(policy, quiet=False)
        if args.command == "audit":
            return audit(policy, args.revision_range)
        return commit(policy, args.commit_args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
