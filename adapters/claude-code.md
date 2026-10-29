# Claude Code adapter

Install personal skills in `~/.claude/skills`. Claude Code supports the Agent Skills format plus invocation controls, dynamic context, hooks, and forked skill context.

The installer owns `rules/astrobyte-routing.md` in the same Claude root as the skills. `CLAUDE_CONFIG_DIR` moves both. Claude Code 2.1.277 or newer reads a project `AGENTS.md` when no `CLAUDE.md` or `CLAUDE.local.md` masks it; keep `@AGENTS.md` in a project `CLAUDE.md` otherwise. See [Routing](../docs/routing.md#projects-and-workspaces). For Claude Code in Docker Sandboxes, follow the opt-in [Docker Sandboxes](../docs/docker-sandboxes.md) steps.

Use hooks for deterministic safety where available. Keep `git-guardrails-claude-code` as a separate Claude-only installation rather than embedding hook assumptions in portable skills.

Claude Code offers GPT models only through an LLM gateway that lists them in its model picker. When it offers the configured reviewer model, the review gate runs a headless `claude -p` session on that model with only read and search tools. Otherwise it dispatches through an installed, authenticated Codex CLI in read-only mode. Without either, the push or pull request waits. See [`reviewer-dispatch.md`](../skills/astrobyte-review/references/reviewer-dispatch.md).

Official reference: https://code.claude.com/docs/en/slash-commands
