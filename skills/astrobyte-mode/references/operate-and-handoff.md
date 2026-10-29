# Operate and handoff playbooks

## Review

1. State the intended outcome and fixed comparison point.
2. Review spec fit, repository standards, correctness, security, data integrity, maintainability, and verification evidence.
3. For every agent-created pull request in `durable` or `production` mode, run `astrobyte-review` with the configured reviewer. Add another reviewer for a high-risk or broad change, or when the operator asks.
4. Reproduce or run code for findings that can be proven cheaply.
5. Classify findings as act, consider, note, or dismiss.

Complete when actionable findings are prioritized and unsupported concerns are filtered out.

## Long or unattended run

1. Set the target, budget, stop conditions, checkpoint interval, and authority boundary.
2. Create resumable state and an `astrobyte-show-work` decision trail.
3. Use idempotent steps and isolated outputs.
4. Checkpoint verified wins. Stop on repeated unexplained failure, exhausted budget, or a decision requiring new authority.
5. Keep routine progress in artifacts or process logs. After acknowledging the start, interrupt the operator only for a requested status, a decision, a blocker, a safety issue, or a configured budget threshold. Send one verified completion report by default.
6. Leave the workspace and next action explicit.

Complete at the target or a declared stop condition, with enough state for another agent to resume safely and without requiring the operator to watch the run.

## Pause or resume

On pause, record current branch, worktree state, running processes, artifacts, last evidence, unresolved decision, and exact next command. On resume, verify those facts against live state before acting.

## Shipping

1. Verify the exact revision and artifact intended for release.
2. Run required quality, security, migration, and rollback checks.
3. Confirm monitoring and ownership for the observation window.
4. Perform external release actions only within explicit authority.

Complete when the shipped artifact is identified, verified, observable, and recoverable.

## Handoff

Capture outcome, current state, decisions with rationale, changed artifacts, verification, known risks, and the next safe action. Keep raw logs behind file pointers.
