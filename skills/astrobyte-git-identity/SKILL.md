---
name: astrobyte-git-identity
description: Attribute Git commits made by an agent to both the operator and the active agent product without changing the operator's normal Git identity. Use before an agent creates, amends, or pushes commits.
---

# Astrobyte Git identity

Read machine config from `${ASTROBYTE_CONFIG}` when set, otherwise `~/.config/astrobyte-agent-skills/config.json`. When the optional file is absent, use this skill's packaged [Git policy](references/git-policy.json). Resolve the active agent product before committing. The helper uses the explicit configured human identity when present, otherwise the current environment's Git author variables and effective Git configuration, including conditional includes. Missing local configuration does not require installation or onboarding.

When author identity is unresolved, ask only for the colleague's own Git name and email when a commit requires them. An explicitly selected missing or malformed config is an error to resolve. If an explicit policy disables attribution, report that choice and use ordinary Git only within the user's authorization; the helper refuses attributed commits in disabled mode.

When attribution is enabled, a helper failure blocks the commit and push. Run the installed helper and inspect its actual error before reporting a blocker. Missing optional machine config is supported; do not prescribe setup to create it. A failure on that missing file may indicate an outdated or incomplete installed package. Report the error and required refresh directly to the operator. Do not silently fall back to an unattributed commit or add setup diagnostics to an unrelated PR description.

## Commit

Use this skill's `scripts/git_agent_identity.py` for every agent-created commit. Pass the active product explicitly:

```bash
python3 <skill-directory>/scripts/git_agent_identity.py --harness codex commit -- -m "feat: describe the change"
```

In the recommended `dual-attribution` mode, the helper records:

- the operator as author;
- the active agent product as committer;
- an `Agent: <name> <email>` commit trailer.

The helper applies identity to one command. It does not write global, repository, or worktree Git configuration. A later human commit therefore uses the operator's normal Git identity and has no agent trailer.

For an amend, preserve the existing author unless the operator approves a change in authorship. The helper supplies the agent committer and trailer, and records the preserved author in an `Agent-Original-Author` trailer. Later audits require that matching preservation record when the author differs from the current identity. New commits still verify against the configured author. Do not rewrite a published commit only to fix attribution without explicit approval.

## Push

When `git_identity.verify_before_push` is true, audit the unpublished range before pushing:

```bash
python3 <skill-directory>/scripts/git_agent_identity.py --harness codex audit
```

Inspect every `agent`, `human`, and `invalid` line. Stop if an agent-created commit is attributed as human-only, uses the wrong product identity, or lacks the configured trailer. Resolve an unknown upstream range explicitly. If verification is disabled, state that the configured audit was skipped.

A push does not change commit identity. GitHub still records the authenticated account or GitHub App as the push and pull-request actor. A distinct remote actor requires separate bot or App credentials and separate approval.

The identity check is complete when the unpublished commits show the intended author, committer, and trailer, and ordinary Git configuration remains unchanged.
