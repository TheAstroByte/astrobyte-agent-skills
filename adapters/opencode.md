# OpenCode adapter

Install portable user skills in `~/.agents/skills`, which OpenCode discovers automatically. OpenCode also supports `~/.config/opencode/skills`.

The installer keeps a marked routing block in `$XDG_CONFIG_HOME/opencode/AGENTS.md`, defaulting to `~/.config/opencode/AGENTS.md`. Creating that file stops OpenCode from reading `~/.claude/CLAUDE.md` as global instructions, so the installer asks before doing it. See [Routing](../docs/routing.md).

Use skill permissions and `metadata.opencode/autoinvoke` when a skill should remain explicit. `astrobyte-review` is explicit-only, so `astrobyte-mode` reaches it by reading the sibling `../astrobyte-review/SKILL.md`. Map delegation to the configured OpenCode agents and respect the selected local or hosted model's ability to follow multi-step skills.

The review gate uses a configured read-only agent only when that agent offers the configured reviewer model. Otherwise the push or pull request waits. See [`reviewer-dispatch.md`](../skills/astrobyte-review/references/reviewer-dispatch.md).

Official reference: https://opencode.ai/docs/skills
