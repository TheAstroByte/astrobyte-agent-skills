# Research and ML playbooks

## Investigation

1. State the question and the evidence that can answer it.
2. Inspect code, history, docs, data, logs, and runtime state as relevant.
3. Separate observations from inference.
4. Return the answer, confidence, and the smallest unresolved uncertainty.

Complete when every material claim has a source or observed artifact.

## Research

1. Define the decision the research must support.
2. Prefer primary sources and current official documentation.
3. Compare alternatives against explicit constraints.
4. Save durable findings when another agent or future task will reuse them.

Complete when the decision can be made without repeating the source search.

## Prototype

1. Name the uncertain design question.
2. Build the cheapest disposable artifact that exposes the answer. When the question is whether logic feels right, or what a UI should look like, use the `prototype` skill.
3. Compare 2 to 3 candidates when one attempt would lock in an arbitrary shape.
4. Record what transfers to production and discard accidental prototype structure.
5. Graduating the prototype to `durable` starts with a sketch of the pull-request series.

Complete when evidence resolves the question or identifies the next discriminating experiment.

## Hill-climb

1. Freeze the target metric, guardrails, evaluation data, and compute budget.
2. Establish a reproducible baseline.
3. Change one hypothesis-bearing variable or one coherent treatment at a time.
4. Run a cheap validity check before the full experiment.
5. Accept a change only when the target improves without violating guardrails.
6. Record hypothesis, configuration, result, variance, cost, and decision.
7. Commit each accepted win separately. Revert or isolate rejected trials.

Reserve untouched test data for final confirmation. Complete at the target, budget boundary, or exhausted high-value hypotheses.

## Prompt, model, or skill eval

1. Define representative tasks and blinded scoring criteria.
2. Preserve a no-change baseline.
3. Run candidates under equivalent tools, context, and budgets.
4. Score correctness, supervision, cost, latency, and failure severity.
5. Inspect regressions by task class before choosing a winner.

Complete when the chosen variant wins on the declared decision rule and its regressions are understood.
