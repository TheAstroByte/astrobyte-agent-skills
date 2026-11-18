# Continue existing work

## Takeover

Use only for an explicit takeover request. Read the source PR, branch, or conversation and the operator's later corrections. Use `../astrobyte-recall/SKILL.md` to verify the actual head, uncommitted work, artifacts, and outstanding feedback. A handoff is context to verify.

State the original goal before judging its implementation. Continue in place when requested. A replacement PR, imported commits, changed base, closing the original, or scope expansion requires the corresponding task authority. Preserve human authors, coauthors, original links, and the active product's Git attribution. Add new fixes separately when that preserves the inherited credit.

Independently verify the original symptom or intended path and recheck source progress before publication. Use the requested finish point; takeover does not automatically include a PR, council, or merging.

## Modernize

Fetch the relevant remote head and actual base. Record repository, PR state, base, observed head, merge base, and user-owned work. Examine base changes and possible replacement implementations beyond overlapping lines.

Choose a disposition before spending effort on rebase:

- `update`: the goal remains useful and the implementation still fits.
- `rework`: the goal remains useful but the implementation needs a different shape. State the proposed scope before doing unapproved work.
- `recommend-close`: the benefit is superseded or no longer warrants the change. Cite evidence and leave closure to the authorized actor.

For an authorized update, isolate work, rebase onto the current intended base, and resolve conflicts against the goal and current invariants. Use `git range-diff` to inspect preserved intent. Run focused checks and distinguish baseline or infrastructure failures. Before an authorized force-with-lease push, tie the lease to the remote head recorded before rebase. If it fails, fetch and reassess instead of overwriting newer work.

Finish with the disposition, evidence, observed verification, push result if authorized, and remaining decision. A clean rebase alone does not establish that the idea still belongs.
