# Contributing

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

This private, personally owned repository currently uses GitHub Free. The workflow above is a contributor agreement, not an enforced branch protection rule. Collaborator write access still technically permits merges and direct pushes.

## Before the owner merges

- Review the latest PR diff, especially changes to agent instructions, installers, and GitHub Actions workflows.
- Confirm the `validate` check from GitHub Actions passes on the latest PR commit. It runs package validation and the test suite.
- Resolve review conversations and check that the branch has no conflicts with `main`.
- Prefer squash merging for a focused change, then delete the merged feature branch.
