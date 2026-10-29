# Principles

Apply the principles named by the selected playbook.

| Principle | Operational rule |
|---|---|
| Smallest sufficient change | Prefer deletion, direct code, and narrow diffs. Add an abstraction when a real repeated shape earns it. Cut bloat: code no current caller needs, including unused fields or constraints, speculative config, compatibility shims, handling for failures nothing raises, and tests of private state. |
| Foundational shape | Settle core data, state, ownership, and concurrency before logic. |
| Domain model | Encode domain states and transitions in structures instead of scattered conditionals. |
| Boundary discipline | Validate at CLI, config, network, file, model, and external API boundaries. Keep typed internal logic direct. |
| Type discipline | Make invalid states difficult to express. Derive types from authoritative schemas where possible. |
| Idempotence | Make retries and partial prior runs converge to the same valid state. |
| Separate shared state | Give concurrent workers separate files, branches, runs, or keys before adding locks. |
| Sequence proof | End each unit in a working, reviewable, and recoverable state. |
| Root cause | Reproduce, localize, explain, fix, and guard the cause. |
| Real artifact | Verify the surface the user or downstream system consumes. |
| Build the lever | Once a repeated recipe is understood, encode it as a script, test, generator, schema, or skill. |
| Friction capture | When the same manual step, clarification, failed handoff, or verification obstacle recurs, record the concrete friction and propose the smallest existing-skill correction, command, or automation that removes it. Do not build speculative process during the active task. |
| Decision trail | Record hypothesis, evidence, decision, and result when future review cannot reconstruct them cheaply. |
| Context control | Summarize bulk evidence. Delegate bounded reads and return conclusions with file or artifact pointers. |
| Safe autonomy | Proceed on reversible work already in scope. Ask before irreversible, destructive, costly, public, or externally visible actions. |
