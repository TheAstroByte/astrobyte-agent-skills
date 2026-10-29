# Build and debug playbooks

## Feature, API, or full stack

1. Name the user-visible outcome and the primary data shape.
2. Inspect existing seams and public contracts.
3. Use `astrobyte-architect` when the work crosses a meaningful boundary.
4. Ship one pull request by default. When the feature spans separable components, sketch the series first: one line per pull request, in dependency order, smallest viable pull request first. Confirm the sketch with the operator.
5. Plan, build, review, and open each pull request one at a time, and stop for the operator after each one. Plan the next pull request in detail only after the previous one merges. Name the files that pull request may touch. The review checks the diff against that list.
6. When a reviewer or the repository points to an existing implementation, copy it and prove the copy with a diff against the source.
7. Implement a thin vertical slice through storage, logic, API, and UI as required.
8. Validate untrusted input at boundaries and preserve authorization, provenance, and error contracts.
9. Verify the real interface and update tests, docs, and examples that describe changed behavior.

Complete when the requested path works end to end and adjacent contracts remain proven.

## Bug

1. Reproduce the symptom with the smallest trustworthy loop.
2. Minimize the failing input or path.
3. Form competing hypotheses and instrument the discriminator.
4. Trace the cause across boundaries instead of patching the last visible symptom.
5. Add a regression test when the seam is clear and affordable.
6. Fix the cause, run the reproduction, then run affected regression coverage.

Complete when the original reproduction is green and the causal explanation fits the evidence.

## Performance

1. Measure the user-relevant baseline and preserve the trace or benchmark.
2. Locate the dominant cost with profiling or instrumentation.
3. Change one bottleneck at a time.
4. Re-measure with equivalent inputs and environment.
5. Check correctness, resource use, and tail behavior.

Complete when the target improves against baseline without a material regression.

## Refactor or migration

1. State the invariant behavior and target structure.
2. Prove current behavior at the affected boundary.
3. Remove dead paths that obscure the target.
4. Move callers in verifiable units. Preserve compatibility only when it is an explicit requirement.
5. Delete obsolete paths once their callers are gone.
6. Verify behavior, documentation, and operational rollback.

Complete when callers converge on the target structure and the old path is either removed or deliberately supported.
