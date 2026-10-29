---
name: astrobyte-mode
description: Route substantial engineering, ML, GenAI, data, API, backend, frontend, prototype, debugging, evaluation, migration, or long-running work through a task-specific playbook with small changes and real-artifact verification. Use when a task crosses files or boundaries, has meaningful uncertainty, runs unattended, or needs a durable handoff.
---

# Astrobyte mode

## Route

1. Read repository instructions and the relevant current code, data contract, config, or artifact.
2. Resolve file preferences with this skill's `scripts/runtime_config.py --project <project-root>`. Read the packaged [working agreement](references/working-agreement.md), then apply the returned `working_agreement_layers` in order. Portable differences precede legacy local agreements; local deltas follow them. Apply higher-priority machine, project, and task preferences afterward. Follow [configuration.md](references/configuration.md) for precedence. Missing machine configuration uses the packaged [baseline](references/baseline.json) without installation or onboarding. A malformed or explicitly requested missing config is an error to resolve, not permission to discard preferences.
3. Invoke `astrobyte-project-startup` before substantial implementation when initializing a project or when a material stack choice remains unresolved. Preserve a coherent existing stack without forcing a startup interview.
4. Resolve the delivery mode as `explore`, `prototype`, `durable`, or `production` using the configuration precedence. The unmodified baseline selects `durable`. Treat "yolo", "hack it", and "quick prototype" as `prototype`. Ask when the selected value is `ask` or the requested outcome conflicts with the selected mode. Keep routine mode resolution internal. Explain a mode choice to the operator only when it changes the requested scope or requires a decision.
5. Name the outcome, constraints, acceptance evidence, and excluded scope. Inspect available evidence before asking a question. Ask one question only when an unanswered choice would materially change the result.
6. Choose one primary playbook family:
   - Investigation, research, experiment, prototype, hill-climb, or eval: read `references/research-and-ml.md`.
   - Feature, API, full stack, bug, performance, refactor, or migration: read `references/build-and-debug.md`.
   - Review, long run, pause, resume, shipping, or handoff: read `references/operate-and-handoff.md`.
   For new user-facing interfaces or deliberate visual redesigns, including prototypes and design-only requests, also read [frontend guidance](references/frontend.md). Routine repairs that preserve appearance and backend-only tasks stay on their primary playbook.
7. Read `references/principles.md`. Apply only the principles named by the selected playbook.
8. Use the primary harness's native tools. Read `references/harnesses.md` only when delegation, browser control, skill invocation, or transcript recovery depends on the harness.

Workflow skills are installed beside this one. To use a named sibling skill, read `../<skill-name>/SKILL.md` resolved from this file's directory; this path works when a harness only allows explicit invocation, as Codex and OpenCode do for `astrobyte-review`. A missing hard dependency means the workflow installation is incomplete; report the missing skill and installation command rather than substituting a weaker gate. For a conditional specialist, report it only when that branch applies and request installation of that capability. For unavailable or legacy references, read [dependencies.md](references/dependencies.md). Runtime tasks do not invoke setup, adoption, or updates automatically.

The route is complete when one playbook and its evidence standard are explicit.

## Execute

1. Break work into the smallest sequence whose steps each end in a verifiable state.
2. Front-load the riskiest assumption or cheapest discriminating experiment.
3. Keep one active implementation slice. Parallelize only independent reads, candidates, or checks within the configured worker limit.
4. Preserve data provenance, public contracts, user work, and recoverability.
5. Test behavior through the cheapest trustworthy seam. For ML work, separate code correctness from empirical model quality.
6. Verify the actual surface: run the CLI, call the API, inspect the UI, read the produced artifact, measure the metric, or compare runtime output.
7. Record decisions when the run is unattended, empirical, expensive, or likely to be resumed.
8. Before an agent-created pull request or push in `durable` or `production` mode, read `../astrobyte-review/SKILL.md` and run its review gate. The push or pull request waits until that gate records `PASS`. In `explore` and `prototype`, run it when the operator asks for a review.
9. Before an agent-created commit or push, read `../astrobyte-git-identity/SKILL.md` and use it to apply and audit the active agent product's attribution.

Execution is complete when every acceptance claim points to observed evidence.

## Report

Lead operator reports with the outcome, changed artifacts, and observed verification. Include unresolved decisions or next actions only when they matter to the requested result. Apply `unslop` to prose. Create a handoff when another harness or session must continue.

For PR descriptions and comments, describe the concrete problem, resulting behavior, relevant verification, and code risks. Follow the repository's template. Invoking this skill or requesting a demo PR does not request workflow narration. Keep skill names, mode selection, configuration paths, onboarding advice, commit-identity mechanics, and explanations of how this workflow shaped the run out of PR text unless the change itself concerns them or the operator requests them. Report setup failures and attribution blockers directly to the operator before publishing. Preserve material verification limits such as tests that could not run. Recommend follow-up work only when supported by the change, rather than adding speculative CI or setup suggestions.

Harness permissions and user authority remain binding. Configuration can narrow autonomy; it cannot grant new authority.
