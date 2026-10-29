# Implement portable skill defaults

Status: implementation authorized on 7 October 2026. All six implementation checkpoints are complete. Hosted Cursor observation remains pending.

The operator approved implementation on 7 October 2026. Preserve the existing skill quality requirements. Performance parity experiments are explicitly excluded.

## Resume from this checkpoint

Implementation is on `feat/portable-skill-runtime` in [PR #19](https://github.com/TheAstroByte/astrobyte-agent-skills/pull/19). The original planning branch remains available. PR #18 merged as `e7d09b3` before implementation began.

1. Read this plan and `AGENTS.md`.
2. Inspect Git status, the branch history, and PR #19's current state before changing anything.
3. Check account usage limits and preserve verified commits. Avoid history rewrites and user-machine installation without the requested scope.
4. If #19 is open, confirm its final head, CI, and review evidence before completing the previously authorized push and merge.
5. If #19 is merged, implementation is complete. The remaining hosted observation is in `docs/cursor-cloud-smoke.md`. Run it only in an available authorized Cursor environment and record actual observations.

Do not infer hosted verification from local tests. Use commits and recorded command results to recover the implementation state.

## Outcome and boundaries

An installed and synced runtime selection works without a source checkout, network access, or Astrobyte machine configuration. It uses the shared Astrobyte baseline. Personalization occurs only when explicitly requested and records differences from that baseline.

Keep the current full selection as the default. Its current delivery default is `durable`; production playbooks remain available. Preserve routing, independent review, Git attribution, real-artifact verification, permission boundaries, proportionate tests, and progressive resource loading.

Source access can remain necessary for installing, updating, or authoring packages. Ordinary execution must not clone the source repository or run adoption merely to read defaults.

Exclude performance benchmarks, broad prompt rewrites, specialist removal, upstream refreshes, stack preference changes, and a new plugin marketplace. Keep the current 38-skill full selection during this change. Separate management behavior logically without introducing a new default bundle.

## Evidence to preserve

- Cursor sync transfers only `~/.cursor/skills/`. Resources inside those folders travel with them. External configuration and source checkouts do not. [Cursor skills](https://cursor.com/docs/skills).
- Cursor's `install` command runs during a Build. Successful Builds preserve disk state for later agents. An ordinary run's changes do not establish that persistence. [Cursor Builds](https://cursor.com/docs/cloud-agent/builds).
- `astrobyte-mode` reads external machine config and its adjacent agreement, with no explicit packaged baseline fallback.
- `astrobyte-review` depends on that agreement for reviewer preference.
- The packaged Git identity helper raises `FileNotFoundError` for missing external config before performing Git operations.
- `astrobyte-project-startup` already packages its defaults in references. Reuse that approach.
- All 40 skills passed validation at the audit checkpoint. Relative Markdown links stay inside their owning skills, but operational dependencies in prose remain unchecked.
- Core has 25 skills, builder 33, and full 38. Cross-skill references need classification rather than automatic treatment as hard dependencies.

## Configuration contract

Use explicit task instructions first, then project configuration and coherent repository evidence, then explicit personal or machine overrides, then the packaged baseline. Preserve the existing precedence between personal and machine settings. Define that order once and reference it from consumers.

Keep reusable policy separate from machine facts. Portable policy includes delivery, communication, review preference, attribution policy, and budgets. Resolve human identity, available tools and models, credentials, permissions, local paths, and host facts in the actual execution environment.

Use `profiles/astrobyte/profile.json` and its working agreement as the canonical baseline source. Generate versioned resources for the router, review, and attribution consumers. Each consumer must remain usable independently. Do not add a mandatory global config directory or a sibling package just to read its defaults.

Generated copies are acceptable when validation checks consistency. Preserve the full working agreement's meaning. Package focused policy extracts for independent consumers without introducing a second editing source.

Store personalization as explicit changed fields plus a baseline identity and version. An absent override inherits future baseline values. A chosen override survives updates. Existing complete personal profiles and machine configs remain supported. When inheritance intent cannot be recovered from legacy files, preserve their effective behavior and offer explicit migration rather than guessing.

## Implementation checkpoints

### C1. Generate portable baseline resources

Scope: `scripts/profile.py`, a focused generation module if needed, generated references under the three consumers, `scripts/validate.py`, and focused tests.

- Define the portable resource schema, baseline version, provenance, and generation command.
- Package the router's baseline and agreement, review policy, and Git attribution policy from canonical sources.
- Exclude machine registries, hostnames, paths, human author identity, secrets, and unverified capability claims.
- Make generation deterministic. Make validation detect missing or stale generated resources.

Done: generation followed by validation succeeds, repeating generation produces no diff, and an isolated copy contains the required baseline resources. Existing runtime behavior remains compatible at this checkpoint.

### C2. Activate packaged defaults in routing and review

Scope: `skills/astrobyte-mode/`, `skills/astrobyte-review/`, runtime configuration resolution, relevant tests, and `docs/architecture.md`.

- Load the packaged baseline when machine config or agreement is absent. Apply explicit overrides using the configuration contract.
- Keep references and playbooks loaded only when needed.
- Put necessary runtime harness mappings inside the consumer package. Leave installation-specific adapters in the source repository.
- Resolve the baseline reviewer preference against offered models. If the configured model or delegation tool is unavailable, report the limitation and leave the push or pull request waiting. Never select a substitute reviewer or skip the required gate.
- Keep independent invocation of review usable without the router or source checkout.

Done: an isolated installed selection can resolve baseline delivery and review policy with no machine config or network. Override fixtures retain expected precedence. Runtime instructions no longer require source-only files for these paths.

### C3. Make Git attribution independent of setup

Scope: `skills/astrobyte-git-identity/` and its regression tests.

- Use packaged attribution policy when machine config is absent. Honor explicit existing policy overrides.
- Resolve the human identity from Git's effective configuration in the current repository and environment, including conditional configuration.
- Preserve amend authorship, product attribution, trailers, unpublished-range auditing, and command-local identity changes.
- Ask for an unresolved human identity only when a commit requires it. Do not start onboarding or substitute the baseline owner's identity.
- Preserve explicit disabled-attribution choices and document their effect. Missing configuration must not disable attribution automatically.

Done: temporary repositories prove author, committer, trailer, amend, and audit behavior without Astrobyte config. Human Git configuration stays unchanged. Invalid or missing identity fails before creating a commit.

### C4. Make personalization optional deltas and preserve updates

Scope: `scripts/profile.py`, `scripts/install.py`, profile templates, adoption and setup instructions, profile documentation, and installer tests.

- Add baseline-plus-overrides representation without breaking legacy profiles.
- Keep baseline installation free of onboarding and repository creation.
- Make the explicit interview record requested differences. Offer local-only personalization as a complete result; repository publication remains a separate chosen action.
- Support approved portable overrides in installed skill resources when cloud portability is requested. Generate consumer resources consistently, excluding machine facts and secrets.
- Update inherited defaults with new package versions while preserving explicit overrides. Retain legacy snapshots until migration is explicitly selected.
- Preserve preview, confirmation, backups, unrelated skills, and repeat-install behavior.

Done: fresh quick install, explicit personalization, local-only use, portable overrides, legacy installation, update, and repeat installation pass focused fixtures. No real user installation or private repository creation is needed for these checks.

### C5. Validate package and selection dependencies

Scope: `catalog.json`, installer selection logic, validator, and dependency tests.

- Declare hard sibling dependencies separately from conditional references and optional suggestions.
- Audit both skill bodies and packaged references. For example, the architect needs API guidance only for the HTTP or GraphQL branch; the security skill's observability commentary is not automatically a hard dependency.
- Resolve hard dependencies for selected workflow bundles. Preserve independent leaf installation and report unavailable conditional capabilities when their branch is used.
- Test copies outside the source tree. Reject required runtime resources that resolve outside their package or declared dependency selection.
- Keep setup, adoption, and update as explicit management actions. Apply product-specific invocation controls without violating existing owned-skill frontmatter rules.

Done: missing dependencies and resources are detected, suggestions do not expand a selection, full remains the default, and unrelated installed skills remain untouched.

### C6. Document and verify the colleague's path

Scope: README, adoption and quick-install docs, profile reference, architecture, Cursor adapter, and this plan's handoff record.

- Document two steps: install the baseline locally, then sync and use it in cloud tasks.
- Explain that `/astrobyte-mode` uses packaged defaults and `/adopt-skill-stack` manages installation or requested personalization.
- Document local overrides versus approved portable preferences. Correct Build persistence guidance and keep the existing Build installer as a compatibility option.
- Perform one real Cursor cloud smoke check if that environment is available: no source checkout or machine config, readable baseline resources, representative task, and review or attribution when applicable.
- If cloud access is unavailable, record the smoke check as pending with exact steps and expected observations. Do not claim it passed.

Done: documentation describes implemented behavior, required automated checks pass, and the cloud observation is either recorded or explicitly pending. No performance parity experiment is required.

## Verification and recoverability

For each checkpoint, run focused behavior tests. Before committing, run the repository-required commands:

```bash
python3 -B scripts/validate.py
python3 -B -m unittest discover -s tests -v
```

Inspect the diff for secrets, machine details, unintended upstream changes, and unrelated edits. Use the Git attribution helper for agent-created commits. Before opening a PR or pushing implementation changes, apply the existing independent review gate and attribution audit. Review and merge policy remains unchanged.

Commit each verified checkpoint before starting the next. Push approved checkpoints to the implementation branch so recovery does not depend on one laptop. Keep the source branch and previous verified commits available. Avoid history rewrites and real-machine migrations while quota is low.

When quota is low enough to threaten completing the current slice, stop at its verified commit. If interrupted earlier, save the bounded diff and mark it unverified; do not mislabel it as a completed checkpoint. Record only durable evidence, not raw terminal logs or private configuration.

After each slice, update the table below and add the following handoff facts: branch, commit, changed files, commands and outcomes, unresolved decisions, pending external checks, and the exact next action. If a process is still running, record its purpose and a safe way to inspect or stop it. Do not start another slice until the current one is recoverable.

| Checkpoint | State | Commit and evidence |
| --- | --- | --- |
| Planning | Complete | Original plan pushed as `f464f75`; carried onto the implementation branch as `f6edf3d` |
| C1 | Complete | `89f9d2e`; generator, four packaged resources, consistency validation, five focused tests |
| C2 | Complete | `801684e`; standalone resolver, router and review fallback, packaged configuration and dispatch guidance; checkpoint commit in this branch's history |
| C3 | Complete | `a70f232`; packaged Git-policy fallback, environment identity, conditional includes, amendments, and attribution audit tests |
| C4 | Complete | `22248e0`; local deltas, approved portable export, inherited updates, legacy compatibility; 56 tests and independent review PASS |
| C5 | Complete | `c258734`; dependency closure, independent subsets, contained runtime resources; 62 tests and independent review PASS |
| C6 | Complete | Local install and sync docs, isolated installed CLI smoke PASS, 62 tests and independent review PASS; hosted check explicitly pending |

## Current handoff

PR #18 merged as `e7d09b3`. Implementation branch `feat/portable-skill-runtime` starts from that merged main and includes the saved plan. C1 adds `scripts/portable_profile.py`, packaged policies, consistency validation, and tests. C2 adds the canonical `scripts/runtime_config.py`, generated standalone copies in router and review, packaged configuration and reviewer dispatch guidance, updated consumer instructions, and four runtime tests.

Generation and `--check` passed. Repository validation passed for all 40 skills, all 43 tests passed, and independent read-only review returned PASS for both checkpoints. Runtime commands executed from isolated copied skill folders with an empty home and no source imports. Tests cover personal, machine, and project precedence, explicit-config directory support, invalid or unavailable explicit config, preserved worker and external-action settings, and secret exclusions. Review corrected a Cursor instruction that initially overrode an explicitly selected reviewer.

No user-machine installation, profile migration, or cloud action has occurred. C3 removes mandatory machine configuration from the attribution helper, preserves existing authorship with a matching amendment record, and rejects unresolved identity before a commit. Nine focused Git tests and independent review passed. The checkpoint's full test result is recorded in its commit message. No background process needs recovery after verification completes.

C4 adds `scripts/preferences.py`, generated package-contained validators, a delta template, installer export and inheritance tracking, ordered agreement layers, adoption instructions, and seven preference tests. Full validation passed for 40 skills and all 56 tests passed. Independent review found and corrected agreement precedence; the corrected review returned PASS. The commit containing this record is the verified C4 checkpoint.

C5 declares hard dependencies separately from conditional specialists and suggestions. `scripts/packages.py` validates closure, cycles, unknown names, required files, linked references, and symlink containment in copied packages. The installer supports `--skills` and `--profile`, preserves extra managed and unrelated skills during quick updates, and previews dependency expansion. Setup is explicitly invoked. Six package tests and all 62 repository tests passed; validation passed for 40 skills. Independent review corrected an omitted router playbook declaration, then returned PASS. The commit containing this record is the verified C5 checkpoint.

C6 updates README, adoption, quick-install, profile, architecture, and Cursor guidance. Ordinary cloud work uses packaged defaults after local installation and sync. Source access remains necessary for management, and cloud-local Build installation remains an alternative. `docs/cursor-cloud-smoke.md` records the hosted check as pending with exact steps and expected observations.

The full installer CLI was run into a temporary home. Only its 38 Cursor skill folders were copied to another empty home. Router and review helpers executed from those installed folders with no source imports or Astrobyte config and resolved the durable baseline. The installed Git helper created a commit using the fixture repository's human identity, Cursor committer, and Agent trailer; audit passed and ordinary Git configuration stayed unchanged. This is a local test of the sync boundary, not a hosted agent observation. Repository validation passed for all 40 skills, all 62 tests passed, generator consistency passed, and independent final review returned PASS. Performance experiments were excluded as requested.

No user-machine installation, private repository creation, migration, or hosted Cloud Agent action occurred. All earlier checkpoints were committed and pushed. No running process needs recovery.

Next action after this verified C6 commit: push the final checkpoint, update and ready PR #19, confirm CI at its exact head, and merge under the user's existing authorization. Preserve the branch and checkpoints. The only pending external check is the hosted checklist; it does not block implementation completion under C6's agreed acceptance criteria.
