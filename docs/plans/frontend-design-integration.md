# Integrate Anthropic frontend design

Status: repository implementation authorized on 15 October 2026. Packaging, routing, and automated verification are complete. Live harness checks, visual comparisons, and machine installation remain separate.

## Outcome

Include Anthropic's `frontend-design` in the `builder` and `full` profiles. Route new interfaces and deliberate visual redesigns through it before implementation. Keep `frontend-ui-engineering` for component structure, interaction states, accessibility, and responsive behavior.

The default Astrobyte profile selects `full`, so this makes design guidance part of the normal installation. Keep `core` focused on shared workflows. Users can still select `frontend-design` independently.

Deliver the repository integration as one pull request. Machine installation follows as a separately requested action after verification.

## Evidence and decisions

- The [official skill](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) covers visual direction, type, palette, layout, and critique. Preserve its upstream name and contents rather than merging it into the engineering skill.
- Its [package license](https://github.com/anthropics/skills/blob/main/skills/frontend-design/LICENSE.txt) is Apache 2.0. Preserve that file inside the installed package. Update the repository's MIT-only description of third-party sources and retain any applicable upstream notices.
- `catalog.json` currently includes `frontend-ui-engineering` in `builder` and `full`. `profiles/astrobyte/profile.json` already selects `full`, so changing the operator profile is unnecessary.
- The router owns composition, according to `docs/architecture.md`. Keep integration instructions in Astrobyte-owned files and leave both vendored skills unchanged.
- The installer already copies complete skill directories and resolves catalog selections. Prefer catalog changes and behavior tests over new installer logic.
- Public listings are not comparative quality evidence. Theo's endorsement has not been independently verified here. During implementation, record attributable independent feedback if available, and explicitly state the evidence gap otherwise. Judge local usefulness with representative outputs.

## 1. Vendor and register the package

1. Resolve a reviewed full commit SHA from `anthropics/skills`. Inspect the skill directory and applicable upstream notices at that commit.
2. Copy `skills/frontend-design/SKILL.md`, `LICENSE.txt`, and any required package resources from the same commit. Compare the copied files with that source.
3. Add an `anthropics` source with the repository and commit to `catalog.json`.
4. Register `frontend-design` as a `builder` skill. Include `LICENSE.txt` in its `runtime_resources` so validation detects a missing installed license.
5. Add the skill to both `builder` and `full`. Keep standalone selection free of sibling dependencies.
6. Update `THIRD_PARTY_NOTICES.md` with the pin, source, license, and applicable attribution. Revise its opening sentence to cover each source's actual license.
7. Update `docs/upstreams.md` with Anthropic's source role and refresh procedure. Keep routine refreshes pinned and reviewable.

Done when catalog validation accepts the package, both profiles select it, and an isolated package copy contains the unchanged upstream instructions and license.

## 2. Route design work explicitly

Add one conditional pointer in `skills/astrobyte-mode/SKILL.md` to a short, package-contained `references/frontend.md`. Reach it for new user-facing interfaces and deliberate changes to visual design, including prototype work. Declare the resource and relevant conditional skill dependencies in the catalog.

The reference defines this sequence:

1. Read the brief, existing UI, brand rules, and design tokens. Treat the user's requested scope and the established product design as constraints.
2. Use `frontend-design` to establish visual direction before coding a new interface or redesign. Reuse a supplied direction instead of introducing another approval step.
3. Use `frontend-ui-engineering` to implement the interface and its interaction states within the existing stack.
4. Inspect the rendered result in an available browser. Use the existing browser-testing guidance when its required tools are available. Check responsive layout, keyboard use, and the match to the brief. Record unavailable checks honestly.

Keep routine bug fixes and backend work outside the visual-design branch. An existing UI fix must not become an unsolicited redesign. For an explicit design-only request, apply the relevant design steps without forcing component implementation.

For a `core` or explicit subset installation, apply the existing missing-specialist policy only when that branch requires an absent skill. Runtime routing must not install packages or begin onboarding.

Done when agents have a clear trigger, order, and completion criterion without changes to either vendored skill or harness-specific routing rules.

## 3. Verify installation and behavior

Extend existing tests at the public selection and installation boundaries:

- `builder` and `full` include the design skill, while `core` and unrelated explicit subsets remain unchanged.
- Explicit selection of `frontend-design` installs a usable independent package.
- Missing `LICENSE.txt` fails package validation, including after copying outside the checkout.
- Temporary-home installations contain both instructions and license at each supported harness destination. Codex and OpenCode retain their shared destination behavior.
- Reinstallation preserves unrelated skills and existing preferences. Managed conflicts retain the installer's existing backup behavior.
- Update the fixed full-profile count assertion in `tests/test_packages.py` and retain meaningful dependency assertions.

Run the repository-required checks:

```bash
python3 -B scripts/validate.py
python3 -B -m unittest discover -s tests -v
```

Check routing with representative prompts and inspect actual skill-loading evidence where the harness exposes it:

| Task | Expected behavior |
|---|---|
| Build a landing page with a clear brief | Establish a visual direction, then implement and inspect it. |
| Add a screen to a dashboard with established tokens | Preserve the product's visual language and reuse its components. |
| Fix a button handler without changing appearance | Keep the repair focused, without starting a visual redesign. |
| Build a backend API | Leave frontend design unloaded. |

For the two visual tasks, keep before-and-after screenshots from equivalent baseline and integrated runs if the evaluation environment is available. Compare brief adherence, visual coherence, accessibility, and unnecessary changes. Treat these as qualitative smoke checks, not proof of universal design improvement. Automated package tests do not establish visual quality or live discovery across every harness.

Could representative real outcomes improve later versions? Yes. Keep user-accepted screenshots as the outcome signal and judge later changes against the same brief and accessibility checks.

Done when automated checks pass and the observed behavior matches the applicable routing cases. Record unavailable live harness or browser checks as pending.

## Expected implementation files

- `skills/frontend-design/SKILL.md`, `skills/frontend-design/LICENSE.txt`, and any resources or notices required by the reviewed upstream snapshot.
- `catalog.json` and `THIRD_PARTY_NOTICES.md`.
- `skills/astrobyte-mode/SKILL.md` and the new `skills/astrobyte-mode/references/frontend.md`.
- `docs/architecture.md`, `docs/upstreams.md`, `docs/skill-stack-assessment.md`, `README.md`, and this plan.
- `tests/test_packages.py` and the relevant existing installer tests in `tests/test_install.py`.

Change installer or validator implementation only if the behavior checks expose a concrete gap. Existing catalog metadata supports the proposed integration.

## Delivery and rollback

Implement in an isolated worktree and keep the addition in one coherent change. Apply Git attribution before commits and obtain the required independent review `PASS` before any authorized push or pull request.

After repository integration, a requested machine update uses the existing installer preview and backup behavior. Verify that a fresh agent session discovers `frontend-design`; an existing chat's skill list alone does not prove discovery.

Rollback removes the new catalog entries, routing reference, and package together. For an installed machine, preview removal through the existing managed-install workflow. Quick updates preserve extra skills, so removing profile membership alone does not prove that a previously installed copy disappeared.

## Implementation evidence, 15 October 2026

- Base: `70f5196b6886d860b024e8e50c16d234e65fb293`, branch `feat/frontend-design`.
- Anthropic source: `dbd4588f9e1033efb41dad4bef2f7947c8993d44`. The two copied files retain their upstream bytes. The reviewed root third-party notices cover software and fonts outside this package.
- `python3 -B scripts/validate.py`: validated 41 skills and all profiles.
- `python3 -B -m unittest discover -s tests -v`: all 99 tests passed. The new package tests exercise all five harnesses across four installation destinations, standalone selection, license loss, conflict backups, repeat installation, and preference preservation in temporary homes.
- `python3 -B scripts/portable_profile.py --check`: packaged baseline resources match their canonical source. Installer and validator implementation required no changes.
- Independent anecdotal feedback and its limitations are recorded in the dated addition to `docs/skill-stack-assessment.md`.
- Live skill discovery in each harness, rendered UI comparisons, and before-and-after screenshots remain pending. This integration changes instruction packages; automated installation checks do not establish visual improvement.
- Independent read-only assessment covered all four representative prompts. It identified an unconditional browser step after the design-only branch; the corrected step applies only to implemented interfaces.
