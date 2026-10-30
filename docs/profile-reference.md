# Operator profile reference

Runtime packages include the shared baseline. Explicit personal, machine, and project preferences can override it. A current user instruction always has priority.

Ordinary installation inherits the committed default operator profile, currently `astrobyte`, without an onboarding interview. That baseline selects the `full` bundle with `durable` delivery and production playbooks available. Personalization is the optional process of recording different preferences in another profile. Quick installation preserves existing explicit local settings and profile documents; it does not import the owner's machine registry or human Git author.

| Layer | Location | Contains | Must exclude |
|---|---|---|---|
| Personal | `profiles/<handle>/profile.json` and `working-agreement.md` | Normalized code standards, autonomy, delivery defaults, repository policy, update policy, and skill choices | Raw interview answers and secrets |
| Machine | `~/.config/astrobyte-agent-skills` | Agent products, local paths, compute, tools, budgets, effective delivery mode, and installation manifest, including routing state | Nothing that needs cross-machine synchronization |
| Project | `.astrobyte/config.json` | Project maturity, stack, deployment, data sensitivity, and explicit exceptions | Secrets, credentials, and transient local endpoints |

The installation manifest uses schema version 3. It records each skill copy's installed hash, raw source hash, and owning harnesses; the source checkout's path, URL, version, and commit; the routing mode; each routing file or block; removed harnesses; and workspace roots. [Routing](routing.md) describes how installs, checks, and removals use these records.

## Personalization deltas

New personalization uses `templates/preferences.json`, with schema version 1. `baseline.handle` is `astrobyte`. `baseline.repository_version` records the version used when approving the differences; omitted fields inherit the currently installed baseline. It does not pin an older baseline.

`overrides.defaults` accepts reusable policy fields, including delivery, autonomy, communication, explanation, Git workflow, tracker, update policy, CI validation, worker limit, unattended work, external actions, and experiment budget. `overrides.skill_profile` selects a catalog bundle. `overrides.review.instructions` and `working_agreement` contain approved normalized differences. `overrides.git_identity` accepts only mode, trailer key, and verification policy. Human identity, paths, credentials, hostnames, and machine registries are excluded.

`overrides.optional_skills` selects additional cataloged optional packages. Omit it to preserve the machine's existing selection; an explicit list replaces that selection for the approved installation. An empty list selects none. The preview includes archiving previously selected managed optional packages removed by that explicit list. Unrelated installed skills remain untouched. Unknown names and packages outside the optional tier are rejected before writes.

`overrides.pr_workflows` holds reusable optional PR-workflow choices: `review_method` is `baseline` or `sol-loop`, `council_round_limit` is an integer from 1 to 20, and `t3` is a boolean. Omitted fields inherit their configured values. These choices do not grant authority, invoke a command, configure model access, or install a package by themselves. Exact model routes stay local.

The [optional PR workflows](pr-workflows.md) package supplies the Sol-loop method and explicit commands. Select the package alongside `review_method: sol-loop`; requesting a method whose package is missing leaves that review pending. Selecting the method does not invoke council or another finish operation.

Apply a reviewed file with `python3 scripts/install.py --quick --harnesses cursor --preferences <file>`. The installer stores it locally beside `config.json`. Local-only personalization is a complete result. Repository creation and publication are separate choices.

The same preferences file can accompany an explicitly requested `--interview` or reviewed `--answers` file. Personal defaults seed the plan; explicit machine answers retain precedence. Optional packages selected in the preferences file replace the saved optional selection. All paths share the same validation and installation plan, without requiring a full interview for a small personal change.

Add `--portable-preferences` after reviewing the entire file for private information. The installer includes it inside the selected runtime consumers, including the optional PR-workflow package when selected, so skill sync transfers it. Free-text rules still need human review for secrets. Later installs preserve this export choice. `--local-preferences` removes the managed portable copies while retaining local preferences.

New quick installs record inherited machine values separately in `baseline_inheritance.values`. Unchanged inherited values follow baseline updates. Edited values remain explicit. Older full profiles and configurations retain their behavior until you explicitly migrate them to deltas. The runtime [configuration contract](../skills/astrobyte-mode/references/configuration.md) defines precedence.

## Customize one machine with your agent

Keep personal differences in `~/.config/astrobyte-agent-skills/preferences.json`, outside the source checkout. No repository `.gitignore` entry is needed for that location. The default install keeps them local; portable export requires the explicit choice described above. Configure each machine separately, or copy only an approved preferences file to another machine and apply it there. Machine state and credentials stay on their own machine.

Ask your agent:

```text
Keep the Astrobyte defaults, prefer Django for new Python services, and require Sol for my reviews on this machine. Show the differences and keep them local. Preserve existing project tooling.
```

The agent previews the requested differences, checks conflicts with existing machine and project settings, and applies the approved file through the native installer. It updates local preferences rather than editing shipped skills or the shared profile. A normalized example is:

```json
{
  "schema_version": 1,
  "baseline": {"handle": "astrobyte", "repository_version": "0.5.0"},
  "working_agreement": "Prefer Django for new Python services. Preserve coherent existing project tooling.",
  "overrides": {
    "review": {
      "instructions": "Require the newest offered GPT Sol reviewer at the harness default reasoning level. If unavailable, keep the independent review gate pending; do not substitute another model."
    }
  }
}
```

The public baseline strongly recommends and prefers Sol. This example makes it a local requirement. Without a strict requirement, unavailable Sol prompts an explicit choice of another available independent read-only reviewer. Missing independent review still leaves publication pending.

Verify the effective policy by running `python3 <installed-skill>/scripts/runtime_config.py --project <project-root>` from `astrobyte-mode`, `astrobyte-review`, or `astrobyte-project-startup`. Inspect the returned sources and ordered agreement layers, then check that startup and review apply those rules. Project evidence and current task instructions still take precedence. Existing legacy agreements remain explicit; keep them until you approve migration of their rules.

## Legacy personal profile

`profile.json` uses schema version 1.

| Field | Values |
|---|---|
| `identity_mode` | `handle` or `full-rename` |
| `skill_profile` | `core`, `builder`, or `full` |
| `defaults.autonomy_preset` | `exact-scope`, `guided-implementation`, `bounded-autonomy`, or `prototype-sprint` |
| `defaults.communication_style` | `strictly-comply`, `collaborative-challenge`, or `actively-challenge` |
| `defaults.explanation_level` | `expert-concise`, `collaborative`, or `guided-teaching` |
| `defaults.delivery_mode` | `explore`, `prototype`, `durable`, or `production` |
| `defaults.machine_delivery_policy` | `inherit-personal-default`, `ask-every-install`, or `ask-every-project` |
| `defaults.skill_update_policy` | `manual-only`, `notify`, `manual-reviewed`, `auto-reviewed-pr`, or `auto-merge-gated` |
| `repository.publication` | `independent-copy`, `github-fork`, or `local-only` |
| `git_identity.mode` | `dual-attribution`, `agent-only`, `human-with-agent-trailer`, or `disabled` |

`skills.required` must include `unslop`. Each required skill must appear in the selected catalog profile.

## Optional machine skills

`optional_skills` is a list of cataloged optional skill names, defaulting to `[]`. The installer previews and installs the selected skills alongside the machine's `core`, `builder`, or `full` profile. A reviewed personal delta can carry the selection across machines; the canonical shared profile remains unchanged. Codex and OpenCode share a skill destination, so a selected skill is discoverable by both if both are active. Explicitly removing a selected optional package previews archiving its managed copy. Ordinary quick updates preserve extra copies and unrelated local skills stay untouched. Selecting a skill does not install its external application, MCP server, or client configuration. Use `--dry-run` to review the plan before applying it.

## Machine registry

`machines.json` contains one or more entries. Each entry has a lowercase kebab-case alias, a delivery default or `ask`, a production-capable flag, allowed delivery modes, broad capabilities, and setup status.

The registry is a sanitized synchronization record. The installer writes detected host and operating-system details only to local configuration.

`production_capable` records whether the machine can perform approved production operations. It does not prevent another machine from applying production-level code standards without production credentials or access.

## Git identity

The committed profile stores the attribution mode, trailer key, and reusable identities for each agent product. An explicit machine config can store the human Git identity; otherwise the helper resolves the current environment's Git identity. Dual attribution records the human as author and the active agent product as committer, then adds an `Agent` trailer.

The commit helper applies identity to one Git command and leaves normal Git configuration unchanged. GitHub push and pull-request actors come from the authenticated account or GitHub App, not commit identity.

## Working agreement

The Markdown working agreement is the readable policy agents apply. It records normalized rules, not the adopter's raw interview wording. It covers scope, autonomy, code quality, dependencies, delivery modes, verification, external actions, unattended work, Git, and communication.
