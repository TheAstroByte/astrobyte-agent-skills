# Install or adopt the skill stack

Start with the shared Astrobyte baseline. Personalization records only requested differences. Local-only use is a complete result; an onboarding interview and a separate repository are optional.

## Instructions for the agent

For installation, read [quick-install.md](../skills/adopt-skill-stack/references/quick-install.md) and follow the requested scope. Use the default profile unless the user selects skills or another bundle. Resolve source access only for installation, updates, or requested personalization.

For ordinary work, use the installed runtime skill and its packaged defaults. A missing optional machine config does not require adoption. Report an explicitly requested missing or malformed configuration as an error.

For personalization, read the source's `AGENTS.md` and `skills/adopt-skill-stack/SKILL.md`. Start with the baseline, ask about desired differences, preview normalized rules, and apply an approved delta. Run a broader interview only when requested. Repository publication is a separate explicit choice.

## Install locally without onboarding

Send this to your local agent:

```text
Read https://github.com/TheAstroByte/astrobyte-agent-skills/blob/main/docs/adoption.md and install the default Astrobyte skills for Cursor on my laptop, without onboarding, for use locally and through personal skill sync in Cloud Agents.
```

Or, from a readable source checkout:

```bash
python3 scripts/install.py --quick --harnesses cursor
```

The environment performing installation needs a checkout of this repository; Git reports any access failure. The command previews changes and asks before applying them. It defaults to the full bundle with durable delivery and production playbooks available. Existing explicit preferences remain supported, and Git identity comes from your execution environment.

The same run installs the always-loaded routing pointer for each selected harness. Use `--skills-only` to skip it. See [Routing](routing.md) for locations, approvals, and removal.

For a smaller workflow, use `--skills astrobyte-mode`. For a standalone leaf, use `--skills diagnosing-bugs`. Hard dependencies are included; conditional specialists are requested only when needed. See the [quick-install guide](../skills/adopt-skill-stack/references/quick-install.md) for updates and third-party installers.

## Bootstrap the entry point

If your agent cannot load the adoption entry point, run `python3 scripts/bootstrap.py --harnesses cursor` from the source checkout. Bootstrap previews and confirms the installation of `adopt-skill-stack` and `unslop` only. It records their ownership in the same manifest as a regular install, so `python3 scripts/install.py --check` and the [uninstall commands](routing.md#lifecycle) work immediately.

Bootstrap preserves existing managed skills, routing, and explicit install choices. It adds no routing itself. A fresh bootstrap does not save its two skills as your permanent selection; later adoption still installs the full default bundle and routing.

## Cursor local and cloud setup

1. Install current skill copies in `~/.cursor/skills/` using local Cursor or a terminal with source access.
2. Enable personal skill sync and start a fresh Cloud Agent. Invoke `/astrobyte-mode` with the task you want it to perform.

Runtime defaults, the agreement, review dispatch guidance, and Git policy are packaged inside the consumer skills. A cloud task can use them without the skills source or `~/.config/astrobyte-agent-skills/`. Sync transfers only Cursor's personal skill directory, not the local routing rule. Add the routing User Rule described in [Routing](routing.md#local-synced-and-cloud) so Cloud Agents load `astrobyte-mode` without an explicit invocation. Follow the [Cursor adapter](../adapters/cursor.md#cloud-agents) and [official sync instructions](https://cursor.com/docs/skills#use-personal-skills-with-cloud-agents).

Your laptop's repository access matters for local installation. Cloud integration access matters only when the cloud environment itself must clone, install, update, or personalize the stack. An attached `SKILL.md` alone does not contain the management tooling.

If you choose cloud installation instead of sync, give the connected integration source read access and run the approved quick command in its environment's `install` step. Verify a successful Build before relying on it for future agents. See [Cursor Builds](https://cursor.com/docs/cloud-agent/builds).

## Personalize the baseline

Say `Run the onboarding interview to record my differences from the Astrobyte baseline, keeping them local` or ask for specific changes directly. The agent previews the requested delta and normalized prose before applying them.

```bash
python3 scripts/install.py --quick --harnesses cursor --preferences approved-preferences.json
```

This writes local preferences only. To use the approved differences in Cloud Agents, review the complete file for private information, then add `--portable-preferences`. To return to local-only differences, use `--local-preferences`. Omitted values inherit later baseline updates; explicit overrides remain. See the [profile reference](profile-reference.md) for the schema and legacy compatibility.

Machine facts, human Git identity, credentials, and paths stay local. Free-text rules still require review before export. If you request an independently maintained profile or repository, adoption offers that broader branch and previews its GitHub actions separately.

Requested personalization can also select optional packages through `overrides.optional_skills`. Ask only about the desired additions and preview them with the personal rules in one plan. The same reviewed delta can be used with an explicitly requested machine interview or answer file. An ordinary default installation adds no optional-package questions.

The [optional PR workflows](pr-workflows.md) provide explicit finish, Sol-loop, council, and continuation operations. Select them only when requested during personalization. Council asks for actual model choices on first use on the current system; adoption can save its round limit and optional T3 preference without pretending provider access has been configured.

Configure only the requested harnesses. One harness is enough for ordinary use; adding another preserves the same portable personal rules and records its local destinations. Reviewer models are separate from installed harnesses. Strongly recommend Sol wherever available, and record an alternative only when the operator explicitly selects it. Installation does not establish access to a provider or start a council.

## Update later

Run the installer from an updated source checkout to refresh installed copies and routing. It preserves approved overrides and existing explicit preferences, previews conflicts, and backs up replacements. Re-sync current Cursor copies afterward. Use `--check` for drift, differences from the current checkout, and shadowed routing. An installation made before 0.5.0 needs `--routing` once to add routing.

Invoke `$update-skill-stack` for a reviewed upstream refresh of an adopted source repository. Management remains explicit; ordinary tasks do not update or personalize the stack automatically.

## Verify the cloud boundary

The repository's automated checks run isolated installed helpers with no source imports or Astrobyte config. The real hosted check is separate. Follow [Cursor cloud smoke check](cursor-cloud-smoke.md), and record discovery and representative task behavior before claiming your cloud setup is verified.
