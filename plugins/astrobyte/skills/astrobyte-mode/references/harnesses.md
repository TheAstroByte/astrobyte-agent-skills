# Harness mapping

Use available native tools. Names below describe capabilities, not literal commands.

| Capability | Codex | OpenCode | Cursor | Claude Code | Hermes | Mistral Vibe |
|---|---|---|---|---|---|---|
| Skill root | `~/.agents/skills` | `~/.agents/skills` | `~/.cursor/skills` | `~/.claude/skills` | `~/.hermes/skills/astrobyte` or external dir | `~/.agents/skills` (shared with Codex and OpenCode); also `~/.vibe/skills` |
| Delegation | sub-agents or tasks when available | agents/tasks | Cursor agents/tasks | subagents or agent teams | delegation/toolsets | `agents.spawn` subagents; custom subagents in `~/.vibe/agents/` |
| Browser | in-app browser or DevTools integration | configured browser tools | Cursor browser/control tools | configured browser tools | browser toolset or skill | configured browser tools or connectors |
| Session recovery | task/thread tools and repo state | session plus repo state | chat history plus repo state | conversation history plus repo state | memory, session, and repo state | `vibe -c` or `--resume` plus repo state |
| Explicit skill | `$skill-name` | native skill tool; `@skill-id` in version 2 | slash command | `/skill-name` | `/skill-name` | `/skill-name`; the model loads skills through its `skill` tool |
| Reviewer dispatch | Read-only subagent or `codex exec` on the configured model | Read-only agent on the configured model, otherwise blocked | Task `model` set to the configured offered slug | Headless `claude -p` with read-only tools when the session offers the configured model, else read-only Codex CLI, otherwise blocked | Read-only delegation on the configured model, otherwise blocked | Read-only subagent on the configured model via `agents.spawn`, otherwise blocked |

For the independent review gate, read `../../astrobyte-review/references/reviewer-dispatch.md` resolved from this file's directory and follow its reviewer-selection policy, including any binding local requirement. Resolve models and tools from the current environment; report an unavailable required capability. A missing independent route leaves publication pending. Runtime execution does not require the source repository's installation adapters. Read a matching source adapter only when changing installation behavior from a full checkout.

Native invocation controls and ordinary file reads are distinct. Read a procedure only when the task or governing workflow authorizes it and the host permits it. Honor denied calls and explicit-only operation requirements. A file pointer is not permission to bypass a host restriction.
