# Quick install with the shared profile

Install the committed Astrobyte baseline unless the user requests personalization. Ordinary tasks use installed runtime skills. Adoption manages installation or requested differences and needs the source checkout.

## Install the baseline

1. Reuse a readable source checkout, or clone the repository supplied by the user outside an unrelated application repository. The original source is `https://github.com/TheAstroByte/astrobyte-agent-skills`. Use existing Git authentication. Report access failures without exposing credentials.
2. Read that checkout's `AGENTS.md`. Resolve the requested agent products from the user instruction or detection. Ask only if the target is unresolved.
3. From that checkout, run:

```bash
python3 scripts/install.py --quick --harnesses cursor
```

The installer previews changes and asks for confirmation. It copies real skill folders, backs up differing copies before replacement, and checks its manifest. Fresh installation selects `full`, currently 38 skills, with `durable` delivery and production playbooks available. The packaged baseline and agreement travel inside runtime skills. Quick installation creates no local agreement snapshot, personal repository, or machine registry. Existing explicit preferences and legacy documents remain supported.

Git attribution stays enabled when local Astrobyte configuration is absent. The helper resolves your own Git identity in the repository where a commit occurs. An unresolved identity blocks that commit until you provide your name and email. It never substitutes the baseline owner's identity.

Use `--dry-run` for a preview without writes. Use `--yes` when the exact installation scope is already approved. `--check` verifies the recorded installation and reports copies that differ from the checkout running it.

The same run installs a short always-loaded routing pointer for each selected harness, so substantial work loads `astrobyte-mode` and pushes wait for the review gate. Relay any routing approval the preview shows, such as replacing a hand-written Cursor rule; with `--yes`, approval requires `--routing`. Use `--skills-only` when the user declines routing. An installation made before 0.5.0 adds routing only with `--routing`. Read the source's `docs/routing.md` for locations, removal, and uninstall.

## Install selected skills

Honor an explicit subset. The native installer adds only hard dependencies:

```bash
python3 scripts/install.py --quick --harnesses cursor --skills astrobyte-mode
python3 scripts/install.py --quick --harnesses cursor --skills diagnosing-bugs
```

The first command installs the router's workflow and gates. The second installs a standalone leaf. Conditional specialists and suggestions stay unselected. A saved subset remains the update selection; use `--profile full` to return to the full catalog bundle. Quick updates preserve other installed skills.

The standard [skills CLI](https://github.com/vercel-labs/skills) can copy independent packages with Node.js and npm:

```bash
npx skills add TheAstroByte/astrobyte-agent-skills --skill unslop codebase-design diagnosing-bugs --agent cursor --global --copy
```

It does not resolve this repository's dependency catalog. Include a workflow's declared dependencies yourself or use the native installer. Runtime packages still contain their baseline resources. Check selected destinations and preserve or back up differing copies before replacement.

## Personalize only requested differences

Use `templates/preferences.json` to record reviewed reusable overrides. Apply them locally with `--preferences <file>`. Add `--portable-preferences` only after approval to include those rules inside synced runtime packages. `--local-preferences` removes managed portable copies later. Local-only preferences are a complete result; publication is separate. Read the source's `docs/profile-reference.md` for fields and precedence.

## Verify local and cloud use

Check the manifest, inspect packaged references, and invoke a selected skill in the target product. Report unobserved discovery as pending.

For Cursor, install locally, enable personal skill sync, then start a fresh Cloud Agent and invoke `/astrobyte-mode` for its task. Cursor transfers `~/.cursor/skills/`, including packaged resources, but not the local routing rule. Automatic routing in Cloud Agents needs the account User Rule described in the source's `docs/routing.md`. External local config remains local. The baseline requires no cloud checkout, clone, or adoption. See [Cursor skill sync](https://cursor.com/docs/skills#use-personal-skills-with-cloud-agents).

If personal sync is unavailable or you explicitly need cloud-local setup, use the approved installer in the environment's `install` command and verify a successful Build. Installing during an ordinary agent run does not prove future-run persistence. See [Cursor Builds](https://cursor.com/docs/cloud-agent/builds).
