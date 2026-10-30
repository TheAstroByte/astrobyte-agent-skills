# Skill mechanics

The skill-specific branch of [`writing-for-agents`](SKILL.md): what changes when the document is a skill — frontmatter, the invocation choice, and router skills. Everything else about writing it is the universal reference in `SKILL.md`.

## Invocation

Separate discovery, loading, and authority. Descriptions advertise when a host should select a skill; invocation controls govern that host's loading behavior. Neither grants permission for external actions.

- A **model-invoked** skill uses its description to let the host select it for relevant tasks. Write the description for the agent, with the trigger branches it needs. Reference needed by several workflows can live in one discoverable skill when they genuinely need that capability.
- A **user-invoked** skill is an operation the user chooses explicitly. Use a human-facing description and the supported host control to suppress automatic selection. Keep the operation's user-intent requirement in its instructions, since hosts differ in which controls they enforce.

Apply the target host's documented controls:

- [Codex](https://learn.chatgpt.com/docs/build-skills): `agents/openai.yaml` uses `policy.allow_implicit_invocation: false`; explicit `$skill-name` invocation remains available.
- [Claude Code](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill): `disable-model-invocation: true` reserves native invocation for the user. If the host blocks a call, honor that block rather than reproducing the operation through another tool.
- OpenCode differs by version: [version 1](https://opencode.ai/docs/skills/) ignores invocation metadata and uses skill permissions for native loading; [version 2](https://dev.opencode.ai/v2/docs/skills/) hides skills with `opencode/autoinvoke: false` or `disable-model-invocation: true` from automatic discovery while retaining explicit loading. Check the installed version before promising enforcement.

Pick model-invocation when the host should select the skill automatically for relevant work. Use user-invocation when the user must choose the operation. A shared reference reached through an authorized file read does not require automatic selection.

An authorized workflow may read a named skill or reference file when the host permits that read. This is distinct from native skill invocation and never bypasses a denial or authorizes an explicit-only operation. Shared reference files can keep common rules in one place without depending on another skill's invocation mechanism.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split off a model-invoked skill when you have a distinct leading word that should trigger it on its own — a trigger word you actually use in your prompts — or another skill must reach it. You pay context load for the new always-loaded description, so that independent reach has to be worth it.

## Router skills

When user-invoked skills multiply past what you can remember, a **router skill** can name them and when to reach each. It may direct an authorized workflow to read shared procedures where the host permits it. Explicit-only operations still require the user's intent; naming them in discussion or reading their reference does not invoke them.
