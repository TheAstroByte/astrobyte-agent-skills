# Agent skill stack assessment

Assessment date: 19 August 2026

## Frontend design addition, 15 October 2026

Add Anthropic's `frontend-design` to `builder` and `full` alongside `frontend-ui-engineering`. The [pinned official instructions](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/SKILL.md) supply a visual-design process that complements the engineering specialist. The [package license](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/LICENSE.txt) is Apache-2.0, and [upstream history](https://github.com/anthropics/skills/commits/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design) makes maintenance reviewable.

Independent feedback is mixed. In [a public discussion](https://www.reddit.com/r/ClaudeCode/comments/1qg7slp/which_claude_skills_for_frontend_design_are_good/), `matsuri2057` reports underwhelming results and asks for stronger accessibility guidance. This is anecdotal feedback about an earlier version, not evidence against the pinned snapshot. Theo's endorsement has not been verified here, and no controlled quality improvement is claimed. Keep engineering and browser checks alongside the design instructions. The integration decision follows the operator's requested coverage; future visual outcomes can test its usefulness.

The assessment below retains its original date and scope.

Sources reviewed:

- The current `main` branches of [Cursor pstack](https://github.com/cursor/plugins/tree/main/pstack) and [Matt Pocock's skills](https://github.com/mattpocock/skills)
- Every active skill exposed in this Codex session
- The fish-classifier repository, especially `AGENTS.md`, `README.md`, `docs/AUTORESEARCH.md`, tests, campaign runner, FastAPI dashboard, React frontend, experiment configs, deployment code, and recent commit history
- Official skill documentation for [Codex](https://learn.chatgpt.com/docs/build-skills), [OpenCode](https://opencode.ai/docs/skills), [Claude Code](https://code.claude.com/docs/en/slash-commands), and the [Agent Skills specification](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx)
- Public reviews, usage reports, repository issues, and recent research listed near the end of this report

## Executive decision

Do not install every skill globally. Build a small shared core, keep specialist skills available, and make the expensive orchestration skills explicit-only.

The best setup for this work is a hybrid:

1. Use pstack's operating model as the base: task-shape routing, small verified changes, real-artifact proof, hill-climbing, decision trails, and resumable work.
2. Use Matt's primitives for requirements, domain language, architecture, diagnosis, TDD, research, and handoffs.
3. Retain Addy skills only where Matt and pstack leave a real gap: API design, security, observability, CI/CD, deployment, frontend work, browser testing, migrations, performance, Git, and source-grounded implementation.
4. Keep the native document, spreadsheet, slide, PDF, browser, Sites, and Hugging Face skills. They are narrow specialists rather than competing workflow systems.
5. Replace `using-agent-skills` with a portable personal router derived from Poteto Mode. Call it `astrobyte-mode`. It should work from `~/.agents/skills` for Codex and OpenCode, with small harness adapters for Cursor, Claude Code, and Hermes.

`unslop` is already installed in Codex and should remain always active.

## What the fish-classifier example reveals

The repository is a useful proxy for the daily job because it combines:

- scientific search across model families, losses, image sizes, seeds, and deployment budgets
- long-running and resumable experiment campaigns with explicit state
- data contracts, taxonomy stability, split integrity, provenance, and pseudo-label review
- Python packaging, CLI design, FastAPI, React, TypeScript, Docker, MLflow, and browser testing
- ONNX, Core ML, LiteRT, ExecuTorch, checksums, golden fixtures, and runtime parity
- tests, runbooks, decisions, configs, dashboards, handoffs, and small checkpoint commits

The highest-value skills therefore help an ML specialist make disciplined software decisions, operate long experiments safely, and prove results against real artifacts. Generic code-generation prompts are lower value.

## Recommended target stack

| Capability | Preferred source | Recommendation | Replaces or complements |
|---|---|---|---|
| Main router | Custom `astrobyte-mode`, derived from pstack | Port Poteto's task-shape router, selected principles, and playbooks. Add Codex, OpenCode, Cursor, Claude Code, and Hermes adapters plus your approval boundaries. | Replace Addy `using-agent-skills`, `incremental-implementation`, and most implicit workflow routing. |
| Requirements and challenge | Matt `grilling`, `to-questionnaire` | Install. Keep explicit when the request is already clear. | Replace Addy `interview-me`; largely replace `idea-refine`. |
| Domain and decisions | Matt `domain-modeling` | Install. Use `CONTEXT.md` only where project vocabulary is genuinely costly. | Replace most of Addy `documentation-and-adrs`; complement pstack domain principles. |
| Architecture | Matt `codebase-design` plus ported pstack `architect` | Install Matt directly; adapt pstack's orchestration. | Keep Addy `api-and-interface-design` for HTTP and public contract details. |
| Research | Matt `research` plus Addy `source-driven-development` | Install Matt. Keep Addy. | Strong fit for LLM, ML, library, and API work. |
| Experiment improvement | pstack hill-climb and eval playbooks | Put inside `astrobyte-mode`. | Direct match for model campaigns, prompt evaluation, latency, accuracy, and cost optimization. |
| Diagnosis | Matt `diagnosing-bugs` plus pstack runtime and trace playbooks | Install Matt; port pstack playbooks. | Replace Addy `debugging-and-error-recovery`. |
| TDD | Matt `tdd` with pstack's cheap-test escape hatch | Install a merged version. | Replace Addy `test-driven-development`; avoid forcing expensive ML integration tests before every change. |
| Implementation | pstack feature/refactor playbooks | Put inside `astrobyte-mode`. | Replace Addy `incremental-implementation`; skip Matt's very thin `implement`. |
| Review | Matt `code-review`, pstack `blast-radius`, ported `interrogate` | Install `blast-radius`; install Matt review explicit-only; adapt `interrogate`. | Replace Addy `code-review-and-quality` and `doubt-driven-development`. |
| Runtime verification | Port pstack `create-verification-skill` and `maintain-verification-skill` | High priority. Generate repo-local verification skills for CLI, API, UI, and deployed artifacts. | Complements browser testing and tests. |
| Long-running work | Port pstack `show-me-your-work`, session pickup, pause, autonomous, and orchestration playbooks | High priority, explicit-only. | Fits overnight experiments and cross-agent continuation. |
| Writing | pstack `unslop`, `technical-writing`; Matt `writing-for-agents` | Keep `unslop`; install the other two. | Replace Addy `context-engineering` and most documentation workflow prose. |
| API, security, operations | Selected Addy specialists | Keep. | Matt and pstack do not cover these areas deeply enough. |
| ML execution | Existing Hugging Face skills | Keep most enabled. | Native domain tools with little workflow overlap. |

## Portability model

| Label | Meaning |
|---|---|
| Portable | Standard `SKILL.md` instructions with ordinary filesystem and shell assumptions. |
| Adapt | The idea travels, but tool names, paths, model routing, or side-effect rules need a harness adapter. |
| Harness-specific | Keep it only in the named product unless rewritten. |
| Native | Supplied by the current Codex or plugin runtime. |

The best shared home on this machine is `~/.agents/skills`. Codex and OpenCode both discover that location. OpenCode also reads `~/.config/opencode/skills`, `~/.claude/skills`, and project `.agents/skills` directories. Claude Code's preferred global path is `~/.claude/skills`; Cursor packages pstack as a plugin. A small sync script is safer than symlink assumptions across every product.

Pstack needs special treatment. Its `disable-model-invocation` field is meaningful in Cursor and Claude Code, while OpenCode ignores unknown frontmatter. Installing all 21 principle skills raw into OpenCode would advertise many tiny, overlapping routes that pstack intended the router to call internally. Bundle those principles as references inside `astrobyte-mode` instead.

## Astrobyte-owned and adapted skills in v0.3

These skills complete the current catalog. The later source tables review every retained Matt, pstack, Addy, native, and Hugging Face skill.

| Skill | Source shape | Decision and reason |
|---|---|---|
| `adopt-skill-stack` | Astrobyte, using Matt's agent-writing mechanics and pstack's verification discipline | Add, explicit-only. It converts an interview into a reviewed personal repository and machine setup without storing raw answers. |
| `update-skill-stack` | Astrobyte | Add, explicit-only. It preserves personal profiles and custom skills while reviewing upstream behavior and license changes. |
| `setup-astrobyte-skills` | Astrobyte | Keep. It owns transactional installation on one machine after adoption. |
| `astrobyte-mode` | Astrobyte router derived from pstack | Keep. It replaces the overlapping general Addy workflow and routes work by task shape and delivery mode. |
| `astrobyte-project-startup` | Astrobyte | Keep. It preserves coherent projects and resolves only material greenfield stack choices. |
| `astrobyte-git-identity` | Astrobyte | Add. It gives agent-created commits dual human and product attribution without relabeling later human commits. |
| `astrobyte-tdd` | Adapted from Matt and pstack | Keep. It combines seam-first red-green-refactor with an escape for expensive or unclear test seams. |
| `astrobyte-architect` | Adapted from pstack and Matt | Keep. It combines types-first architecture with deep-module design. |
| `astrobyte-verify-project` | Adapted from pstack | Keep. It creates and maintains repository-specific checks for actual CLIs, APIs, interfaces, and artifacts. |
| `astrobyte-show-work` | Adapted from pstack | Keep. It records decisions and evidence for experiments and unattended work without forcing routine logging. |
| `astrobyte-review` | Adapted from pstack and Matt | Keep. It separates standards and specification review, then requires evidence for actionable findings. |
| `astrobyte-recall` | Adapted from pstack and Matt | Keep. It reconstructs a resumable state across sessions and agent products. |

## Already installed skills

### Personal workflow skills

| Installed skill | Daily fit | Decision | Comparison |
|---|---:|---|---|
| `api-and-interface-design` | High | Keep | Best current specialist for REST, GraphQL, public contracts, versioning, pagination, and frontend/backend boundaries. Matt and pstack help shape modules but do not replace this detail. |
| `browser-testing-with-devtools` | High | Keep | Essential for full-stack prototypes and dashboards. Complements verification skills. |
| `ci-cd-and-automation` | Medium | Keep | Neither candidate library has comparable CI/CD breadth. |
| `code-review-and-quality` | High | Replace | Matt review gives standards/spec separation; pstack adds blast-radius and adversarial review. The installed skill is broad and much longer. |
| `code-simplification` | High | Replace | Poteto's laziness, subtract-first, reader-load, and domain principles are a cleaner set when bundled in the router. |
| `context-engineering` | High | Replace after port | Matt `writing-for-agents`, `handoff`, and domain docs fit the actual multi-agent pattern with less generic process. |
| `debugging-and-error-recovery` | High | Replace | Matt's reproduce, minimize, hypothesize, instrument, fix, regression-test loop is tighter. Pstack adds runtime and trace forensics. |
| `deprecation-and-migration` | Medium | Keep | Pstack has useful migration principles but lacks this skill's lifecycle and communication coverage. |
| `documentation-and-adrs` | High | Replace after port | Use Matt `domain-modeling` for glossary and decisions, plus pstack `technical-writing` for document quality. |
| `doubt-driven-development` | Medium | Replace | Use pstack `interrogate` for explicit high-risk adversarial review. Continuous adversarial review is costly for routine work. |
| `frontend-ui-engineering` | High | Keep | Important coverage for an ML specialist building UIs outside the core expertise. |
| `git-workflow-and-versioning` | High | Keep | Broader and more portable than the candidate Git fragments. |
| `idea-refine` | Medium | Replace | Matt `grilling`, `to-questionnaire`, and `prototype` cover divergent thinking with clearer outputs. |
| `incremental-implementation` | High | Replace | Poteto's feature/refactor playbooks and sequence-verifiable-units principle give a stronger execution contract. |
| `interview-me` | High | Replace | Matt `grilling` is smaller, more composable, and widely used. Adapt it to research the repo before asking questions. |
| `observability-and-instrumentation` | High | Keep | Critical for APIs, production ML, and long-running jobs. No full replacement in either candidate set. |
| `performance-optimization` | High | Keep | Pair it with pstack perf, runtime-forensics, trace-forensics, and hill-climb playbooks. |
| `planning-and-task-breakdown` | High | Replace | Matt `to-tickets` gives vertical tracer slices; pstack handles multi-phase and autonomous work. |
| `security-and-hardening` | High | Keep | Important gap in both candidate libraries. |
| `shipping-and-launch` | Medium | Keep | Pstack shipping is Graphite and Cursor oriented; the installed skill is more general. |
| `source-driven-development` | High | Keep | Strong complement to Matt `research`, especially for fast-moving LLM and framework APIs. |
| `spec-driven-development` | High | Replace | Matt `grilling` plus `to-spec` is leaner. Keep specs proportional to uncertainty. |
| `test-driven-development` | High | Replace | Merge Matt's seam-first TDD loop with pstack's rule to skip forced TDD when the test path is unclear or expensive. |
| `unslop` | High | Keep, already installed | Required. Portable and low conflict. |
| `using-agent-skills` | High | Replace | A personal pstack-derived router should own task routing and reference the selected skills directly. |

### Codex system and artifact skills

| Installed skill | Daily fit | Decision | Comparison |
|---|---:|---|---|
| `imagegen` | Medium | Keep | Native image generation and editing; no candidate overlap. |
| `openai-docs` | High | Keep | Required for current OpenAI product and API guidance. |
| `plugin-creator` | Low | Keep available | Narrow system capability; little routing cost and no overlap. |
| `skill-creator` | High | Keep | Needed to build and maintain `astrobyte-mode` and portable adaptations. |
| `skill-installer` | High | Keep | Required for safe installation and updates. |
| `browser:control-in-app-browser` | High | Keep | Useful for signed-in browsing and local UI testing. |
| `documents:documents` | High | Keep | Day-to-day reports and Word deliverables. |
| `pdf:pdf` | High | Keep | Paper, report, and PDF inspection with visual verification. |
| `presentations:Presentations` | High | Keep | Common data-science communication output. |
| `spreadsheets:Spreadsheets` | High | Keep | Core analysis and business handoff format. |
| `spreadsheets:excel-live-control` | Medium | Keep | Narrow trigger; useful when Excel is active. |
| `template-creator:template-creator` | Medium | Keep | Useful for repeatable stakeholder artifacts. |
| `plugin-management:plugin-management` | Medium | Keep | Native capability for connectors and plugin lifecycle. |
| `sites:sites-building` | High | Keep | Useful for prototypes, internal tools, dashboards, and lightweight full-stack delivery. |
| `sites:sites-hosting` | Medium | Keep | Completes the Sites deployment path. |
| `visualize:visualize` | High | Keep | Useful for comparisons, model results, simulations, and explanatory tools. |

### Hugging Face plugin skills

| Installed skill | Daily fit | Decision | Comparison |
|---|---:|---|---|
| `hugging-face:hf-cli` | High | Keep | Core Hub operations. |
| `hugging-face:huggingface-community-evals` | High | Keep | Direct fit for model evaluation. |
| `hugging-face:huggingface-datasets` | High | Keep | Direct fit for dataset inspection and retrieval. |
| `hugging-face:huggingface-gradio` | High | Keep | Strong bridge from ML code to usable prototypes. |
| `hugging-face:huggingface-jobs` | High | Keep | Cloud compute, batch work, experiments, and GPU workloads. |
| `hugging-face:huggingface-llm-trainer` | High | Keep | Direct fit for LLM fine-tuning and preference optimization. |
| `hugging-face:huggingface-paper-publisher` | Low | Explicit-only or disable | Useful only when publishing research pages. |
| `hugging-face:huggingface-papers` | High | Keep | Direct fit for AI paper analysis. |
| `hugging-face:huggingface-trackio` | High | Keep | Experiment metrics, dashboards, and alerts. |
| `hugging-face:huggingface-vision-trainer` | Medium | Keep | Strong when the task involves vision; fish-classifier is one example. |
| `hugging-face:transformers-js` | Medium | Keep | Useful when a prototype needs browser or Node inference. |

## Pstack: every skill reviewed

### Workflow and utility skills

| Pstack skill | Fit | Portability | Decision and reason |
|---|---:|---|---|
| `Poteto Mode` | Core | Cursor native; adapt elsewhere | Use pstack directly in Cursor. Port its router and relevant playbooks to `astrobyte-mode` for Codex, OpenCode, and Hermes. Raw use elsewhere hardcodes Cursor tasks, models, paths, agents, Graphite, and external skills. |
| `architect` | High | Adapt | Strong types-first and module-shape workflow. Adapt subagent and model calls. Pair with Matt `codebase-design`. |
| `arena` | Medium | Adapt | Valuable for competing prototypes, prompt variants, UI alternatives, and architecture forks. Explicit-only because parallel candidates cost time and tokens. |
| `automate-me` | High | Adapt | Excellent route to a personal working-mode skill. Replace Cursor transcript paths and built-ins with each harness's history and skill creator. |
| `blast-radius` | High | Portable | Install. It looks beyond the diff and proves one safety fact with real code. Useful for data contracts, deployment formats, and shared APIs. |
| `bro` | Low | Portable | Skip by default. Handy as an explicit rewrite command, but `unslop` and normal clarification cover most cases. |
| `create-verification-skill` | High | Adapt | Port early. Generate repo-local controls for CLI, service, UI, and ML artifacts. Replace `.cursor/skills` with the portable project skill location. |
| `figure-it-out` | High | Mostly portable | Add after porting `show-me-your-work`. Strong fallback for migrations and unattended work that do not fit a standard playbook. |
| `how` | High | Adapt | Useful onboarding and architecture walkthrough. Replace hardcoded multi-model subagent calls. |
| `interrogate` | High | Adapt | Use explicit-only for risky diffs, security, data contracts, and deployment. Configure models per harness and preserve lead synthesis. |
| `maintain-verification-skill` | High | Adapt | Port with `create-verification-skill`. Particularly useful as CLIs, dashboards, and deployment targets evolve. |
| `no-comments` | Medium | Cursor native; adapt elsewhere | The constraint-encoding idea is good. The named Comment Sicko agent is Cursor-specific. Avoid a blanket ban on useful rationale comments. |
| `recall` | High | Adapt | Valuable across Codex, OpenCode, Cursor, and Claude sessions. Each harness needs its own transcript or thread adapter. |
| `reflect` | Medium | Adapt | Useful after expensive failures or long projects. Explicit-only; routine reflection can create noisy skill churn. |
| `setup-pstack` | Medium | Cursor-specific | Install only with pstack in Cursor. A separate portable config is needed for Codex and OpenCode model names. |
| `show-me-your-work` | High | Adapt | Port. Decision TSVs fit experiment campaigns and unattended engineering. Store locally by default and commit only when review value warrants it. |
| `swarm` | Medium | Adapt | Useful for independent dataset slices, package checks, review coverage, and research surveys. Explicit-only and bounded. |
| `tdd` | High | Portable | Keep its pragmatic trigger policy, but use Matt's fuller red-green workflow as the main implementation. |
| `teach` | Medium | Adapt | Useful for unfamiliar backend and frontend systems. Depends on adapted `how` and `why`. |
| `technical-writing` | High | Portable | Install. Diataxis, developer style, controlled instructions, and global English improve docs beyond what `unslop` covers. |
| `typescript-best-practices` | High | Portable | Install. High value because TypeScript/full-stack work is outside the main expertise. |
| `unslop` | Core | Portable | Installed and required. |
| `why` | High | Adapt | Strong evidence model across Git, tickets, docs, chat, observability, errors, and analytics. Connector discovery and model calls need harness adapters. |

### Principle skills

Install these as references inside `astrobyte-mode`, not as 21 standalone global skills. That preserves the ideas without flooding skill discovery.

| Pstack principle | Fit | Decision and reason |
|---|---:|---|
| `principle-boundary-discipline` | Core | Bundle. Direct fit for data ingestion, config parsing, APIs, model runtimes, and pure core logic. |
| `principle-build-the-lever` | High | Bundle. Strong for experiment generators, evaluation scripts, migration tools, and reproducible checks. Apply only after the recipe is understood. |
| `principle-encode-lessons-in-structure` | High | Bundle. Turn repeated agent corrections into tests, schemas, lints, metadata, or scripts. |
| `principle-exhaust-the-design-space` | High | Bundle. Especially useful for prototype UIs, agent prompts, model choices, and uncertain architecture. Keep the 2 to 3 candidate cap. |
| `principle-experience-first` | Medium | Bundle for product work. It matters for prototypes and dashboards, less for internal model code. |
| `principle-fix-root-causes` | Core | Bundle. Pair with Matt diagnosis. |
| `principle-foundational-thinking` | Core | Bundle. Data shapes, state, ownership, and concurrency deserve attention before implementation. |
| `principle-guard-the-context-window` | High | Bundle with harness-specific delegation. Important for large datasets, logs, papers, and codebases. |
| `principle-laziness-protocol` | Core | Bundle. Small diffs and deletion bias counter overbuilt agent code. |
| `principle-make-operations-idempotent` | Core | Bundle. Critical for training campaigns, pseudo-labeling, batch APIs, retries, and deployments. |
| `principle-migrate-callers-then-delete-legacy-apis` | Medium | Bundle. Good default for internal APIs; exempt deliberate public deprecation windows. |
| `principle-minimize-reader-load` | High | Bundle. Helps keep ML pipelines and service glue understandable. |
| `principle-model-the-domain` | Core | Bundle. Species, splits, runs, artifacts, deployment variants, and review states should be explicit structures. |
| `principle-never-block-on-the-human` | Medium | Adapt before bundling. Preserve autonomy for reversible in-scope work, but keep Codex approval rules and avoid external side effects without authority. |
| `principle-outcome-oriented-execution` | Medium | Bundle for planned migrations. Avoid when compatibility is a real product requirement. |
| `principle-prove-it-works` | Core | Bundle. Tests, actual CLI/API/UI runs, model artifacts, and runtime parity all matter. |
| `principle-redesign-from-first-principles` | High | Bundle. Prevents repeated bolt-ons when a new requirement changes the data model. |
| `principle-separate-before-serializing-shared-state` | High | Bundle. Useful for parallel agents, experiment runners, files, queues, and database writes. |
| `principle-sequence-verifiable-units` | Core | Bundle. Fits small commits, campaign waves, migrations, and cross-agent handoffs. |
| `principle-subtract-before-you-add` | High | Bundle. Reduces dead paths before features and refactors. |
| `principle-type-system-discipline` | High | Bundle. Strong for TypeScript, Python typing, Pydantic models, schemas, and generated contracts. |

## Matt Pocock: every skill reviewed

### Engineering skills

| Matt skill | Fit | Portability | Decision and reason |
|---|---:|---|---|
| `ask-matt` | Low | Adapt | Skip. A personal router supersedes it, and a public issue reports that it sometimes described other skills without checking them. |
| `code-review` | High | Adapt | Install explicit-only. Standards and spec are useful separate axes. Subagent calls need harness mapping, and review still needs correctness, security, and runtime evidence. |
| `codebase-design` | Core | Portable | Install. Deep modules, narrow interfaces, seams, and testability are excellent guidance for unfamiliar backend and full-stack work. |
| `diagnosing-bugs` | Core | Mostly portable | Install. Its disciplined feedback loop is the best standalone debugger in the compared sets. Adapt background-agent details where needed. |
| `domain-modeling` | Core | Portable | Install. Shared vocabulary and selective ADRs reduce ambiguity across humans and agents. |
| `grill-with-docs` | High | Portable composition | Install explicit-only after `grilling` and `domain-modeling`. It is a thin wrapper, so its value depends entirely on those dependencies. |
| `implement` | Low | Portable | Skip. It is too thin to add value beside `astrobyte-mode`, TDD, and review. |
| `improve-codebase-architecture` | High | Adapt | Install explicit-only. The deep-module scan and visual report are useful for unfamiliar systems. It depends on several other Matt skills and a capable harness. |
| `prototype` | Core | Mostly portable | Install. Throwaway empirical prototypes are valuable for UI, state models, model-serving paths, and uncertain design questions. |
| `research` | Core | Mostly portable | Install. Primary-source, cited repo artifacts fit LLM, GenAI, libraries, model choices, and technical due diligence. Adapt background-agent calls. |
| `resolving-merge-conflicts` | Medium | Portable | Keep explicit-only. Concise and useful, though Addy's Git skill already covers the broader workflow. |
| `setup-matt-pocock-skills` | Medium | Adapt | Keep explicit-only and run per repository only when using Matt's issue and domain workflow. Do not impose issue-tracker scaffolding on every experiment repo. |
| `tdd` | Core | Portable | Install a merged edition with pstack's cheap-test exception. Strong seam-first red-green-refactor loop. |
| `to-spec` | High | Adapt | Install explicit-only. Good synthesis after discussion. Publishing to trackers must respect user authority and configured tooling. |
| `to-tickets` | High | Adapt | Install explicit-only. Vertical tracer bullets and explicit blocking edges are better than horizontal layer plans. |
| `triage` | Medium | Adapt | Install only if maintaining a substantial GitHub, Linear, or local backlog. Too much process for small prototypes. |
| `wayfinder` | Medium | Adapt | Keep explicit-only for multi-session programs. It is too heavy for ordinary features and experiments. |
| `wizard` | High | Mostly portable | Install explicit-only. Excellent for credentials, dashboards, infrastructure, and cutovers where the human must perform steps. Review generated shell carefully. |

### Productivity skills

| Matt skill | Fit | Portability | Decision and reason |
|---|---:|---|---|
| `grill-me` | Low | Portable wrapper | Skip. `grilling` is the substantive dependency and should be installed directly. |
| `grilling` | Core | Portable | Install. Modify it to inspect the repository and existing documents before asking the user questions. Keep one question at a time. |
| `handoff` | Core | Portable | Install. Direct match for moving work between Codex, OpenCode, Cursor, Claude Code, machines, and long sessions. |
| `teach` | Medium | Mostly portable | Keep explicit-only. Useful for learning unfamiliar software concepts from the actual workspace; relatively long for occasional use. |
| `to-questionnaire` | High | Portable | Install explicit-only. Strong for gathering domain, legal, product, or operational facts from colleagues without inventing answers. |
| `wait-what` | Low | Portable | Skip. A plain request to reframe usually suffices. |
| `writing-for-agents` | Core | Portable | Install. Directly useful for `AGENTS.md`, `CLAUDE.md`, skills, handoffs, and experiment continuation prompts. |

### In-progress skills

| Matt skill | Fit | Portability | Decision and reason |
|---|---:|---|---|
| `claude-handoff` | Medium | Claude-specific | Use only in Claude Code. The portable `handoff` is the default elsewhere. |
| `loop-me` | Low | Adapt | Skip. It is for designing workspace workflows and remains in progress. |
| `setup-ts-deep-modules` | Medium | TypeScript-specific | Trial only in a suitable TypeScript monorepo. It modifies dependency-cruiser boundaries and is still in progress. |
| `writing-beats` | Low | Portable | Skip by default. Useful for article or narrative production, not the core job. |
| `writing-fragments` | Low | Portable | Skip by default. Same writing pipeline. |
| `writing-shape` | Low | Portable | Skip by default. Same writing pipeline. |

### Miscellaneous skills

| Matt skill | Fit | Portability | Decision and reason |
|---|---:|---|---|
| `git-guardrails-claude-code` | High in Claude | Claude-specific | Install when Claude Code is present. Hooks provide deterministic safety that prose cannot guarantee. No value to Codex/OpenCode without a rewrite. |
| `migrate-to-shoehorn` | Low | TypeScript niche | Skip unless a codebase already uses `@total-typescript/shoehorn`. |
| `scaffold-exercises` | Low | Portable | Skip unless creating courses or exercises. |
| `setup-pre-commit` | Medium | Node-specific | Keep explicit-only for JavaScript/TypeScript repos using Husky. It is not the right default for Python projects. |

## Public reception and external evidence

| Evidence | What people say | Weight in this decision |
|---|---|---|
| [Matt's skills on skills.sh](https://www.skills.sh/mattpocock/skills) | Very high reported installation volume and broad interest. The catalog includes historical or renamed entries, so its count does not equal the current repository's 35 skill directories. | Strong adoption signal, weak effectiveness signal. |
| [Independent critical review by Florian Gahn](https://florian-gahn.de/blog/matt-pocock-agent-skills) | Codex installation was reproducible. The small workflows are useful, but prompt gates are soft, complex skills depend on the harness, and independent productivity or quality proof is missing. | High-quality qualitative assessment. |
| [Critical guide by Kaitlin Albasi](https://kaizencode.art/notepad/matt-pocock-skills-guide/) | The strongest part is conventional engineering discipline: seams, tracer bullets, red-green-refactor, two-axis review, and domain language. | Supports choosing the core primitives rather than every wrapper. |
| [Hands-on multi-model report](https://www.reddit.com/r/WebAfterAI/comments/1v2xmc8/handson_evaluation_running_matt_pococks_ai_skills/) | Frontier models followed complex workflows well; smaller or alternative models varied and needed prompt tuning. Long loops consumed substantial tokens. | Relevant to OpenCode using a local Qwen model, though the post has no peer review or community validation. |
| [Matt repository issues](https://github.com/mattpocock/skills/issues) | Users report that one-question gates are sometimes ignored, TDD may be described without tests actually running, and the skill router has made claims without reading the target skill. Users also ask for a clearer end-to-end flow. | Concrete warning that prose is guidance, not enforcement. Supports tests, hooks, verification, and a small audited router. |
| [Kayvane's pstack teardown](https://www.kayvane.com/posts/building-a-multi-skill-system) | Praises the three-layer router, playbook, principle design. After two days and about 12 PRs, the author reported targeted, reviewable changes with low cognitive debt. | Best independent pstack account found, but short duration and one user. |
| [Pstack repository](https://github.com/cursor/plugins/tree/main/pstack) and [Lauren Tan's launch account](https://www.linkedin.com/posts/laurenelizabethtan_cursor-pstack-the-skills-behind-10000-activity-7465439429042737152-ADbv) | Pstack is presented as the workflow behind 10,000 agent runs and daily Cursor engineering. | Useful provenance, still a first-party claim. |
| [Benchmark of 34,000 real-world skills](https://arxiv.org/abs/2604.04323) | Skill gains became fragile as retrieval and task mismatch grew. Query-specific refinement recovered performance; one Terminal-Bench result improved from 57.7% to 65.5%. | Strong reason to keep the active set small and customize it to this work. The paper does not evaluate Matt or pstack specifically. |
| [Study of 138,133 public skills](https://arxiv.org/abs/2608.08453) | The authors detected at least one defect in 91.8% of skills, commonly weak routing metadata, bloated bodies, or poor resource organization. Specification-aware skills did better. | Strong reason to lint, port, test, and pin reviewed snapshots rather than bulk-install. Preprint, not a final verdict on these two repositories. |

The public evidence favors Matt's small primitives and pstack's orchestration shape. It does not justify treating either collection as proven end-to-end quality assurance. Pstack has less independent evidence because it is newer. Both benefit from local evaluation on your actual repositories and models.

## Recommended installation waves

### Wave 1: low-risk portable core

Install into a shared `~/.agents/skills` source, then expose it to Codex and OpenCode:

- pstack: `unslop`, `blast-radius`, `technical-writing`, `typescript-best-practices`
- Matt: `grilling`, `domain-modeling`, `codebase-design`, `diagnosing-bugs`, `prototype`, `research`, `handoff`, `to-questionnaire`, `writing-for-agents`
- merged local skill: `tdd`, using Matt's loop and pstack's skip conditions

Keep these Addy specialists:

- `api-and-interface-design`
- `browser-testing-with-devtools`
- `ci-cd-and-automation`
- `deprecation-and-migration`
- `frontend-ui-engineering`
- `git-workflow-and-versioning`
- `observability-and-instrumentation`
- `performance-optimization`
- `security-and-hardening`
- `shipping-and-launch`
- `source-driven-development`

### Wave 2: personal router and long-run support

Create `astrobyte-mode` rather than installing raw Poteto Mode outside Cursor. Include:

- playbooks for investigation, bug, performance, runtime/trace forensics, hill-climb, feature, refactor, prototype, eval, autonomous run, session pickup, pause, multi-phase work, and verification
- selected pstack principles as internal references
- Matt primitives as routed skills
- your existing safety, Git, verification, documentation, and approval rules
- adapters for Codex and OpenCode tool names
- explicit limits for parallelism, spend, external side effects, experiment budgets, and unattended runs

Port `create-verification-skill`, `maintain-verification-skill`, `show-me-your-work`, `recall`, `architect`, `how`, `why`, and `interrogate` alongside it.

### Wave 3: explicit-only situational skills

Add Matt `code-review`, `grill-with-docs`, `improve-codebase-architecture`, `resolving-merge-conflicts`, `to-spec`, `to-tickets`, `triage`, `wayfinder`, `wizard`, and `setup-pre-commit` only where their trigger and dependencies are clear.

Use pstack `arena`, `swarm`, `reflect`, `figure-it-out`, `teach`, and `no-comments` only by explicit invocation.

### Wave 4: remove duplicated Addy workflows

After a small local evaluation, disable the replaced Addy skills:

- `code-review-and-quality`
- `code-simplification`
- `context-engineering`
- `debugging-and-error-recovery`
- `documentation-and-adrs`
- `doubt-driven-development`
- `idea-refine`
- `incremental-implementation`
- `interview-me`
- `planning-and-task-breakdown`
- `spec-driven-development`
- `test-driven-development`
- `using-agent-skills`

Do not remove them before the replacement router and direct skills pass the evaluation.

## Evaluation before migration

Use a small blind comparison on representative tasks:

1. A Python data-contract bug with a cheap regression test.
2. An ML hill-climb with a fixed compute budget and decision log.
3. A FastAPI endpoint with validation, errors, tests, and documentation.
4. A React/TypeScript dashboard change verified in a real browser.
5. A model export or deployment parity task across two runtimes.
6. A cross-session handoff resumed in OpenCode with the local Qwen model.

Score each run on correctness, unnecessary diff size, questions asked, tests and runtime evidence, documentation accuracy, token/time cost, and whether another agent can resume it. Keep a skill only when it improves the result or reliably reduces supervision.

## Final recommendation

Adopt pstack's architecture, not its raw Cursor implementation, as the cross-tool workflow layer. Adopt Matt's best small primitives directly. Retain the Addy specialists that cover operational and product-engineering gaps. Keep the active catalog lean, route niche skills explicitly, and test the setup with the same rigor used for model and prompt evaluation.
