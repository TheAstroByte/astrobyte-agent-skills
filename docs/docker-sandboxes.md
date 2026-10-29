# Claude Code in Docker Sandboxes

This page is opt-in. It applies only to Claude Code running in [Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) (`sbx`) with a host workspace mounted. Every other harness, and Claude Code on the host, uses [Routing](routing.md) as written.

Hand this page to an agent with the workspace path and the sandbox name. The agent runs the steps on the host, outside the sandbox.

## Why the sandbox misses routing

- The sandbox has its own home directory, so host routing such as `~/.claude/rules/astrobyte-routing.md` never reaches it.
- sbx writes its own profile, `CLAUDE.md`, into the parent directory of the mounted workspace. For a workspace at `<parent>/<workspace-name>`, that's `<parent>/CLAUDE.md` inside the sandbox.
- With Claude Code's default Project instructions, any `CLAUDE.md` in the working directory or above it stops Claude from reading `AGENTS.md`. So a workspace `AGENTS.md` is visible through the mount but never loaded.
- Skills arrive separately, through sbx's shared skills store.

The fix keeps `AGENTS.md` as the only routing source and adds a workspace `CLAUDE.md` that is a symbolic link to it. Claude loads every `CLAUDE.md` from its working directory upward, so a session started anywhere under the workspace gets the routing.

This was verified with sbx v0.47.0 and Claude Code 2.1.296, from the workspace root and from two nested repositories.

## Steps

You need three values. `<workspace>` is the absolute path in the `WORKSPACE` column of `sbx ls`. `<sandbox>` is the sandbox name from that row. `<checkout>` is an Astrobyte checkout on the host.

1. **Confirm the sandbox.** Run `sbx ls`. Done when the row for `<sandbox>` shows agent `claude` and workspace `<workspace>`. For any other agent, stop: this procedure covers Claude Code only.
2. **Install workspace routing.** Run `python3 <checkout>/scripts/install.py --harnesses <the harnesses you use> --routing --workspace-root <workspace>`, then `python3 <checkout>/scripts/install.py --check`. Done when the check passes and `<workspace>/AGENTS.md` contains `<!-- astrobyte-routing:begin schema=1 -->`. If both are already true, skip the install.
3. **Mirror `AGENTS.md`.** If `<workspace>/CLAUDE.md` does not exist, run `ln -s AGENTS.md <workspace>/CLAUDE.md`. The relative target keeps the link valid inside the sandbox mount. If a `CLAUDE.md` already exists, stop and ask the operator how to combine them; leave the file unchanged. Done when `readlink <workspace>/CLAUDE.md` prints `AGENTS.md`.
4. **Refresh sandbox skills.** Run `sbx skills import --dry-run`, review the list, then run `sbx skills import --force`. Import copies every skill from the host's agent skill directories and replaces store entries with the same name, using the first copy it finds (`~/.agents/skills` comes before `~/.claude/skills`). Done when `sbx exec <sandbox> sh -c 'ls ~/.claude/skills'` lists `astrobyte-mode`, `astrobyte-review`, and `astrobyte-git-identity`. A running sandbox sees edits to existing skills at once and new skills after its next start.
5. **Verify in the sandbox.** Run the command below twice: with `<directory>` set to `<workspace>`, then to a repository inside it. Each run is one model call billed through the sandbox's credentials. Keep the prompt before `--disallowedTools`, because that flag takes every following argument as a tool name.

   ```bash
   sbx exec -w <directory> <sandbox> claude -p "Without using any tools, list every instruction file loaded into your context, then quote the first numbered Astrobyte routing instruction or say NONE." --disallowedTools Read Bash Glob Grep Edit Write WebFetch Task
   ```

   Done when both answers list `<workspace>/CLAUDE.md` and quote the rule that starts "Before substantial work, load the `astrobyte-mode` skill".

After each Astrobyte update, repeat step 4. The link follows `AGENTS.md`, so routing changes need nothing more.

## Review gate in the sandbox

A sandbox usually has no Codex CLI, so sandboxed Claude can run the review gate only when its model provider offers the reviewer model, for example a GPT Sol model through an LLM gateway. `<model>` is that model's name.

1. **Check the reviewer model.** Run the gate's reviewer command with a test prompt:

   ```bash
   sbx exec -w <workspace> <sandbox> claude -p "Reply with exactly: REVIEWER_OK" --model <model> --setting-sources user --tools Read,Grep,Glob --strict-mcp-config --permission-mode plan --output-format json
   ```

   Done when the JSON `result` is `REVIEWER_OK` and `modelUsage` lists `<model>` alone. If the call fails or another model appears, the gate is blocked in this sandbox. Push from the host only after the host's own review gate returns `PASS`.
2. **Pin the reviewer (optional).** To fix the model or its reasoning level for this sandbox, add a sentence such as "Claude Code in Docker Sandboxes runs the `astrobyte-review` gate with `--model <model> --effort high`." to `<workspace>/AGENTS.md`, outside the managed routing block. The installer leaves text outside the block alone, and the link carries it into the sandbox.

## Limits

- **Only the workspace file is mirrored.** A repository inside the workspace that has only an `AGENTS.md` is still unread by sandboxed Claude. There are two fixes:
  - **Per repository.** Link `CLAUDE.md` to `AGENTS.md` in that repository. This is a repository change, so commit it deliberately.
  - **Per sandbox.** Set Project instructions to read both files by merging the JSON below into `~/.claude/settings.json` inside the sandbox. Claude reads every `AGENTS.md` on the path with this setting. Claude ignores this key in project settings files, and sbx rewrites `settings.json` when it creates a sandbox, so apply it again after each `sbx create`.

    ```json
    { "pluginConfigs": { "cc-plugin-agents-md@builtin": { "options": { "instructionFiles": "claude-md-and-agents-md" } } } }
    ```

- **Host Claude Code reads the link too.** The content is the same routing, so nothing is duplicated in effect. A host Claude session under the workspace then follows the same default rule, so repositories that have only an `AGENTS.md` need the fixes above on the host as well.
- **Other sandboxed agents are untested.** This page has been checked only with Claude Code. Codex, OpenCode, and Cursor sandboxes may load workspace files differently.
- **The method lives in the workspace, not in a sandbox kit.** A kit can make the same change per sandbox, but it has to be passed with `--kit` on every `sbx create`. The workspace link covers every sandbox that mounts the workspace.

## Remove

1. Delete the link only if it points at `AGENTS.md`: `[ -L <workspace>/CLAUDE.md ] && [ "$(readlink <workspace>/CLAUDE.md)" = AGENTS.md ] && rm <workspace>/CLAUDE.md`. If the check fails, leave the file and ask the operator. Do this before `--remove-workspace-root <workspace>`, `--remove-routing` without `--harnesses`, or `--uninstall --all`. Each can delete an `AGENTS.md` the installer created, which would leave the link dangling.
2. Optionally remove skills from the sandbox store with `sbx skills rm <skill>...`.
