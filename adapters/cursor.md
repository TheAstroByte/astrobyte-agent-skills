# Cursor adapter

Install real portable skill copies in `~/.cursor/skills/`. The installer also owns `~/.cursor/rules/astrobyte-routing.mdc`, an `alwaysApply` rule described in [Routing](../docs/routing.md). Keep installation-specific Cursor behavior in this adapter. Runtime consumers carry their own baseline, policy, references, and helpers.

## Cloud Agents

The default path is local installation followed by personal sync:

1. Install approved skill copies locally from a readable source checkout. A hosted agent cannot operate the laptop's filesystem.
2. Open Settings → Agents → Context and Tools, enable Sync Skills for Cloud Agents, and confirm.
3. Start a fresh Cloud Agent and invoke `/astrobyte-mode` for a representative task. Check its packaged baseline and references using the [smoke checklist](../docs/cursor-cloud-smoke.md).

Cursor copies `~/.cursor/skills/`; external local configuration stays local. Packaged baseline resources and explicitly exported preferences travel with the skills. See [Cursor personal sync](https://cursor.com/docs/skills#use-personal-skills-with-cloud-agents). Ordinary runtime work needs no source checkout or adoption.

`/adopt-skill-stack`, `/setup-astrobyte-skills`, and `/update-skill-stack` are explicit management actions. They need the full source and appropriate repository access in the environment performing them. A laptop's Git authentication does not establish the cloud integration's access.

For cloud-local setup without sync, put the approved quick installer command in the environment's `install` step, with a readable source checkout and environment credentials when required. Use `--yes` for the approved unattended scope. Verify a successful Build. Builds preserve disk state; ordinary task changes are not evidence of future-run persistence. See [Cursor Builds](https://cursor.com/docs/cloud-agent/builds).

Sync does not copy `~/.cursor/rules/`, so the installer's local routing rule never reaches Cloud Agents. Automatic routing there needs the account User Rule described in [Routing](../docs/routing.md#local-synced-and-cloud).

Report local installation, sync, and cloud observation separately. Settings and hosted checks remain pending until observed or confirmed. Keep personal skills outside application repositories unless project-wide distribution is requested.

## Review dispatch

Select the reviewer through the public preference or explicit local requirement in [`reviewer-dispatch.md`](../skills/astrobyte-review/references/reviewer-dispatch.md). Use a read-only Task on the selected available model at the harness default reasoning level. An unavailable model or Task tool leaves the push or pull request pending; follow that policy before proposing a different reviewer.
