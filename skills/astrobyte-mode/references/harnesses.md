# Harness mapping

Use available native tools. Names below describe capabilities, not literal commands.

| Capability | Codex | OpenCode | Cursor | Claude Code | Hermes |
|---|---|---|---|---|---|
| Skill root | `~/.agents/skills` | `~/.agents/skills` | `~/.cursor/skills` | `~/.claude/skills` | `~/.hermes/skills/astrobyte` or external dir |
| Delegation | sub-agents or tasks when available | agents/tasks | Cursor agents/tasks | subagents or agent teams | delegation/toolsets |
| Browser | in-app browser or DevTools integration | configured browser tools | Cursor browser/control tools | configured browser tools | browser toolset or skill |
| Session recovery | task/thread tools and repo state | session plus repo state | chat history plus repo state | conversation history plus repo state | memory, session, and repo state |
| Explicit skill | `$skill-name` | skill tool or slash command | slash command | `/skill-name` | `/skill-name` |
| Reviewer dispatch | Read-only subagent or `codex exec` on the configured model | Read-only agent on the configured model, otherwise blocked | Task `model` set to the configured offered slug | Headless `claude -p` with read-only tools when the session offers the configured model, else read-only Codex CLI, otherwise blocked | Read-only delegation on the configured model, otherwise blocked |

For the independent review gate, read `../../astrobyte-review/references/reviewer-dispatch.md` resolved from this file's directory. An unavailable reviewer blocks the push or pull request; it never selects a substitute. Resolve models and tools from the current environment; report an unavailable required capability. Runtime execution does not require the source repository's installation adapters. Read a matching source adapter only when changing installation behavior from a full checkout.
