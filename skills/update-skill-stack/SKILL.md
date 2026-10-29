---
name: update-skill-stack
description: Review and apply upstream skill-stack updates without losing a personal profile or local skills. Use only when the user invokes $update-skill-stack or explicitly asks to update the adopted skill stack.
disable-model-invocation: true
metadata:
  opencode/autoinvoke: "false"
---

# Update the skill stack

1. Locate the adopted repository from the current checkout or `~/.config/astrobyte-agent-skills/install-manifest.json`. Read `config/repository.json`, the active operator profile, `docs/upstreams.md`, and the installation manifest. When the recorded checkout is gone, `python3 scripts/install.py --check` from any checkout prints the clone and checkout commands that restore it; ask where to clone before running them.
2. Check repository status. Stop for unresolved local changes that overlap the update.
3. Fetch `upstream` and identify the current base version and available release. Do not merge yet.
4. Create an isolated update branch or worktree.
5. Compare upstream changes with personal profiles, custom skills, catalog composition, adapters, installer behavior, licenses, and migrations.
6. Show behavioral changes, conflicts, renamed or removed skills, source-pin changes, and any new scripts or external actions.
7. Preserve personal profiles and custom skills. A fully renamed skill set needs a manual mapping for each upstream change.
8. Apply the reviewed update. Run `python3 scripts/validate.py` and `python3 -m unittest discover -s tests -v`.
9. Present the diff and installation plan. Ask before pushing, opening or merging a pull request, or reinstalling.
10. After approval, push the update branch, open the pull request, wait for CI, merge, and run `python3 scripts/install.py --operator <handle>` from the merged checkout. Relay any routing approval it previews. An installation made before 0.5.0 needs `--routing` once.
11. Run `python3 scripts/install.py --check` and resolve drift, checkout differences, and shadowed routing. Then verify actual skill discovery in the selected agent products. `docs/routing.md` describes each check result.

Follow the operator's update policy: manual only, notify, open a reviewed pull request, or merge and install automatically only when every configured gate passes. Agent and repository permissions remain authoritative.
