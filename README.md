# Astrobyte agent skills

A portable skill stack for engineering, ML, GenAI, data science, APIs, backend systems, full-stack prototypes, and long-running agent work.

Start with the shared Astrobyte profile and its full skill stack. The installed runtime packages carry their defaults and working agreement. Personalization is optional and records only your differences from that baseline.

## Quick install

Install the shared profile without the personal interview or repository creation. Send your agent:

```text
Read https://github.com/TheAstroByte/astrobyte-agent-skills/blob/main/docs/adoption.md and install the default Astrobyte profile for Cursor without onboarding.
```

Or run this from the cloned source repository:

```bash
python3 scripts/install.py --quick --harnesses cursor
```

This inherits `profiles/astrobyte/profile.json`: the `full` bundle, its working agreement, and shared preferences. The baseline currently defaults to `durable` delivery, with production playbooks available. It preserves existing explicit local preferences and uses your machine's own Git identity. See [Quick install](skills/adopt-skill-stack/references/quick-install.md) for explicit subsets and cloud use.

The installer also adds a short always-loaded routing pointer for each selected harness, so substantial work loads `astrobyte-mode` and pushes wait for the review gate. [Routing](docs/routing.md) covers where it goes, how to opt out, and how to remove or uninstall everything.

## Use locally and in Cloud Agents

After local installation, enable Cursor personal skill sync and start a fresh Cloud Agent. Use `/astrobyte-mode` for ordinary work. Its packaged defaults require no source checkout or external machine config. `/adopt-skill-stack` manages installation or requested personalization. See [local and cloud setup](docs/adoption.md#cursor-local-and-cloud-setup) and the [hosted smoke checklist](docs/cursor-cloud-smoke.md).

Install a smaller workflow or an independent leaf from the source checkout:

```bash
python3 scripts/install.py --quick --harnesses cursor --skills astrobyte-mode
python3 scripts/install.py --quick --harnesses cursor --skills diagnosing-bugs
```

The native installer adds hard dependencies only. A saved subset stays selected for later quick updates. Use `--profile full` to return to the full bundle.

## Personalize the baseline

Ask your agent to record requested differences, or explicitly request an onboarding interview. Local-only personalization is a complete result. Start from `templates/preferences.json`, review the normalized delta, then apply it:

```bash
python3 scripts/install.py --quick --harnesses cursor --preferences approved-preferences.json
```

Add `--portable-preferences` only after approval to carry those reusable rules inside synced runtime packages. Use `--local-preferences` to remove exported copies later. Omitted fields inherit newer baseline values. Explicit overrides and legacy full profiles remain supported. A separate profile repository and publication are optional chosen actions.

Personalization can also select the [optional PR workflows](docs/pr-workflows.md) for explicit finish, Sol-loop, council, and continuation commands. Both finish commands leave work unmerged. Council models are chosen on first use in the current system. This package is absent from the default bundles; normal installation and review behavior stay unchanged.

Installation and personalization run from a checkout of this repository. Ordinary synced runtime work does not need one. If your agent does not load the adoption entry point, run `python3 scripts/bootstrap.py` from the source checkout; it installs the entry skill and `unslop`, then you can invoke `/adopt-skill-stack` or `$adopt-skill-stack`.

See [Adopt the skill stack](docs/adoption.md) for the full operator procedure. See [Operator profile reference](docs/profile-reference.md) for committed and local configuration boundaries.

## Install an existing profile on a machine

Astrobyte uses the committed `profiles/astrobyte` profile:

```bash
python3 scripts/install.py --operator astrobyte
```

The installer detects Codex, OpenCode, Cursor, Claude Code, and Hermes, then previews the baseline installation and asks for confirmation. Add `--harnesses cursor` to select the target directly. Use `--interview` only when you want to configure machine-specific differences, optional skills, or attribution interactively. No files are copied until the plan is confirmed.

Agent-created commits use the configured Git attribution policy: your machine's human Git author, the active agent product as committer, and an `Agent` trailer. Manual commits keep the normal human identity. The helper changes identity for one commit and audits unpublished commits before a push.

Preview or check an installation:

```bash
python3 scripts/install.py --operator astrobyte --dry-run
python3 scripts/install.py --check
```

`--check` also reports skill copies that differ from the checkout running it and routing that another file shadows. Remove routing, uninstall one harness, uninstall everything, or purge local state with the commands in [Routing](docs/routing.md#lifecycle).

Machine answers and local deltas live in `~/.config/astrobyte-agent-skills`. Runtime policy lives inside the consumer skills. Fresh quick installs use those packaged resources; existing legacy local documents remain supported.

## Delivery modes

| Mode | Contract |
|---|---|
| `explore` | Answer a question with reproducible evidence. The implementation can be disposable. |
| `prototype` | Produce a working vertical slice with minimal infrastructure and mark shortcuts. |
| `durable` | Use maintainable boundaries, dependency checks, typing, documentation, and proportionate tests. |
| `production` | Add security, observability, migrations, rollout, and rollback to the durable standard. |

## Skill profiles

| Profile | Purpose |
|---|---|
| `core` | Portable workflow, research, diagnosis, handoff, verification, review, adoption, and updates. |
| `builder` | Core plus API, frontend, browser, security, source, TypeScript, and writing specialists. Recommended for daily work. |
| `full` | Builder plus CI/CD, migrations, observability, performance, and shipping. |

`builder` and `full` include Anthropic's `frontend-design` for visual direction alongside `frontend-ui-engineering` for implementation. Astrobyte routes new interfaces and deliberate redesigns through design, implementation, and browser verification. Existing product identity and design tokens guide additions to established UIs. Routine repairs keep their requested scope. The standalone design package retains its Apache-2.0 license.

`unslop` is required in every profile. Optional specialists are absent from the default profiles. `davinci-resolve-reel-editing` asks about a reel's purpose and media before Codex plans an edit; it does not install Resolve or an MCP server. Select it at the installation interview or include `"optional_skills": ["davinci-resolve-reel-editing"]` in a reviewed answer file. Codex and OpenCode share `~/.agents/skills`, so both can discover a selected skill. Use the interview or a reviewed answer file to remove a previous optional selection and preview archiving its managed copy; quick installation preserves extra installed skills. Live editing requires a separately configured and tested Resolve connection.

Adoption explains and selects other behavioral skills. `docs/skill-stack-assessment.md` records the dated review of the original catalog and upstream skill collections. New recommendations require primary evidence and independent public feedback; state when meaningful feedback is unavailable.

## Start a project

Invoke `astrobyte-project-startup` before substantial greenfield implementation or when material stack choices remain unresolved. It inspects the repository first, preserves coherent existing tooling, asks only consequential questions, and records confirmed choices in `.astrobyte/config.json`.

The greenfield preferences include uv, FastAPI, React and TypeScript, pnpm, PostgreSQL, Qdrant or pgvector by workload, typed adapters for hosted or local OpenAI-compatible models, MLflow, optional Inspect AI and self-hosted Opik, and Docker. They are decision defaults, not a mandatory template.

## Update an adopted stack

Invoke `$update-skill-stack` or say "Update my skill stack." The agent compares the current base with `upstream`, preserves personal profiles and custom skills, shows behavioral and license changes, validates in an isolated branch or worktree, and asks before merging or reinstalling.

Vendored upstream sources remain pinned. Read `docs/upstreams.md` before refreshing one.

## Agent product paths

- Codex and OpenCode share `~/.agents/skills`.
- Cursor uses `~/.cursor/skills`.
- Claude Code uses `~/.claude/skills`.
- Hermes uses `~/.hermes/skills/astrobyte` or a configured external directory.

Routing pointers and their environment overrides are listed in [Routing](docs/routing.md#where-routing-goes). See `adapters/` before changing product-specific behavior. Unknown products require an adapter based on current official documentation and a real discovery check.

## Verify the repository

For changes to this repository, follow [Contributing](CONTRIBUTING.md). Submit a feature-branch PR and leave merging to the repository owner.

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

GitHub Actions runs the same checks by default. An adopter can disable CI during the reviewed adoption plan.
