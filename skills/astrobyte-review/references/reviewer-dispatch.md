# Dispatch a read-only reviewer

Apply the configured reviewer preference to the current harness's offered models. The shared baseline requires the newest offered GPT Sol model at the harness default reasoning level. Use one reviewer, adding a second only when requested or when the change is broad or high-risk.

- Cursor: use Task with `model` set to the newest offered `gpt-*-sol*` slug, or the configured slug. When Sol slugs include reasoning levels, use the harness default unless an explicit preference changes it. Instruct the task to read and review without editing files.
- Codex: use a read-only subagent with the configured model and its default reasoning effort. When a subagent is unavailable, run `codex --ask-for-approval never exec --sandbox read-only --model <model>`; the approval flag must precede `exec`.
- Claude Code: Claude Code offers GPT models only through an LLM gateway that lists them in its model picker. When the session offers the configured model, pipe the brief to `claude -p --model <model> --setting-sources user --tools Read,Grep,Glob --strict-mcp-config --permission-mode plan --output-format json`, adding `--effort <level>` only when a preference sets the reasoning level. The review counts only when the result's `modelUsage` lists that model alone; a fallback model does not satisfy the gate. Otherwise use an installed, authenticated Codex CLI with the same read-only `codex exec` command. Without either, the gate is blocked.
- OpenCode: use a configured read-only agent only when it offers the configured model. Otherwise the gate is blocked.
- Other harnesses: use read-only delegation that offers the configured model. Otherwise the gate is blocked.

When the gate is blocked, report the missing model or delegation capability and leave the push or pull request waiting. Another model, a self-review, or an unconfigured substitute does not satisfy the gate. Installation adapters are unnecessary for this runtime dispatch.
