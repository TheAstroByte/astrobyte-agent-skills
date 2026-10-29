---
name: astrobyte-project-startup
description: Establish or revise a project's stack and operating assumptions before substantial implementation. Use for greenfield setup, repository bootstrap, prototype kickoff, architecture startup, or when project stack choices are materially unresolved.
---

# Astrobyte project startup

## Inspect

1. Read repository instructions and `.astrobyte/config.json` when present.
2. Inspect manifests, lockfiles, imports, services, containers, CI, deployment files, data formats, and runnable entry points.
3. Classify each relevant choice as `detected`, `confirmed`, `defaultable`, `conflicting`, or `unresolved`.
4. Preserve a coherent existing stack. Treat conflicting evidence as unresolved rather than choosing by file count.

Inspection is complete when observable facts are separated from decisions that require the operator.

## Interview

Read [stack-policy.md](references/stack-policy.md) and consult [project-defaults.json](references/project-defaults.json). When a recommendation depends on a changing tool capability, verify it against current primary documentation, starting from [sources.md](references/sources.md). Ask only questions whose answers materially affect architecture, dependencies, external data transfer, deployment, cost, or verification.

1. Establish project archetype, maturity, expected users, and success evidence.
2. Resolve deployment target, data sensitivity, authentication exposure, and external-provider permissions.
3. Resolve only the stack boundaries still marked conflicting or unresolved.
4. For each question, show the detected evidence, recommend one choice with a short reason, and name the meaningful alternative.
5. Ask one question at a time unless the operator requests a batch. Accept “use the default” without extending the interview.

The interview is complete when implementation can start without an implicit material stack decision.

## Record

1. Summarize the selected stack, inherited choices, exceptions, and unresolved decisions.
2. After confirmation, create or update `.astrobyte/config.json` using [project-config.example.json](references/project-config.example.json) as the shape. Record only relevant fields.
3. Keep the project file portable and safe to commit: exclude secrets, credentials, absolute machine paths, and transient local endpoint values.
4. Point implementation plans to the project file. Reopen the interview only when scope or constraints invalidate a recorded choice.

Startup is complete when the operator has confirmed the material choices and `.astrobyte/config.json` matches that decision. Stack selection does not itself authorize scaffolding, dependency installation, deployment, or external actions.
