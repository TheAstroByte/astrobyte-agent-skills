# Repository and installation flow

## Independent repository

Local-only preferences and installation are a complete adoption result. Follow this publication branch only when the operator explicitly requests a separate repository. For that branch, recommend an independent private repository. Private forks remain tied to upstream access.

1. Confirm GitHub authentication and the target account or organization.
2. Confirm the new repository name, privacy, collaborator access, and initial review mode.
3. Create the repository without initializing it.
4. Rename the source remote to `upstream`, or add it under that name when no source remote exists.
5. Add the new repository as `origin`.
6. Push the unchanged source revision to the new repository's default branch. This gives the setup pull request a reviewable base.
7. Push the approved setup branch.
8. Open a pull request. Wait for CI and show failures.
9. Merge only after the operator approves the external action.

Never send a personal profile back to upstream without separate approval. Contributions to generic skills or tooling must exclude the adopter's private configuration.

For full renaming, create an explicit mapping for every `astrobyte-*` skill. Update directories, frontmatter names, catalog entries, cross-skill references, agent metadata, documentation, and tests. Validate the complete mapping before publication. Warn again that upstream updates will need this mapping on every release.

## Existing setup migration

After permission, inspect only named or known agent configuration and skill directories. Optionally inspect one or two project directories that the operator identifies.

Inventory existing skills, instruction files, permissions, plugins, MCP servers, agent profiles, and duplicates. For each item, propose `preserve`, `import`, `replace`, or `archive`. Review imported skills for provenance, license, scripts, and external actions. Back up every replacement and never overwrite an unrelated item silently.

## Machine installation

For an explicitly maintained legacy profile, run `python3 scripts/install.py --operator <handle> --interview`. The installer gathers machine-local facts and writes them under the operator's local configuration directory. Review the plan before applying it. Ordinary installation uses the committed baseline without this interview; follow [quick-install.md](quick-install.md).

If the preferred agent product is unknown, verify its current official documentation. Record its skill path, invocation syntax, repository instruction file, permission model, and plugin mechanism in `adapters/<name>.md`. Add installer support and a discovery test only after approval.

Verify the installed manifest, then invoke `adopt-skill-stack` or `astrobyte-mode` from each selected agent product. A copied directory is not proof of discovery.
