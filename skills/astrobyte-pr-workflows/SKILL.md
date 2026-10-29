---
name: astrobyte-pr-workflows
description: Explicit PR completion, Sol review loops, councils, and continuation commands.
disable-model-invocation: true
metadata:
  opencode/autoinvoke: "false"
---

# Optional PR workflows

Run the operation the operator requests. Installing this package, mentioning a command in discussion, or encountering a risky change does not invoke a finish command, council, or takeover. A selected personal `review_method: sol-loop` permits the existing review gate to read that method without starting another operation.

1. Read repository instructions and resolve the current delivery mode and acceptance evidence through `../astrobyte-mode/SKILL.md`.
2. Run this package's `scripts/workflow_state.py policy --project <repository>` to read effective personal options. It uses the installed router's resolver; missing dependencies or malformed settings remain errors.
3. Read only the requested branch:

| Operation | Procedure |
| --- | --- |
| `full-stop`, `full-send` | [Finish the task](references/finish.md). Both names currently leave work unmerged. |
| `sol-loop` | [Run scoped independent review](references/sol-loop.md). |
| `council` | [Select and run council](references/council.md). |
| `takeover`, `modernize` | [Continue existing work](references/continuation.md). |
| `babysit-pr`, `file-pr`, `leaving-pr-comments` | [Handle PR work](references/pr-feedback.md). |

Use an operation inside another only when that requested workflow includes it. `full-stop` and `full-send` include scoped Sol review and relevant PR feedback, but never add council. Reuse a current independent verdict instead of reviewing the same change twice.

For `explore` and `prototype`, prove the intended question or runnable path. Defer uncommon, unobserved error handling unless it blocks that goal or the operator requests it. Give reviewers the mode and acceptance evidence. A finish command preserves the quality mode.

Use [T3 integration](references/t3.md) only when the effective `t3` option is true and the relevant tools are available. Other hosts keep their supported native tools. This package does not configure providers, grant external authority, or establish T3 installation support.

Finish with the observed result, exact current revision when relevant, verification, and any remaining decision. Keep internal review ledgers and model statistics in the operator report rather than routine PR prose.

Adapted from [the reviewed tstack source](https://github.com/t3dotgg/tstack/tree/7de017b3fc9d50c03cf3ecb98fb71e0ca65a78bd). Keep its [source license](LICENSE.tstack.txt) with this package.
