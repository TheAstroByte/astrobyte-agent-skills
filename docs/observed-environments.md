# Observed environments

Checked 30 October 2026 during public preparation, based on merged source revision `82ca58c349bfbf5f104f0986a4f33f2accd331b5`. This records evidence, not a support matrix or compatibility promise. The skills are distributed as-is.

## OS and execution evidence

| Environment | Observed | Limits |
|---|---|---|
| macOS 27.2, Python 3.13.5 | Local validator and full unittest suite; isolated CLI installs, updates, preferences, recovery, shared ownership, removal, and copied-package execution | These checks use temporary homes; they do not prove every host loads or follows the instructions. |
| Codex desktop on macOS | Agent-led implementation, attributed commits, and independent Sol reviews during preparation; an isolated research fallback and handoff exercise | This is live use in this task, not a clean-session discovery test for every installed package. Desktop version was not recorded. |
| Linux/Python 3.12 and 3.13; macOS/Python 3.12 | Workflow definitions prepared and inspected | Hosted Actions is disabled. No hosted matrix result is claimed. |
| Other OS and Python combinations | No release-preparation runtime result recorded here | Provide a reproduction and focused contribution if changes are needed. |

## Harness boundaries

| Harness | Evidence | Still unverified here |
|---|---|---|
| Codex | Temporary-home skill copies and managed instruction files; live work and independent review in this desktop session | Fresh-session discovery and the complete install-to-task path in another environment |
| OpenCode | Shared destinations and managed instruction files tested; CLI version 1.17.9 observed | Live skill activation, explicit controls, and review dispatch; version 1 and 2 have different metadata behavior |
| Cursor | Isolated copies, local routing file creation, and portable runtime resources tested | Local automatic discovery, personal sync, hosted Cloud Agents, and automation behavior |
| Claude Code | Isolated copies and routing ownership/removal tested | Live discovery, invocation controls, rules precedence, and reviewer access |
| Hermes | Isolated copies tested; installer reports unavailable automatic routing | Live recursive discovery and explicit invocation; automatic routing is not implemented |

The [adapters](../adapters/) describe documented host behavior. A source citation or successful file copy is not a live host result. Cursor's [cloud smoke checklist](cursor-cloud-smoke.md) remains pending until run in an actual hosted environment. Browser verification requires an available permitted route; no browser session was run during this preparation slice.

## Add an observation

Record the source revision, OS, Python and harness versions where relevant, minimal command or prompt, resulting artifact or test output, and unresolved capability. Distinguish reported use, package installation, fresh-session discovery, routing, task behavior, and hosted execution. Keep usernames, hostnames, credentials, private repositories, and absolute personal paths out of the record.

Use the [adapter contribution procedure](../CONTRIBUTING.md#extend-a-harness-or-fix-an-os-issue) for a fix. A passing report expands the evidence; it does not create a support or maintenance obligation.
