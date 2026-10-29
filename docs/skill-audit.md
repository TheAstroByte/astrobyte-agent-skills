# Skill audit

Reviewed 2026-10-02 against the catalog at `0.4.0` plus the review-gate, prototype-mode, reviewer-dispatch, and lean-PR changes. This document recommends. It does not change the catalog, profiles, or skill text.

Vendored files stay snapshots. A "drop from profile" action removes a skill from `catalog.json` profile lists and leaves the skill directory in place. `explicit_only` is not available for those skills: the validator requires `disable-model-invocation` in the skill file, and that file is vendored.

## Owned skills

| Skill | Recommendation | Why |
|---|---|---|
| `astrobyte-mode` | keep | Router. The new gate, prototype phrases, and pull-request steps live here. |
| `astrobyte-project-startup` | keep | Stack interview before implementation. No overlap with the review gate. |
| `astrobyte-git-identity` | keep | Commit attribution. Narrower than `git-workflow-and-versioning`. |
| `adopt-skill-stack` | keep | Already explicit-only. |
| `update-skill-stack` | keep | Already explicit-only. |
| `setup-astrobyte-skills` | keep | Now asks for a reviewer model when the agreement names none. |
| `astrobyte-tdd` | keep, then add one line | Red says "one test for the requested behavior" and "observable behavior". It does not say to assert public behavior, and principles now call tests of private state bloat. |
| `continual-improvement-check` | keep | 110 words, one question, stops. |
| `pr-feedback-loop` | keep | Shepherds an approved pull request. Different job from the pre-push review gate. |
| `hermetic-test-suites` | keep | Isolation failures. No second copy in owned skills. |
| `astrobyte-architect` | keep | Already sends module vocabulary to `codebase-design` and HTTP contracts to `api-and-interface-design`. |
| `astrobyte-verify-project` | keep | Project-local verification skill. |
| `astrobyte-show-work` | keep | Decision trail. `astrobyte-recall` reads it. |
| `astrobyte-review` | keep, then adjust the description | The review axis is now bloat. The description still says "maintainability". |
| `astrobyte-recall` | keep | Reads repo evidence, including handoffs. It does not write the handoff. |

Owned skills no longer say "independent reviewers". The remaining copy is in vendored `blast-radius`.

## Overlapping vendored skills

| Skill | Profile | Recommendation | Evidence |
|---|---|---|---|
| `git-workflow-and-versioning` | optional | dropped from full | Description says "Use when making any code change." About 2131 words. Overlaps `astrobyte-git-identity` and the working agreement's Git section. The skill file stays, and setup can still install it by name. |
| `source-driven-development` | builder | drop from profile | Description says "Grounds every implementation decision" and "any framework or library". About 1458 words. Project startup already points at primary docs in `references/sources.md`. |
| `handoff` | core | keep | 138 words. Writes the handoff document. `astrobyte-recall` and the handoff playbook consume it. |
| `blast-radius` | core | keep | Proves what else a change can break by running code. Step 6 still asks for several independent reviewers. Leave the vendored sentence. The review gate already covers a second reviewer for high-risk work. |
| `codebase-design` | core | keep | Vocabulary for deep modules. `astrobyte-architect` points here instead of restating it. |
| `ci-cd-and-automation` | full | keep | Pipeline setup. Trigger is pipeline work, not every change. About 1560 words. |
| `deprecation-and-migration` | full | keep | Removal and migration. The refactor playbook is shorter and does not replace this. About 1953 words. |
| `observability-and-instrumentation` | full | keep | About 1699 words. The description covers adding logs, metrics, tracing, or alerting, and also shipping a production feature that needs evidence, and diagnosing a production issue. The short performance and shipping playbooks do not replace that checklist. |
| `performance-optimization` | full | keep | The performance playbook measures one bottleneck. This skill is the longer checklist. About 2217 words. |
| `shipping-and-launch` | full | keep | Launch, rollout, rollback. The shipping playbook stays short. About 1583 words. |
| `technical-writing` | builder | keep | About 1910 words. Fires on docs, RFCs, readmes, pull-request descriptions, and commit messages. Wide trigger, and the writing is still the specialist the stack uses for those artifacts. |
| `security-and-hardening` | builder | keep | About 3506 words. Fires on untrusted input, auth, storage, third parties, and any feature that accepts untrusted data. Production mode expects this check. |
| `typescript-best-practices` | builder | keep | About 408 words. Fires on any `.ts` or `.tsx` file. Short enough to leave in the builder profile. |

Do not switch the operator profile from `full` to `builder`. That would also drop CI, migration, observability, performance, and shipping. `git-workflow-and-versioning` left the full list on its own and is optional.

## Machine drift

Not fixed in this repository. Machine config stays outside Git.

- `~/.config/astrobyte-agent-skills/config.json` lists `harnesses: ["codex"]`. Cursor is in active use, and the Git identity table already has a Cursor committer.
- `~/.cursor/skills/unslop` duplicates `~/.agents/skills/unslop`. The Cursor adapter installs into `~/.cursor/skills`, and this machine's installer is Codex-only, so the copy is leftover.

## Actions waiting on the operator

1. Done in the follow-up that adds "Assert public behavior." to the Red section of `astrobyte-tdd`. The audit found that Red only said "one test for the requested behavior."
2. Change the `astrobyte-review` description so it says bloat instead of maintainability.
3. Done. `git-workflow-and-versioning` left the full profile and is now optional.
4. Remove `source-driven-development` from the builder profile.
5. On the next install, add Cursor to this machine's harnesses and drop the extra `unslop` copy.
