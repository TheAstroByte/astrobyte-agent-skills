# Explicit council

Council runs only when the operator requests it. Establish whether the task is review, exploration, or implementation with review. An audit-only request authorizes inspection; known findings do not authorize implementing fixes.

## First use on this system

1. Discover the current host's actual read-only delegation and model routes. A model's public name does not establish access.
2. Run `scripts/workflow_state.py council show --harness <host>`. If no selection exists, ask for the council members from available routes. Offer Sol strongly where available, Opus where available, and ask for the third model. Prefer provider diversity when desired; do not guess a third model or install another harness silently.
3. After the choice, save it with `council set --harness <host> --input <approved-json>`. The input is an object containing `members`, each with `model` and `route`, and optional `label` and `provider`. Store actual offered model identifiers and route labels, never credentials or shell commands. The helper's `--help` describes its arguments.
4. On later runs, verify each saved route is still available. A missing member requires a replacement choice or permission to run with a smaller council. Local route selections do not travel with portable personal policy.

## Review rounds

Give the selected members the same intent, revision, mode, acceptance evidence, and excluded scope. Delegates stay read-only and do not start more reviewers. For a review, run relevant available checks and disclose known findings before dispatch. Prepare fixes only when implementation is already in scope.

Use the effective `council_round_limit`, default three. One round is a review pass by the selected members over the agreed revision. Collect evidence-backed findings, disagreements, and limits rather than scores. The lead verifies claims against the actual artifact and preserves scope.

After authorized fixes, focus later rounds on changed material and unresolved findings. For prototypes and exploration, uncommon, unobserved error handling is non-blocking unless it prevents the intended result or the operator asks.

At the cap, show resolved findings, remaining disagreements with evidence, current revision, blockers, and available usage. Ask whether to continue for two more rounds, finish with disagreements recorded, or narrow the question. Honor another bounded extension if selected; do not reset the budget automatically. Keep effort at the host default unless explicitly configured.

A completed report with disagreement is valid. It does not claim consensus or satisfy another gate. Reuse a council member's Sol verdict for `astrobyte-review` only when that configured reviewer received the required brief and returned its required verdict for the current change. Council alone grants no publication or merge authority.
