---
name: astrobyte-recall
description: Rebuild where work was left from repo evidence, handoffs, decision trails, and history. Use when resuming work, switching harnesses, or changing machines.
metadata:
  opencode/autoinvoke: "false"
---

# Astrobyte recall

1. Read repository instructions and current Git state.
2. Inspect recent commits, active branches or worktrees, open changes, project handoffs, `.astrobyte/decisions.tsv`, run state, and generated next-step prompts.
3. Use harness session or thread history when available. Treat it as evidence that may be stale.
4. Verify claimed running processes, files, artifacts, tests, metrics, and remote state before relying on them.
5. Separate facts, likely inferences, and unresolved questions.

Return:

- objective
- completed and verified work
- current live state
- decisions and rationale
- uncommitted or external state
- blockers and risks
- exact next safe action
- evidence locations

Recall is complete when another agent can continue without repeating completed work or trusting stale transcript claims.
