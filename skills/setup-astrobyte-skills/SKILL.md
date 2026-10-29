---
name: setup-astrobyte-skills
description: Install the shared Astrobyte profile without onboarding, or configure a personalized profile when requested. Invoke explicitly to install or change this stack on a machine.
disable-model-invocation: true
metadata:
  opencode/autoinvoke: "false"
---

# Setup Astrobyte skills

Default to the shared Astrobyte profile without onboarding. Follow `skills/adopt-skill-stack/references/quick-install.md` in the source checkout, or `references/quick-install.md` in the installed `adopt-skill-stack` folder. Resolve the source URL supplied by the user if neither is available. Continue below only when the user explicitly requests a machine setup interview or personalization. Personalization records differences from the baseline; installation does not require creating a new profile or private repository.

1. Locate the repository root containing `config/repository.json`, `catalog.json`, and `scripts/install.py`.
2. Resolve the committed operator handle or approved baseline delta. Use the existing Astrobyte baseline when no personal profile exists. For requested local-only personalization, follow `adopt-skill-stack`'s delta path; use this machine interview only when machine-specific setup was requested.
3. Run `python3 scripts/install.py --operator <handle> --interview` in an interactive terminal. Relay every question to the user when the agent product cannot give the script direct terminal input.
4. Use detected agent products as evidence, not as consent. Confirm active products, preferred product, machine alias, delivery default, autonomy, skill profile, model environment, reviewer model, parallelism, unattended work, interactive and unattended external-action policies, Git workflow, human and per-product Git identities, tracker, docs path, compute, experiment budget, browser tools, and containers. When the working agreement names no reviewer, ask once which model to use and offer to record the answer there.
5. Present the script's plan. Apply it only after the operator confirms.
6. Run `python3 scripts/validate.py` and `python3 -m unittest discover -s tests -v` from the repository.
7. Report the installed profile, machine alias, delivery default, destinations, routing locations, config path, backups, and manual follow-up, such as the Cursor Cloud User Rule in `docs/routing.md`.

The setup is complete when `python3 scripts/install.py --check` passes and each selected harness can discover `astrobyte-mode`.

Preserve unrelated skills and machine configuration. Treat credentials, private repository access, and harness permission changes as separate user-authorized actions.
