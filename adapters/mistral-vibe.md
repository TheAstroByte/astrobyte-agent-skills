# Mistral Vibe adapter

Install portable user skills in `~/.agents/skills`, the Agent Skills standard user-global directory that Vibe discovers automatically. Codex and OpenCode read the same directory, so one installer run covers all three: the installer writes a single shared copy and records every owning harness, and a copy is removed only when its last owner is uninstalled. Vibe's own user-global `~/.vibe/skills/` is also discovered, but the shared `~/.agents/skills` copy is the one place that keeps every harness current.

Vibe's skill search order is, first match wins: `skill_paths` from `config.toml`, then `.vibe/skills/` and `.agents/skills/` in a trusted project directory, then `~/.vibe/skills/`, then `~/.agents/skills/`. Project-local copies need a trusted folder; user-global copies need none. `enabled_skills` and `disabled_skills` patterns in `config.toml` filter discovery, and every `VIBE_*` environment variable overrides its config field.

The installer keeps a marked routing block in `$VIBE_HOME/AGENTS.md`, defaulting to `~/.vibe/AGENTS.md`. Vibe loads that file at the start of every session, plus each project `AGENTS.md` from the project root up through the trust chain. See [Routing](../docs/routing.md).

The user invokes a `user-invocable` skill with `/skill-name`; the model loads skills on demand through its `skill` tool. Vibe honors `disable-model-invocation: true` natively, so the management skills (`adopt-skill-stack`, `setup-astrobyte-skills`, `update-skill-stack`) stay explicit slash commands and never load implicitly. OpenCode's `metadata.opencode/autoinvoke` convention is not read by Vibe; the portable frontmatter flag is the one that counts here.

Delegation uses the `agents.spawn` tool; custom subagents live in `~/.vibe/agents/*.toml` or `.vibe/agents/` in a trusted project. The review gate uses a read-only subagent only when it offers the configured reviewer model; otherwise the push or pull request waits. See [`reviewer-dispatch.md`](../skills/astrobyte-review/references/reviewer-dispatch.md).

Start a fresh session and confirm `astrobyte-mode` is offered and loads for a bounded task; copying files alone does not prove activation. Official documentation: https://docs.mistral.ai/vibe/code/overview
