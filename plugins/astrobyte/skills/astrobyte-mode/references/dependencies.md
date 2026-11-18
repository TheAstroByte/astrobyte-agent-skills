# Missing skill dependencies

The source catalog distinguishes hard dependencies from conditional specialists and suggestions. Hard dependencies ship with the workflow that needs them. Conditional specialists and suggestions are separate choices.

## Find a named skill

Resolve a named skill in this order. Stop at the first match.

1. **Sibling.** Read `../<skill-name>/SKILL.md` resolved from this skill's directory. This works for native installs and for skills in the same plugin, including skills the harness does not list.
2. **Installed elsewhere.** Use the skill when the session's skill list offers it, including under a plugin prefix such as `astrobyte-web:frontend-design`. Invoke it through the harness's skill tool or read its listed path. Do not search plugin caches or other directories for it.
3. **Not installed.** Report it as described below.

## Report what is missing

When a hard dependency is missing, the installation is incomplete. Report the missing skill and do not substitute a weaker gate.

- Claude Code plugin: update or reinstall the package, for example `claude plugin update astrobyte@<marketplace>`, then restart the session.
- Native install: offer the native installation with `--skills <workflow>`, preserving the current profile or subset.

When a conditional specialist is needed but missing, name it only when its branch applies, then name where it comes from:

- Claude Code plugin: the optional package that provides it. Frontend and API specialists are in `astrobyte-web`; writing and research in `astrobyte-writing`; testing, debugging, security, and operations in `astrobyte-reliability`; recall, handoff, and PR feedback in `astrobyte-continuity`.
- Native install: add it to the current selection with `--skills <current-selection>,<specialist>` rather than replacing the selection.

Reinstalling a workflow does not select conditional specialists. Suggestions are related guidance, not execution requirements. Installation remains an explicit management action; a runtime task must not clone or configure the source just to read baseline policy.

## Known conditional branches

`astrobyte-architect` uses `api-and-interface-design` for public HTTP or GraphQL contracts. Core covers other architecture tasks. Review still requires an available independent reviewer, and browser testing still requires an actual browser tool.

The security skill uses `diagnosing-bugs` for privacy-incident diagnosis and reports its absence if unavailable. Its observability reference is related guidance rather than an unconditional execution dependency. Other standalone specialists include local steps for diagnosis, change splitting, and completion checks so those branches can run without a workflow bundle.

Standard third-party skill installers may copy only the named skill and do not necessarily understand this catalog's dependency closure. Install the declared workflow dependencies explicitly, or use the native installer from a readable source checkout. Standalone leaf skills with no dependencies need no workflow bundle.
