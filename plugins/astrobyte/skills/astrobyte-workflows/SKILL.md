---
name: astrobyte-workflows
description: Council and review-loop operations. Use only when the operator asks for one by name.
disable-model-invocation: true
metadata:
  opencode/autoinvoke: "false"
---

# Astrobyte workflows

Run the operation the operator requests. Installing this package, mentioning a command in discussion, or encountering a risky change does not invoke council or a review loop. A selected personal `review_method: review-loop` permits the existing review gate to read that method without starting another operation. The older name `sol-loop` means the same operation.

1. Read repository instructions and resolve the current delivery mode and acceptance evidence through `../astrobyte-mode/SKILL.md`.
2. Run this package's `scripts/workflow_state.py policy --project <repository>` to read effective personal options. It uses the installed router's resolver; missing dependencies or malformed settings remain errors.
3. Read only the requested branch:

| Operation | Procedure |
| --- | --- |
| `review-loop` | [Run scoped independent review](references/review-loop.md). |
| `council` | [Select and run council](references/council.md). |

This package contains council and review-loop only. Finish, takeover, and PR-feedback operations are in the full skill collection. Reuse a current independent verdict instead of reviewing the same change twice.

For `explore` and `prototype`, prove the intended question or runnable path. Defer uncommon, unobserved error handling unless it blocks that goal or the operator requests it. Give reviewers the mode and acceptance evidence.

Use [T3 integration](references/t3.md) only when the effective `t3` option is true and the relevant tools are available. Other hosts keep their supported native tools. This package does not configure providers, grant external authority, or establish T3 installation support.

Finish with the observed result, exact current revision when relevant, verification, and any remaining decision. Keep internal review ledgers and model statistics in the operator report rather than routine PR prose.

Adapted from [the reviewed tstack source](https://github.com/t3dotgg/tstack/tree/7de017b3fc9d50c03cf3ecb98fb71e0ca65a78bd). Keep its [source license](LICENSE.tstack.txt) with this package.
