# Scoped Sol review

This method runs inside the existing `../astrobyte-review/SKILL.md` procedure. It does not add a second gate. Strongly recommend the newest offered Sol reviewer at the host's default effort; use another reviewer only when the operator's current instruction or recorded preference explicitly selects it.

1. Fix the comparison base, complete diff or artifact set, intent, delivery mode, excluded scope, and available verification. Account for untracked and user-owned work without including unrelated changes.
2. Give one read-only reviewer that brief. Require the existing first-line `PASS` or `BLOCK` verdict with findings and locations. The reviewer neither edits nor starts other reviewers. Keep scoped files stable while it reviews.
3. Keep a small ledger with stable finding ID, severity, claim, evidence, disposition, and status. Reproduce high-impact findings when a cheap proof exists. Fix the smallest justified cause when implementation is authorized; answer disagreements with evidence.
4. Check whether fixes expanded the change beyond the task. For `explore` and `prototype`, defer uncommon, unobserved error paths unless they obstruct the stated question or the operator asks. For durable and production work, judge impact and repository obligations.
5. Re-run affected verification. Later rounds review changed material and unresolved findings, with the full comparison available to understand interactions. Record the revision covered by the verdict. A behavior change after review needs current review evidence.

Start with three total rounds and retain the existing gate's three-blocked-round stop. When the budget ends or a material disagreement persists, present the evidence and ask whether to extend for a bounded number of rounds or finish with the issue unresolved. Timeouts, unclear replies, disagreement, and budget exhaustion are not approval.

Only a current `PASS` satisfying the existing gate permits the action it protects. An explicit Sol-loop request alone does not authorize editing, pushing, or opening a PR. Keep the ledger, verified model identity, rounds, and available usage in the operator report unless repository policy requests them in the PR.
