---
name: astrobyte-verify-project
description: Create or maintain a project-local skill that proves CLI, API, UI, service, model, pipeline, or deployment behavior through the real runtime surface. Use when a repository lacks a repeatable verification path or its verification map has drifted.
metadata:
  opencode/autoinvoke: "false"
---

# Astrobyte verify project

## Discover

Interview the repository before the user. Find:

- primary user and operator surfaces
- setup and launch commands
- health checks and required services
- representative features and data paths
- observable evidence for success and failure
- cleanup and idempotence requirements
- existing tests, smoke scripts, browser flows, benchmarks, and golden artifacts

Ask the user only for choices the repository cannot reveal.

## Create

Create `.agents/skills/verify-<project>/SKILL.md` with:

1. prerequisites and doctor checks
2. deterministic launch steps
3. a feature map from capability to exact drive action and evidence
4. focused verification commands
5. real-surface checks for CLI, HTTP, browser, model, artifact, or deployment as applicable
6. cleanup and recovery
7. known expensive checks and when to run them

When the project needs human acceptance before merge, also define one revision-identifiable preview path appropriate to the product: a private web URL, mobile install link, desktop artifact, CLI invocation, or API smoke target. Include readiness evidence, access boundaries, the exact revision under test, and cleanup. Prefer an existing private project path over adding a hosted preview service.

Use relative paths and portable commands. Keep secrets and machine-specific values in environment variables or local configuration.

## Maintain

1. Compare the feature map with current source, routes, commands, configs, and docs.
2. Drive every mapped feature in one live session when affordable.
3. Correct only drift proven by source or runtime evidence.
4. Add newly important features and remove paths that no longer exist.
5. Run the updated skill from a clean starting state.

The work is complete when another agent can reproduce the verification without undocumented knowledge and every mapped claim has observed evidence.
