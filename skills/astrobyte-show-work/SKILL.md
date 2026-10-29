---
name: astrobyte-show-work
description: Keep a compact, reviewable decision trail for experiments, unattended runs, migrations, evaluations, or multi-phase work. Use when a reviewer will need to understand what changed, why, what evidence was observed, and what was accepted or rejected.
metadata:
  opencode/autoinvoke: "false"
---

# Astrobyte show work

Create `.astrobyte/decisions.tsv` unless the project defines another location. Use one row per decision:

```text
timestamp\tphase\thypothesis_or_choice\tevidence\taction\tresult\tstatus\tartifact
```

Rules:

- Record decisions, not routine commands.
- Link to configs, commits, runs, traces, metrics, tests, or screenshots instead of pasting bulk output.
- Use `accepted`, `rejected`, `inconclusive`, or `blocked` as status.
- Record failed and rejected work when it prevents repetition.
- Keep secrets, tokens, personal data, and raw sensitive inputs out of the log.
- Commit the trail only when it is part of the review or reproducibility contract.

Before ending, ensure the final row identifies the current state and next safe action. The trail is complete when another agent can explain the decision sequence without reading the full transcript.
