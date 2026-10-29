# Upstream maintenance

## Refresh procedure

1. Fetch the pinned source repository.
2. Compare the current pin with the proposed commit.
3. Copy only cataloged skills and their referenced resources.
4. Preserve upstream names for substantially unchanged skills.
5. Put merged or materially changed behavior in an `astrobyte-*` skill.
6. Update `THIRD_PARTY_NOTICES.md` and `catalog.json`.
7. Run validation and tests.
8. Review descriptions, harness assumptions, external side effects, and new scripts before committing.

## Package license notices

Each source's `license_file` in `catalog.json` names its canonical license copy. Run `python3 scripts/package_licenses.py` after changing a source license, source pin, or skill provenance. It generates `LICENSES.txt` inside every skill from its `source` and deduplicated `derived_from` sources. Owned packages include the Astrobyte MIT notice; adaptations also include their declared upstream notices and revisions.

Keep these generated files with standalone copies and cloud-synced packages. The native installer copies them as package files and rejects a missing notice. Repository validation checks the complete contents against the canonical sources; `python3 scripts/package_licenses.py --check` checks notices alone. Regenerate rather than editing a package notice by hand. Preserve original upstream license files unchanged.

For a new skill recommendation, cite primary evidence for behavior, maintenance, and license. Also cite independent public feedback. Separate fact, reputation, and inference, and state when meaningful independent feedback does not exist.

## Current source roles

- Matt Pocock: requirements, domain language, module design, diagnosis, research, prototypes, handoffs, and agent-facing writing.
- Pstack: concise writing, blast-radius proof, technical writing, TypeScript discipline, playbook routing, and engineering principles.
- Addy Osmani: specialist gaps in APIs, frontend, browser verification, security, CI/CD, Git, migrations, observability, performance, shipping, and source-grounded implementation.
- Anthropic: visual direction for new interfaces and deliberate redesigns through `frontend-design`. Preserve the unchanged instructions and package-local Apache-2.0 license from the commit in `catalog.json`. Review upstream resources and applicable notices at every refresh. The upstream package files remain `SKILL.md` and `LICENSE.txt`; Astrobyte adds the generated `LICENSES.txt` notice.
- Tstack: selected PR-completion, Sol-loop, council, continuation, and feedback procedures, adapted in the optional `astrobyte-pr-workflows` package. Preserve its package-local MIT notice and reviewed source pin. Recheck explicit invocation, the no-merge contract, mode-specific scope, model selection, and external actions when comparing later upstream changes. The source watcher is not redistributed. Independent operational evidence remains limited; an upstream author's workflow is a design input, not proof of this adaptation's behavior.
