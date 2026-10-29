# Codex adapter

Install portable user skills in `~/.agents/skills`. Codex also supports `~/.codex/skills`, but the shared location avoids a second copy when OpenCode is installed.

The installer keeps a marked routing block in `$CODEX_HOME/AGENTS.md`, defaulting to `~/.codex/AGENTS.md`. A non-empty `AGENTS.override.md` beside it hides that file, and `--check` reports it as shadowed. Project discovery stops at the Git root. See [Routing](../docs/routing.md).

Use `agents/openai.yaml` to make costly skills explicit-only with `policy.allow_implicit_invocation: false`. `astrobyte-review` is explicit-only, so `astrobyte-mode` reaches it by reading the sibling `../astrobyte-review/SKILL.md`. Keep product and API questions grounded in the native OpenAI documentation skill.

Codex permissions remain authoritative. A preference for autonomous work never grants permission for destructive commands, external messages, publication, or credentials.

Official reference: https://learn.chatgpt.com/docs/build-skills

Runtime dispatch lives in [`skills/astrobyte-review/references/reviewer-dispatch.md`](../skills/astrobyte-review/references/reviewer-dispatch.md). Dispatch the configured reviewer as a read-only subagent; the packaged baseline is the newest offered Sol model. In the spawn request, name that model and leave reasoning effort unset, so Codex uses the model's default. A custom agent file can set `sandbox_mode = "read-only"`. A custom agent file that sets only `model` keeps the previously resolved reasoning effort, so name the model in the spawn request. When a subagent spawn is unavailable, run `codex --ask-for-approval never exec --sandbox read-only` with `--model` set to the same model and no reasoning-effort override. If neither is available, the push or pull request waits.

Subagent reference: https://developers.openai.com/codex/subagents
