# Contributing

The skills are provided as-is. Focused bug fixes, clearer instructions, and harness or OS adaptations are welcome. There is no compatibility guarantee, response deadline, or commitment to maintain every environment. Read the [code of conduct](CODE_OF_CONDUCT.md); report security issues through [SECURITY.md](SECURITY.md).

## Submit a change

1. Read [AGENTS.md](AGENTS.md) for repository invariants and task-specific references. These instructions apply to human and agent-assisted contributions.
2. Create a short-lived feature branch from current `main`, such as `docs/contribution-workflow` or `fix/installer-check`.
3. Keep the change focused. Preserve upstream attribution and license files. Keep credentials and machine-specific configuration out of commits.
4. Run the repository checks from the repository root:

   ```bash
   python3 scripts/validate.py
   python3 -m unittest discover -s tests -v
   ```

   Add or update tests when changing installer or validator behavior. Inspect `git diff --check` and the complete diff before committing.
5. Commit with a conventional message, such as `docs: explain contribution workflow`. Agent-created commits follow the attribution instructions in [AGENTS.md](AGENTS.md).
6. Push your feature branch and open a pull request against `main`. Complete the PR template with the reason for the change, verification results, and any remaining risks. Use a draft PR while work is incomplete. Follow the independent review gate in [astrobyte-mode](skills/astrobyte-mode/SKILL.md) before an agent-created push or PR.
7. Address review feedback and rerun affected checks after changes. Leave the PR for the repository owner to review and merge.

## Merge ownership

Only the repository owner, `TheAstroByte`, merges pull requests into `main`. Collaborators and agents submit changes through PRs. Agents leave merging to the owner even when authenticated with the owner's credentials. Keep auto-merge disabled.

Do not push directly to `main`, force-push it, or delete it. Changes to repository access, visibility, or merge settings require the owner's explicit approval.

GitHub's active repository rules are authoritative for server enforcement. This contributor agreement applies even where a setting is unavailable; it does not claim branch protection is enabled. Changes to repository settings are separate from a contribution's source changes.

## Extend a harness or fix an OS issue

1. Report the source version or commit, OS, harness version, exact command or prompt, expected behavior, and smallest reproduction. Redact personal paths, usernames, endpoints, and credentials. Separate file installation from fresh-session discovery and task behavior.
2. Check current official documentation for discovery paths, instruction precedence, invocation controls, and available tools. Link the supporting sections and state the versions they cover. Keep undocumented behavior unverified.
3. Change the relevant `adapters/` guide and the narrow mapping in `scripts/install.py` or `scripts/routing.py` only when needed. Preserve the default full install, unrelated skills, backups, ownership markers, shared destinations, and removal behavior.
4. Add a focused regression for path, ownership, override, or lifecycle changes using an isolated temporary home. For instruction-only repairs, inspect the copied artifact and exercise a representative task where possible. Run the repository checks above.
5. Record a fresh-session discovery or routing observation when the host is available. Include a minimal task and result, and update [observed environments](docs/observed-environments.md) with evidence and limits. If unavailable, state that live behavior is pending rather than treating package tests as a substitute.

OS-specific changes follow the same reproduction and focused-test procedure. Do not add a compatibility layer or dependency for an unobserved problem. Preserve source pins, licenses, and documented local adaptations during upstream refreshes.

## Before the owner merges

- Review the latest PR diff, especially changes to agent instructions, installers, and GitHub Actions workflows.
- Run the local validator and complete test suite on the current PR revision. Record commands, results, and unavailable checks in the PR.
- Hosted Actions is currently disabled. If the owner later enables it, verify the actual current-head results, including the `Required CI` aggregate. Do not claim a hosted pass or require an unavailable hosted result while execution is disabled.
- Resolve review conversations and check that the branch has no conflicts with `main`.
- Prefer squash merging for a focused change, then delete the merged feature branch.
