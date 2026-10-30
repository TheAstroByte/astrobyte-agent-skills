# OpenCode adapter

Install portable user skills in `~/.agents/skills`, which OpenCode discovers automatically. OpenCode also supports `~/.config/opencode/skills`.

The installer keeps a marked routing block in `$XDG_CONFIG_HOME/opencode/AGENTS.md`, defaulting to `~/.config/opencode/AGENTS.md`. Creating that file stops OpenCode from reading `~/.claude/CLAUDE.md` as global instructions, so the installer asks before doing it. See [Routing](../docs/routing.md).

Check the installed OpenCode version. [Version 1](https://opencode.ai/docs/skills/) ignores invocation metadata; skill permissions control native loading. [Version 2](https://dev.opencode.ai/v2/docs/skills/) hides `metadata.opencode/autoinvoke: false` skills from automatic discovery while retaining explicit loading by ID. V2 also recognizes `disable-model-invocation: true`, with `opencode/autoinvoke` taking precedence. These fields do not establish the same enforcement on both versions.

The stack keeps optional operations explicit in their instructions. Its required review gate may read the sibling `../astrobyte-review/SKILL.md` through an authorized file read when permitted. Honor host denials; a file read is not a workaround for a blocked native call. Map delegation to configured OpenCode agents and respect the selected model's ability to follow multi-step skills.

The review gate uses a configured read-only agent only when that agent offers the configured reviewer model. Otherwise the push or pull request waits. See [`reviewer-dispatch.md`](../skills/astrobyte-review/references/reviewer-dispatch.md).

For explicit loading, V1's native skill tool takes `name`; V2's takes `id`, and the user can mention `@skill-id`. Use the actual offered tool schema rather than guessing a slash command.
