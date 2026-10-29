# Finish the task and leave it unmerged

`full-stop` and `full-send` are aliases for this procedure. Future merge support requires a new explicit opt-in; an upstream refresh must not change their existing authority.

1. Fix the goal, repository, branch, delivery mode, acceptance evidence, and requested external actions from the task and repository instructions. Resolve a material missing choice before its dependent action. Preserve user-owned work and use an isolated branch or worktree when needed.
2. Complete the smallest implementation that meets the goal. In exploration, the result can be an evidence-backed answer. In a prototype, it can be a disposable runnable artifact. Create a PR only when that is part of the requested outcome.
3. Observe the result directly through the relevant CLI, API, UI, experiment, or produced artifact. Run proportionate checks and record limits. Do not promote a prototype to production requirements merely to complete this operation.
4. Use [Sol loop](sol-loop.md) for scoped independent review. Apply the existing `astrobyte-review` gate and verdict rules. Reuse a verdict only if its required brief and evidence cover the current change.
5. For an authorized PR, follow [PR work](pr-feedback.md) to create or update it and handle CI and findings. Before each push to an existing PR, check for auto-merge or queue state that could cause that push to merge it. If the promised unmerged result cannot be maintained within task authority, stop before the triggering action.
6. Read back the final head, base, checks, review state, draft state, and mergeability. Report one of `ready`, `waiting for required approval`, or `blocked`, with evidence. If someone else merged or closed it, report that live state instead.

Leave the PR unmerged. Neither alias enables auto-merge, enters a merge queue, pushes to the default branch, or delegates a merge. Keep actual human requirements visible; an advisory bot's request for human review can be declined with a reason when repository policy permits it.

Use the existing Git attribution helper for commits and the independent gate before required publication. End with the PR or artifact link, final revision, observed verification, unresolved findings, and the next decision. For an unattended run, keep routine waiting quiet and request input through the host's supported question mechanism when a real blocker needs it.
