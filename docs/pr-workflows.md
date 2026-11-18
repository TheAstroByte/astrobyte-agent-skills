# Optional PR workflows

The optional `astrobyte-workflows` package adds deliberate PR completion, review, and continuation operations. It is absent from every default bundle. A normal quick install keeps its existing behavior.

## Select it during personalization

Ask for the optional PR workflows, or review a delta such as:

```json
{
  "schema_version": 1,
  "baseline": {
    "handle": "astrobyte",
    "repository_version": "0.5.0"
  },
  "overrides": {
    "optional_skills": ["astrobyte-workflows"],
    "pr_workflows": {
      "review_method": "review-loop",
      "council_round_limit": 3,
      "t3": false
    }
  }
}
```

An explicit optional-skill list replaces the saved optional selection. Retain any other optional skills you still want. Omit the list to preserve the existing selection.

Apply the reviewed delta through the existing installation preview:

```bash
python3 scripts/install.py --harnesses cursor --preferences approved-preferences.json
```

Choose your own harness or selected harnesses. Adding a personal preference does not require a full interview or a personal repository. Exact council models and routes remain local. Add `--portable-preferences` only after reviewing and approving the reusable rules for export. Selected packages and their contained resources travel with skill sync; credentials and local setup answers do not.

Selecting `review-loop` changes how the personal independent review gate runs. It does not start council or add a second mandatory review.

### Reviewer choice on first use

The first review on a host asks which model reviews. The agent lists the models the host actually offers, recommends the newest Sol, and waits for you to confirm or pick another independent reviewer. The answer is saved per harness with `astrobyte-review`'s `scripts/reviewer_state.py` and reused while its route is still offered. A reviewer named in the task, project instructions, or machine configuration skips the question. A missing route asks again; it never falls back silently.

### Earlier names

This package was called `astrobyte-pr-workflows`, and the review loop was `sol-loop`. Saved selections and preferences that use the old names keep working: the installer maps the package name and archives the old installed directory, and `sol-loop` resolves to `review-loop`. Invoke the package by its new name; hosts do not alias the old skill name. Personal free-text rules that mention the old path are not rewritten; update them yourself.

## Invoke an operation

Invoke `astrobyte-workflows` with the requested operation using your host's skill syntax. For example, in Codex:

```text
Use $astrobyte-workflows full-stop for this change.
Use $astrobyte-workflows council to review this design.
Use $astrobyte-workflows takeover to continue this PR.
```

The package recognizes operation names, not nine separate installed skills. Your personal agreement may also map a deliberate natural-language request to this entrypoint. Mentioning or discussing an operation does not invoke it.

| Operation | Result |
| --- | --- |
| `full-stop`, `full-send` | Complete the requested task with proof, a review loop, and any authorized PR feedback work. Leave it unmerged and report its actual status. Both names share this behavior. |
| `review-loop` | Review the current change with a stable findings ledger, evidence-backed dispositions, bounded follow-up rounds, and the existing independent verdict. |
| `council` | Obtain independent feedback from explicitly selected models and report agreement or unresolved differences. |
| `takeover` | Verify inherited work and continue the original goal while preserving contributor credit. |
| `modernize` | Reassess an old PR's purpose before updating its branch, reworking it, or recommending closure. |
| `babysit-pr` | Monitor the requested PR, classify feedback, and make authorized fixes through the existing feedback loop. |
| `file-pr` | Create or update the requested PR using existing repository conventions. |
| PR comments | Prepare evidence-backed, attributed replies within the authorized task. |

Finish, council, and takeover operations are explicit-only. Enabled settings and a high-risk change do not invoke them automatically. Neither finish command merges, enables auto-merge, joins a merge queue, or pushes to the default branch. Adding a merge option later requires a new explicit choice; an upstream refresh cannot change that contract.

## First use on a system or repository

On the first council run, inspect the host's offered models and read-only routes, then select the members. Three different providers are useful when available. A single harness can reach multiple providers; installing several harnesses does not establish model access. Save the approved selection locally and ask when a member becomes unavailable.

Council uses the configured round limit, defaulting to three. At the cap, show unresolved findings and offer a bounded extension or a completed report with disagreements recorded. An exhausted budget never means approval.

Read repository review and bot policy before monitoring. When it is missing, ask on first relevant use and save the answer for that repository and base branch. Required human approval remains visible as pending. Advisory requests can be declined with evidence. Keep model scores and internal workflow statistics out of ordinary PR descriptions.

The package's `scripts/workflow_state.py --help` describes the local setup helper. It stores model and review-policy data; it does not call models, run arbitrary commands, or modify GitHub.

## Exploration and prototypes

Finish the question or runnable path the user asked for. Defer uncommon, unobserved error handling unless it affects the actual experiment or the user requests it. Use cheap tests when they help learning. Include the mode and acceptance evidence in review briefs so Sol and council apply the same scope.

An explicit finish operation requests a review loop. It does not silently turn a prototype into a durable implementation, require a PR that was not requested, or create a merge path.

## Optional T3 use

Set `t3` only in the personal policy that wants T3 integration. The package then uses its T3 reference when the relevant native tools are actually available. Keep watcher ownership and wakeups in the host that owns the PR.

The native installer does not currently have a T3 target. Installing for a supported underlying host is not proof of discovery or live monitoring in T3. Verify those capabilities before relying on them. The package reports unavailable routes rather than claiming a watch or review is running.

## Source and maintenance

This is an Astrobyte adaptation of selected procedures from [tstack at the reviewed source pin](https://github.com/t3dotgg/tstack/tree/7de017b3fc9d50c03cf3ecb98fb71e0ca65a78bd). The source's merge behavior, model choices, and review classifications are adapted to the explicit operation and mode contracts above. The watcher script is not redistributed.

See [upstream maintenance](upstreams.md) before refreshing this source. Preserve the package-local source license and validate behavior rather than automatically copying later upstream instructions.
