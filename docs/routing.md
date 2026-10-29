# Routing contract

Skills load on demand. An agent sees each skill's name and description, and reads the body only when it decides the skill applies. That is not reliable enough for gates such as the pre-push review. Routing closes the gap with a short instruction that each harness loads at the start of every session. The pointer names when to load `astrobyte-mode`, `astrobyte-review`, and `astrobyte-git-identity`. The skills keep all policy.

The canonical text is [templates/routing.md](../templates/routing.md). The installer writes it, records it, checks it, and removes it. This page is the single source for how that works. Change this page together with `scripts/routing.py` and `tests/test_routing.py`.

## Install

Clone the source and run the installer from it. Read access over HTTPS or SSH is enough.

```bash
git clone https://github.com/TheAstroByte/astrobyte-agent-skills.git
cd astrobyte-agent-skills
python3 scripts/install.py --harnesses cursor,codex,opencode,claude
```

The installer previews every skill and routing change, then asks once. Add `--dry-run` to preview without writing, or `--yes` after you have approved the exact plan.

Routing is installed when the selection contains `astrobyte-mode`, `astrobyte-review`, and `astrobyte-git-identity`. Every profile does. A leaf selection such as `--skills diagnosing-bugs` installs skills only and says why.

`npx skills add` copies standalone leaf skills. It does not resolve hard dependencies, install routing, or keep a manifest, so use the native installer for workflow skills.

## Where routing goes

| Harness | Location | Ownership | Override |
|---|---|---|---|
| Cursor (local) | `~/.cursor/rules/astrobyte-routing.mdc` | Whole file, `alwaysApply: true` | None |
| Claude Code | `<claude root>/rules/astrobyte-routing.md` | Whole file | `CLAUDE_CONFIG_DIR` sets the root; skills move with it |
| Codex | `<codex home>/AGENTS.md` | Marked block | `CODEX_HOME` |
| OpenCode | `<config home>/opencode/AGENTS.md` | Marked block | `XDG_CONFIG_HOME` |
| Workspace (opt-in) | `<root>/AGENTS.md` | Marked block | `--workspace-root <root>` |
| Hermes | None | Skills only | Invoke `astrobyte-mode` explicitly |

An owned file carries `<!-- astrobyte-routing: owned schema=1 -->`. A shared file gets one block between `<!-- astrobyte-routing:begin schema=1 -->` and `<!-- astrobyte-routing:end -->`. Content outside the block stays byte-for-byte unchanged, including a byte-order mark, CRLF line endings, a missing final newline, and the file mode.

The installer refuses to write when:

- the target is a symbolic link;
- markers are duplicated, nested, unclosed, unrecognized, or inside a code fence;
- an owned file exists without a matching record (for example a hand-written Cursor rule) or was edited after installation, unless you approve its replacement;
- creating OpenCode's global `AGENTS.md` would stop OpenCode from reading a non-empty `~/.claude/CLAUDE.md`, unless you approve it. The installer skips this check when `OPENCODE_DISABLE_CLAUDE_CODE` or `OPENCODE_DISABLE_CLAUDE_CODE_PROMPT` is set, because OpenCode then ignores that fallback anyway.

Interactive runs ask about each approval separately. With `--yes`, approvals require `--routing`; otherwise the run stops before writing anything. A replaced file is backed up first.

## Projects and workspaces

`AGENTS.md` is the shared project format. Codex, OpenCode, and Cursor read it. Claude Code 2.1.277 or newer reads it when the project has no `CLAUDE.md` or `CLAUDE.local.md`; use 2.1.281 or newer for Bedrock and telemetry-disabled sessions. When a project keeps a `CLAUDE.md`, put `@AGENTS.md` in it, or set Claude Code's Project instructions to `claude-md-and-agents-md`. The installer never edits a project `CLAUDE.md` or Claude settings.

`--workspace-root <path>` adds a routing block to that directory's `AGENTS.md`. It is a convenience for sessions started in that directory, not a cross-harness fallback. Codex stops project discovery at the Git root, so a nested repository does not inherit a parent directory's `AGENTS.md`. The installer warns when the file is tracked by Git or sits inside a work tree. Later installs keep recorded roots without repeating the flag.

Claude Code in Docker Sandboxes skips a workspace `AGENTS.md`, because sbx writes its own `CLAUDE.md` above the mounted workspace. The opt-in fix links a workspace `CLAUDE.md` to `AGENTS.md`; see [Docker Sandboxes](docker-sandboxes.md).

## Lifecycle

| Goal | Command |
|---|---|
| Preview | `python3 scripts/install.py --harnesses cursor --dry-run` |
| Check | `python3 scripts/install.py --check` |
| Skills without routing | `python3 scripts/install.py --harnesses cursor --skills-only` |
| Add or restore routing | `python3 scripts/install.py --harnesses cursor --routing` |
| Remove routing for one harness | `python3 scripts/install.py --remove-routing --harnesses cursor` |
| Remove all routing | `python3 scripts/install.py --remove-routing` |
| Add a workspace block | `python3 scripts/install.py --harnesses cursor --workspace-root ~/Developer` |
| Remove a workspace block | `python3 scripts/install.py --remove-workspace-root ~/Developer` |
| Uninstall one harness | `python3 scripts/install.py --uninstall --harnesses opencode` |
| Uninstall everything | `python3 scripts/install.py --uninstall --all` |
| Remove local state | `python3 scripts/install.py --purge-state` |

Each command previews and asks first. `--dry-run` and `--yes` apply to all of them.

The manifest records a routing mode that later runs respect:

- `enabled`: installs keep routing current for every selected harness that has not been removed.
- `disabled`: set by `--skills-only` on a new install or by `--remove-routing` without `--harnesses`, which also removes workspace blocks. Later installs skip routing until `--routing`.
- `migration-required`: an installation made before routing existed. A repeated `--yes` command updates skills and adds no routing. `--routing` adds it; `--skills-only` declines it.

`--remove-routing --harnesses <name>` removes that harness's routing and remembers the choice. `--skills-only` never removes routing. A harness that is no longer selected keeps its routing until you remove it.

`--uninstall --harnesses <name>` removes that harness's routing and its claim on each skill copy. Codex and OpenCode share `~/.agents/skills`; a copy there moves to backups only when neither still uses it. `--uninstall --all` removes every managed skill copy and routing target. Both keep backups, machine config, and preferences. `--purge-state` then removes the manifest, config, preferences, and profile snapshots. It refuses while managed targets or Astrobyte markers at the known routing locations remain, and always leaves backups.

Backups live under `~/.config/astrobyte-agent-skills/backups/<timestamp>/` unless `ASTROBYTE_CONFIG_HOME` points elsewhere.

Skill replacements are copied into a temporary sibling directory, including any exported preferences, and checked against the previewed package hash before the installed copy moves. A copy or hash failure leaves that installed skill intact. A caught promotion failure restores its prior copy from backup; if restoration fails, the error identifies the backup to inspect.

An installation containing several changes is not one transaction. Earlier completed changes may remain after a later failure, and abrupt process termination may require manual recovery from backups. Package replacement errors report the backup directory; run `--check` before retrying. Temporary staging directories are removed on normal completion and caught failures.

## Check

`--check` reports:

- `missing` or `drifted` skill copies;
- `differs from this checkout` when the checkout running the check has different skill sources from the ones installed (a newer or older checkout, or local edits);
- `source provenance unknown; reinstall to migrate` for manifests written before version 0.5.0, and a note naming skills kept from such an install by a partial reinstall;
- `skills not at the active <harness> location` and `routing not at the active <harness> location` when `CLAUDE_CONFIG_DIR`, `CODEX_HOME`, or `XDG_CONFIG_HOME` now points somewhere other than the recorded install, and `routing not recorded for workspace root` when a recorded workspace root lost its routing record;
- `routing missing`, `routing drifted`, `routing differs from this checkout`, and `routing unsafe`, including any Astrobyte marker other than the exact current ones;
- `inactive: shadowed` when a non-empty `AGENTS.override.md` in the Codex home hides the managed `AGENTS.md`.

Notes, which do not fail the check, cover an unrecorded routing marker at a known location, a pending migration decision, and a missing recorded source checkout. The installer and `--check` never clone. When the recorded checkout is gone, the check prints the `git clone` and `git checkout <commit>` commands to restore it at a destination you choose.

## What routing does and does not do

Routing is advisory. It puts the right pointer in front of the agent at the start of each session, and the agent still has to follow it. Nothing here blocks a `git push` mechanically. Hooks or server-side branch protection can add hard enforcement; they are outside this installer.

## Local, synced, and cloud

- Cursor's local rule applies only to the desktop app on this machine.
- Cursor personal skill sync copies `~/.cursor/skills` to Cloud Agents. It does not copy `~/.cursor/rules` or any `AGENTS.md`. For Cloud Agents, paste the body of `templates/routing.md` into a User Rule in Cursor's Customize → Rules. Once that account rule loads locally too, remove the duplicate local rule with `--remove-routing --harnesses cursor`.
- Codex, OpenCode, and Claude Code read their global files on this machine only.
- Hermes has no always-loaded routing location yet. Its adapter must define and verify one before the installer supports it.

## Troubleshooting

- The agent skipped the review gate: run `--check`. Confirm the routing file exists and is not shadowed, then start a new session. Harnesses read these files at session start.
- Codex ignores the block: look for `AGENTS.override.md` in the Codex home, and confirm `CODEX_HOME` matches the home you installed into.
- Claude Code ignores a project `AGENTS.md`: look for a `CLAUDE.md` or `CLAUDE.local.md` on the project path, and check the Claude Code version. Before 2.1.280, `/memory` omits an `AGENTS.md` that Claude read directly, so test with an instruction only that file contains.
- Claude Code in a Docker Sandbox reports no Astrobyte routing: follow [Docker Sandboxes](docker-sandboxes.md). Its last step is the check.
- The installer stopped on a marker error: fix the markers by hand, or move the block out of the code fence, then rerun.
- A target is a symbolic link: point the link's target at the routing text yourself, or replace the link with a regular file and rerun.
