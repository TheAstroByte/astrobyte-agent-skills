# Astrobyte agent skills

An opinionated skill stack for engineering, ML, GenAI, data work, and prototypes. Agents get project startup guidance, small verified changes, independent review, Git attribution, and specialist procedures. Humans can inspect the same plain-text instructions.

The default install is the full Astrobyte bundle with durable delivery. Keep those defaults or ask your agent to record a few local differences. No onboarding interview or personal repository is required.

## Install the default

Use Git and Python 3.12 or newer. The installer uses the Python standard library. Your local agent needs access to this source checkout and its personal skill directory. See [observed environments](docs/observed-environments.md) for what has actually been exercised.

Ask your agent:

```text
Read https://github.com/TheAstroByte/astrobyte-agent-skills/blob/main/docs/adoption.md and install the default Astrobyte skills for Cursor on this machine. Keep the defaults and show the plan before applying it.
```

Or run:

```bash
git clone https://github.com/TheAstroByte/astrobyte-agent-skills.git
cd astrobyte-agent-skills
python3 scripts/install.py --harnesses cursor
python3 scripts/install.py --check
```

Replace `cursor` with `codex`, `opencode`, `claude`, or `hermes`, or use a comma-separated list. The installer previews skill and routing changes, asks for confirmation, and backs up conflicting copies. `--dry-run` previews without writes. Your own Git identity stays in your execution environment.

Start a fresh agent session and ask it to use `astrobyte-mode` for a bounded task. Verify discovery in that host; copying files alone does not prove activation. Routing locations and capability limits are in [Routing](docs/routing.md) and the [host adapters](adapters/). Hermes currently needs explicit invocation.

## Keep the defaults, customize locally

The stack prefers tools such as uv, FastAPI, React, typed adapters, and direct code. These are overridable new-project preferences. Existing coherent project tooling takes priority.

Ask your agent:

```text
Keep the Astrobyte defaults, use branches, and prefer Django for new Python services. Show the differences and keep them local to this machine. Preserve existing project tooling.
```

Approved differences live outside this checkout in `~/.config/astrobyte-agent-skills/preferences.json`. Configure each machine separately. Export into synced skills only when you explicitly choose `--portable-preferences` after reviewing the file. See [customization and precedence](docs/profile-reference.md#customize-one-machine-with-your-agent).

Independent review strongly prefers Sol. If unavailable, the public policy permits an explicitly chosen independent read-only alternative; a strict local reviewer requirement stays binding. The [optional PR workflows](docs/pr-workflows.md), councils, and media specialists are absent from the default bundle.

## Check, update, or remove

From an updated source checkout:

```bash
python3 scripts/install.py --harnesses cursor --dry-run
python3 scripts/install.py --harnesses cursor
python3 scripts/install.py --check
```

When you want to remove one harness, run:

```bash
python3 scripts/install.py --uninstall --harnesses cursor
```

Removal previews and confirms, and keeps backups and local preferences. [Lifecycle commands](docs/routing.md#lifecycle) cover shared ownership, uninstalling everything, and purging state.

For a smaller workflow or standalone skill, use the [quick-install guide](skills/adopt-skill-stack/references/quick-install.md). Explicit subsets remain selected on later updates; `--profile full` restores the full bundle. [Adoption](docs/adoption.md) covers bootstrap, approved personalization, and Cursor local/cloud use. Hosted sync and automation have separate limits; follow the linked smoke checks before relying on them.

## Contribute or report a problem

The skills are provided as-is under the applicable licenses, without compatibility, maintenance, or response-time promises. Focused fixes and adapter extensions are welcome. Include a version, minimal reproduction, and observed evidence; redact private information.

Read [Contributing](CONTRIBUTING.md), the [code of conduct](CODE_OF_CONDUCT.md), and [security reporting](SECURITY.md). Source and adaptation notices are in [upstream maintenance](docs/upstreams.md), [third-party notices](THIRD_PARTY_NOTICES.md), and each package's `LICENSES.txt`.

Repository checks:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

Hosted GitHub Actions is currently disabled. Workflow source is prepared, but local results are the available verification; no hosted CI pass is implied. Only the repository owner merges PRs.
