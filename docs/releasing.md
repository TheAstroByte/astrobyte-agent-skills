# Release a verified source revision

Use a focused release PR for `VERSION`, matching catalog and template versions, generated resources, and release notes. Keep installer or policy fixes in separate PRs. The repository owner merges; publication and repository-setting changes require explicit authority.

## Verify before publication

1. Record the intended version and exact source revision. Work from a clean checkout or an isolated export of the reviewed tree, with no private files or inherited Git refs.
2. Run the repository checks:

   ```bash
   python3 scripts/validate.py
   python3 scripts/portable_profile.py --check
   python3 scripts/package_licenses.py --check
   python3 -m unittest discover -s tests -v
   ```

3. Exercise the documented CLI in temporary homes: fresh full install, cancellation and preview, repeat update, explicit subset, local preferences, approved portable export and removal, conflict backups, shared ownership, bootstrap followed by full adoption, uninstall, and state purge. Check actual installed notices and routing records. Keep recovery-failure coverage in the suite.
4. Compare generic runtime defaults with any retained personal rules. Preserve private preferences and legacy agreements; a release check does not authorize installing onto the operator's real machine.
5. Scan the complete proposed tree and Git history with a current trusted secret scanner. Check known private identifiers separately outside the repository. Inspect branches, tags, PR text and reviews, comments, Actions logs, artifacts, releases, and repository metadata that will become public. Record inaccessible material rather than calling it clean.
6. Obtain independent review for the release tree and its evidence. Record limitations from [observed environments](observed-environments.md); source and package checks do not prove live discovery or model behavior on every host.

## Check the destination and settings

Record source and destination repository identities before a rename or visibility change. Preserve any private original independently. Check for active work and update affected remotes before reusing its old name; name reuse can remove the old redirect. Never import private refs into the public candidate.

Prepare and verify the available repository controls:

- Protect `main` with PRs, resolved review conversations, and blocks on deletion and force-pushes. Apply the normal rules to the owner, with no routine bypass. Keep external approval count at zero while there is one maintainer; review and owner-only merging still apply.
- Keep squash merging available and auto-merge disabled. Restrict write/admin access to the intended maintainers. GitHub cannot distinguish a human from an agent using the same credentials; agent merge restrictions also remain in `AGENTS.md`.
- Protect published version tags from update and deletion. Create a tag only for the verified merged revision.
- Verify private vulnerability reporting, available dependency alerts, secret scanning, and push protection. Check community files and issue templates after merge. Enable only available no-cost features within approved scope.
- Hosted Actions is currently disabled and stays disabled until the owner explicitly changes that instruction. Do not require an unavailable hosted check. If enabled later, observe the matrix and secret scan at the current revision before requiring `Required CI` and an up-to-date branch. Code scanning that uses Actions also waits for that approval.

Observe actual enforcement through the API or a bounded test; a configuration file or successful settings request alone does not prove a rule works. Private plan limits may defer some protections until the candidate becomes public. Record that limit and recheck before declaring release complete.

## Publish and verify

After the authorized cutover, confirm the intended repository is public and any preserved original remains private. Verify active protections and security settings, anonymous access to the exact source revision, and the README's canonical install URL. Install from that retrieved source into a temporary home and inspect the resulting packages and ownership records.

Create the reviewed version tag and release notes only after those checks. Record the final commit, tag, settings results, remaining capability limits, and the owner's merge. Clean merged task branches and worktrees without removing user changes or required backups.

For a functional defect, use a focused corrective or revert PR and preserve installed backups. Moving a repository back to private does not retract copies already obtained while public. Preserve privacy before publication rather than relying on a visibility rollback.
