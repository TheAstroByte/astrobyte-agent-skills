# Runtime configuration precedence

Apply preferences in this order, from highest priority to lowest:

1. Explicit user instructions for the current task.
2. Project `.astrobyte/config.json`.
3. Coherent repository evidence for choices the project file leaves unspecified.
4. Machine config from `ASTROBYTE_CONFIG`, otherwise `config.json` under `ASTROBYTE_CONFIG_HOME` when set, otherwise `~/.config/astrobyte-agent-skills/config.json`.
5. Local personal deltas in `preferences.json`, then legacy personal profile and working agreement beside that machine config.
6. Approved portable deltas in this skill's `references/preferences.json`, when explicitly exported.
7. This skill's packaged Astrobyte baseline and working agreement.

Run `scripts/runtime_config.py --project <project-root>` from this skill's location to resolve JSON file preferences. The command reports their sources and agreement paths. Apply current instructions and repository evidence yourself. Project configuration conflicting with repository evidence is drift to resolve, not a choice based on file age.

Read the packaged agreement once when the workflow activates. Existing local agreements supply explicit personal preferences over that baseline. Apply higher-priority choices to the relevant passages. The command preserves complete legacy profile snapshots; it does not infer which fields their authors intended to inherit.

If Python is unavailable, read the packaged baseline and optional files in the same order. Missing optional files use the baseline. Report malformed files or a missing explicitly selected config and resolve the error before relying on those settings. Ordinary execution does not require a source checkout, cloning, installation, or an onboarding interview.

Resolve actual tools, reviewer models, Git identity, paths, and permissions in the execution environment. Preferences cannot grant authority or establish capability. Keep review and Git attribution requirements active even when machine config is absent.

New quick installs record inherited values separately. Unchanged inherited values follow the packaged baseline and personal deltas; edited machine values remain explicit. Legacy snapshots retain their full meaning until the operator approves a migration. Portable overrides contain approved reusable rules only, and include their baseline identity and authoring version. Omitted fields inherit the currently installed baseline.
