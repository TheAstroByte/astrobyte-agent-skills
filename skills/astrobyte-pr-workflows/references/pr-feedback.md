# PR creation, feedback, and replies

## Establish repository policy

Read repository instructions and live check/review requirements. They outrank a saved convenience policy. When no review-bot policy exists, run `scripts/workflow_state.py repository show --repo <host/owner/repo> --base <branch>`. If still unconfigured, ask once whether to use CI-only, named advisory bots, or named required bots. Save the approved `required_bots` and `advisory_bots` lists with `repository set --input <approved-json>`. Empty lists record an explicit CI-only choice. Revisit the selection when repository requirements change.

The saved policy never replaces live branch requirements or human decisions. Bot findings are evidence to verify. A bot's advisory human-review suggestion can be declined with a reason; actual required approval and unresolved human changes requests remain pending.

## File or update a PR

Use the existing publication gate and Git attribution. Inspect the current diff against the actual base and check for an existing PR on the branch. Follow repository title and draft conventions. Preserve the current concise, problem-first description, relevant verification, and material limits. Inspect publishing content for private details. Add no council score table, internal workflow narration, or guessed model identity.

Posting a PR or reply needs authority from the requested task. Creating a PR does not by itself request continuous monitoring; a finish or babysit operation does.

## Babysit

Use `../pr-feedback-loop/SKILL.md`. Keep one monitoring owner for the PR and deduplicate already-handled findings. Confirm the current head before applying feedback and after each push. Existing unresolved relevant findings remain in scope even when older than the latest push.

Use the host's supported watcher when available. If T3 is personally enabled, follow [T3 integration](t3.md). Otherwise, `gh pr checks --watch` can wait for CI checks; it does not watch comments or prove all review requirements have settled. Re-read reviews, threads, base, and head after it returns. Do not claim future wakeups without an active supported mechanism. If feedback monitoring is unavailable, report the current state and that specific limit.

Handle only new or unresolved actionable evidence inside the approved contract. Keep the feedback loop's bounded correction attempts and stop conditions. Recheck required checks, review decisions, base changes, and mergeability on the final head before calling the PR ready. Keep actual approval-pending and blocked states distinct from readiness. This operation leaves merging to the authorized human.

## Reply to findings

Lead with the disposition and cite the code, check, or reproduction. Keep the reply concise and distinguish observations from judgment. Use verified public model or product attribution when the repository or operator requests it. Check private details, preview Markdown, and verify the posted response URL before marking a response as delivered or resolving a thread. Resolve human review requirements only through their actual authorized decision process.
