# Agent instructions

This repository distributes portable instructions to other agents. Treat routing metadata, completion criteria, installer safety, and cross-harness behavior as product code.

If the user requests installation or adoption of this stack, or invokes `$adopt-skill-stack` or `/adopt-skill-stack`, read `skills/adopt-skill-stack/SKILL.md`. Default to quick installation of the committed Astrobyte profile; run the onboarding interview only when explicitly requested. Honor an explicitly selected subset. Do not treat a clone as consent to install, publish, migrate, or overwrite anything.

## Repository contribution workflow

Before changing this repository, read [CONTRIBUTING.md](CONTRIBUTING.md). Work on a feature branch and submit a pull request against `main`. Only the repository owner, `TheAstroByte`, merges pull requests. Agents leave merging to the owner, including when using the owner's credentials. Do not push directly to `main`, force-push it, delete it, or enable auto-merge.

These rules govern this repository, not the reusable policies installed into other projects.

## Read by task

- Skill, `AGENTS.md`, or README wording: read `skills/writing-for-agents/SKILL.md` and its `SKILL-MECHANICS.md` before editing.
- Router, profile, or skill composition: read `docs/architecture.md`, `catalog.json`, and `skills/astrobyte-mode/SKILL.md`.
- Selection or replacement decisions: read `docs/skill-stack-assessment.md` and `docs/upstreams.md`.
- Installer or harness behavior: read `scripts/install.py` and the relevant file under `adapters/`. For routing, also read `docs/routing.md` and `scripts/routing.py`.
- Project startup or stack defaults: read `skills/astrobyte-project-startup/SKILL.md`, `skills/astrobyte-project-startup/references/stack-policy.md`, and `skills/astrobyte-project-startup/references/project-defaults.json`.
- Upstream refresh: read `docs/upstreams.md` and preserve the matching license file.
- Adoption or profile changes: read `skills/adopt-skill-stack/SKILL.md`, its relevant references, `docs/adoption.md`, and `docs/profile-reference.md`.
- Agent-created Git commit or push: read `skills/astrobyte-git-identity/SKILL.md`, use its helper, and audit the unpublished range.

## Change contract

1. Inspect the current source and the affected completion criteria.
2. Make one coherent change at a time.
3. Add or update tests for installer or validator behavior.
4. Run `python3 scripts/validate.py`.
5. Run `python3 -m unittest discover -s tests -v`.
6. Inspect the diff for secrets, machine paths, stale source pins, and accidental upstream edits.
7. Commit the verified checkpoint with a conventional message.

## Invariants

- The default installation previews its plan and asks for confirmation. Onboarding is optional; approved unattended installation uses --yes.
- Machine answers stay outside this repository.
- Existing unrelated skills remain untouched.
- Conflicting managed skills are backed up before replacement.
- The installer changes instruction files only inside its ownership markers, and stops on anything it cannot attribute. `docs/routing.md` is the routing contract.
- Every skill directory has a matching lowercase kebab-case `name` and a useful trigger description.
- Owned skills keep harness-specific details behind pointers in `adapters/` or skill references.
- Vendored files retain attribution and a pinned upstream commit.
- Documentation states durable behavior and points to executable sources for discoverable details.
- `unslop` remains in every catalog profile.
- Raw onboarding answers, secrets, hostnames, usernames, serial identifiers, local endpoints, and absolute machine paths never enter a committed operator profile.
