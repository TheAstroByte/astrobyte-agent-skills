---
name: astrobyte-review
description: Review a change against intent, repository standards, correctness, security, data integrity, maintainability, and real verification evidence. Use for PRs, branches, diffs, risky artifacts, or explicit adversarial review.
metadata:
  opencode/autoinvoke: "false"
---

# Astrobyte review

1. Fix the comparison point and gather the complete diff or artifact set.
2. State the intended outcome from the request, issue, spec, commit history, and code.
3. Read repository standards and affected contracts. Resolve delivery and review preferences from this skill's `scripts/runtime_config.py --project <project-root>` and [configuration.md](references/configuration.md). Missing local configuration uses the packaged [review policy](references/review-policy.json) without onboarding. Apply current instructions and project evidence before personal defaults.
4. Review these axes:
   - intent and acceptance criteria
   - correctness and edge cases
   - data integrity, provenance, and migrations
   - security and trust boundaries
   - public interfaces and compatibility
   - bloat. See principles.
   - tests and real-runtime evidence
   - documentation and operational recovery
   - PR text. Describe the change and its verification for repository reviewers. Remove internal workflow narration and unrelated setup advice while retaining material code risks and verification limits.
5. Run a focused proof for any high-impact finding that can be checked cheaply.
6. In `durable` and `production` modes, run the review gate before an agent-created pull request or push. In `explore` and `prototype`, run it when the operator asks for a review.
   - Start with the packaged review policy. Apply the returned `working_agreement_layers` in order, including their review instructions. Portable differences precede legacy local agreements; local deltas follow them. Apply higher-priority machine, project, and task preferences afterward. Resolve the preferred reviewer against the models the current harness actually offers. Read [reviewer-dispatch.md](references/reviewer-dispatch.md) when dispatch depends on the harness. If the configured reviewer model or read-only delegation is unavailable, report the blocker and keep the gate pending; the push or pull request waits. Do not propose or select another model, and do not substitute self-review. A different reviewer applies only when the operator's current instruction or a recorded review preference names it. Missing configuration is not a reason to skip the gate.
   - Send that reviewer one read-only strict brief: the intent, the comparison point, the diff, and any external feedback the change must satisfy. Ask for a first line of exactly `PASS` or `BLOCK`, followed by findings with file locations. Any other reply has not passed, and never infer a verdict from the wording. Ask the reviewer once for its verdict; if the second reply is also unclear, report the gate pending and the push or pull request waits.
   - On `BLOCK`, when this run is also implementing the change, fix the finding. When the finding conflicts with the spec, a cited pattern, or a human reviewer's instruction, send that evidence back and ask for a re-ruling. The reviewer stays read-only.
   - A fresh review must return `PASS`. Stop and report after three blocked rounds.
7. Synthesize as lead reviewer. Deduplicate findings and account for missing context.

Start the report with a decision layer that states:

- the practical problem;
- the smallest recommended action;
- why it works;
- what remains risky or unproven;
- the exact decision or action required from the operator.

Keep detailed findings and evidence below that layer or behind artifact links.

Classify each item:

- `act`: blocks correctness, safety, data integrity, or the requested outcome
- `consider`: real tradeoff that may be worth addressing
- `note`: valid context with low present impact
- `dismiss`: incorrect, unsupported, or out of scope

Lead with `act` findings ordered by severity and include file or artifact locations. State when no actionable findings remain. Do not apply changes unless the user also requested implementation.
