---
name: adopt-skill-stack
description: Install the shared Astrobyte profile by default, or run an explicitly requested onboarding interview to personalize it. Use only when the user invokes $adopt-skill-stack or requests installation or adoption of this stack.
disable-model-invocation: true
metadata:
  opencode/autoinvoke: "false"
---

# Adopt this skill stack

Treat adoption as a transaction. Inspect first. Ask and normalize. Preview every persistent change. Apply only the approved plan.

## Choose the setup

Use **Quick install** with the committed Astrobyte baseline unless the user explicitly requests the onboarding interview or personalization. Do not ask an installation-versus-personalization question when they only want to get started. Honor an explicitly selected subset of skills instead of expanding it to the full profile.

- For quick install, read [quick-install.md](references/quick-install.md). Install the shared skill packages with their baseline and agreement, preserve existing explicit preferences, and verify discovery. Skip the remaining adoption sections; this path creates no new personal profile or private repository.
- For requested personalization, resolve the source below, then follow the local-delta procedure. Ask only about desired differences. The broader interview and profile-publication sections apply only when a separately maintained profile or repository was explicitly requested.

For ordinary personalization or an explicitly requested onboarding interview, use a local-only delta. Resolve the source before reading its templates. Read the source's `templates/preferences.json`, ask only about desired changes from the baseline, and generate a reviewed preferences JSON containing normalized differences. Preview the complete delta and working-agreement overrides. After approval, run `python3 scripts/install.py --quick --harnesses <products> --preferences <approved-file>`. Add `--portable-preferences` only when the operator approves exporting those reusable rules into synced skills. Use `--local-preferences` to remove managed portable copies later. This result requires no personal repository or machine registry. Use the full interview below only when the operator requests a separately maintained profile or repository.

When requested differences include extra capabilities, select the relevant cataloged optional packages in `overrides.optional_skills` and preview them with the personal rules. Omit that field to retain an existing selection. Explain that an explicit replacement, including an empty list, previews archiving previously selected managed optional packages that it removes. Preserve unrelated skills. Use the same preferences file with `--interview` or `--answers` only when the operator also requests that machine setup; a small personal change does not require a full interview. Preserve explicit machine defaults and show any higher-priority setting that overrides a requested personal value.

Configure only the requested harnesses. Recommend Sol for independent review when available. A different reviewer requires the operator's explicit choice; a model name does not establish access. Defer workflow-specific model setup until that workflow is actually invoked.

For requested PR completion, Sol-loop, council, or continuation personalization, read the source's `docs/pr-workflows.md`. Offer the optional `astrobyte-pr-workflows` package and only the requested reusable choices. Keep finish, council, and takeover explicit-only; both finish names leave work unmerged. Save no guessed council members during adoption. Select actual models on first council use and resolve missing repository review policy on first relevant PR task.

Applying one skill to a document is not installation of the requested selection. Report inaccessible source files as an access blocker rather than claiming setup is complete.

## Resolve the source

1. Check the current workspace and any source checkout named by the user for `config/repository.json`, `catalog.json`, `templates/preferences.json`, and `scripts/install.py`. An installed skill folder or attached `SKILL.md` is an entry point; adoption needs the complete repository.
2. If the source is missing, use the repository URL supplied by the user. For the original stack, use `https://github.com/TheAstroByte/astrobyte-agent-skills`. Reuse an existing checkout or clone into a separate workspace directory, subject to the environment's filesystem permissions. Keep the skills source outside an unrelated application repository.
3. If access fails, report the attempted repository and the access error without exposing credentials. For cloud management, resolve the connected integration's source read access or run installation in local Cursor and sync current skill packages. Ordinary cloud runtime needs only the synced packages. Cloud access to an application repository does not imply access to the skills repository. Instructions cannot grant repository access or operate the user's laptop from a hosted VM.
4. Read the source checkout's `AGENTS.md` and this skill there. Resolve repository paths from that checkout and skill references from its `skills/adopt-skill-stack/` directory. Read `adapters/cursor.md` when the requested setup includes Cursor Cloud Agents.

Continue only when the complete source is readable in the environment performing adoption. If access requires user action, return the exact repository and action needed to resume.

## Prepare

1. Locate the repository root containing `config/repository.json`, `catalog.json`, and `templates/operator-profile.json`.
2. Read [interview.md](references/interview.md) and the three templates under `templates/`.
3. Read `unslop` and apply it to every generated document. Read `docs/skill-stack-assessment.md` before recommending, removing, or replacing a skill.
4. Detect the current Git state and known agent products. Detection is evidence, not consent.
5. Ask permission before inspecting known skill directories, agent configuration, plugins, or representative projects. Do not scan the home directory broadly.
6. Keep answers in conversation until the operator approves a resumable local draft under the ignored `.astrobyte/` directory. Do not commit raw interview answers.

Preparation is complete when the operator knows what the interview will inspect and no persistent state has changed.

## Interview

Ask one question at a time unless the operator requests a batch. Skip a question only when repository evidence or an earlier answer resolves it. Mark skipped and unresolved items in the final preview.

1. Establish the operator's work, experience, languages, project types, and desired explanation level.
2. Ask what good code means to the operator, what agents do that frustrates them, what must never change without approval, and what proof they expect. Convert the answers into specific rules and ask the operator to approve the normalized rules.
3. Resolve autonomy controls and delivery modes. Keep personal defaults separate from machine and project overrides.
4. Resolve stack preferences only where the operator has a stable view. Record `ask-per-project` elsewhere.
5. Resolve repository identity, machine synchronization, agent products, Git isolation, external actions, unattended work, budgets, and update policy.
6. Ask whether to run existing-setup migration. The default is yes, but the operator can skip it with a recorded reason.
7. Ask before browsing for additional skills. If approved, follow [skill-discovery.md](references/skill-discovery.md).
8. Offer the calibration in [calibration.md](references/calibration.md). It is optional and strongly recommended.

The interview is complete when every consequential preference is chosen, delegated to project startup, or visibly unresolved.

## Preview

Generate, but do not yet persist, these artifacts:

- `profiles/<handle>/profile.json`
- `profiles/<handle>/working-agreement.md`
- `profiles/<handle>/machines.json`
- the repository metadata and README changes
- the selected catalog and profile changes
- the machine installation answer file
- the GitHub, Git, filesystem, migration, and installation actions

Show the complete working agreement, the repository diff, any skill provenance and license changes, conflicts with existing setup, secrets or personal data excluded from Git, and every external action. The normalized agreement is the durable record. Discard raw answers.

Ask for one final approval. If the operator previously opted into incremental application, show and approve each section before applying it.

## Apply

Read [repository-and-install.md](references/repository-and-install.md). Follow the approved plan in recoverable steps.

1. Create a short-lived setup branch or worktree.
2. Write the approved personal profile and sanitized machine registry. Keep credentials, hostnames, usernames, serial identifiers, absolute paths, and local endpoints outside Git.
3. Apply approved migration decisions. Back up every replacement. Preserve unrelated skills and agent configuration.
4. Validate the repository and run its tests.
5. When publication was explicitly selected, create the chosen independent private repository. Make it `origin` and retain the source repository as read-only `upstream`. Use a GitHub fork only when the operator knowingly selects that alternative. Local-only adoption ends with approved preferences and installation.
6. For approved publication, push the setup branch, open the initial pull request, wait for checks, and merge only after operator approval. Offer direct-to-main when selected.
7. Run `python3 scripts/install.py --operator <handle> --interview` and present its machine plan before installation.
8. Verify skill discovery in each selected agent product. For an unknown product, verify current official documentation and add a small adapter only after approval.

Adoption is complete when the approved baseline or personalization is installed, validation passes, and selected agent products discover the entry skills. For explicitly chosen publication, also verify repository ownership and update remotes. Repository creation is not required for local-only personalization.

Do not infer external authority from an autonomy preset. Agent permissions, repository access, and user approval remain binding.
