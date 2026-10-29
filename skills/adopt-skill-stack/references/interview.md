# Adoption interview

Use this order, but adapt the depth to the operator. A senior engineer gets terse trade-offs. A technical prototyper gets enough explanation to make an informed choice.

## Identity and work

Ask for:

- a handle and optional display name;
- role, recurring project types, and team context;
- languages and domains classified as expert, comfortable, learning, occasional, or avoid;
- the agent products in use and the preferred product;
- desired explanation level: expert concise, collaborative, or guided teaching.

Recommend handle-based repository naming and keep upstream `astrobyte-*` skill names. Offer full renaming with a warning that every upstream update becomes harder to merge.

## Good code

Ask in the operator's own words:

1. What makes code good enough to keep?
2. What agent behavior has caused the most frustration?
3. What must an agent never change without asking?
4. What evidence makes a change trustworthy?

Translate the answer into observable rules for scope, module boundaries, dependencies, typing, tests, documentation, compatibility, maintainability, and real-artifact verification. Show the normalized rules and correct them with the operator. Do not store the raw answers.

Use these repository practices as starting recommendations, not forced doctrine: scope fidelity, dependency blast-radius checks, deep modules, pragmatic TDD, real-artifact verification, and explicit excluded scope.

## Autonomy

Offer these presets and then review each control:

| Preset | Default behavior |
|---|---|
| `exact-scope` | Change only approved files and behavior. Ask before dependent work or scope expansion. |
| `guided-implementation` | Implement the agreed outcome and necessary dependencies, with milestone approvals. |
| `bounded-autonomy` | Work independently inside the repository scope and acceptance contract. Pause at destructive, external, costly, or architectural boundaries. |
| `prototype-sprint` | Build a time-boxed vertical slice. Keep security, data-loss, cost, and external-action limits. |

Review scope expansion, dependency changes, tests, Git actions, external actions, unattended runs, communication, refactoring, cleanup, and destructive actions. The operator can override any preset field.

Use collaborative challenge as the recommended communication style. Offer strictly comply and actively challenge. Challenge concrete risk, not taste.

## Delivery modes

Support all four modes in one profile:

| Mode | Contract |
|---|---|
| `explore` | Disposable work that answers a question with reproducible evidence. |
| `prototype` | A working vertical slice with minimal infrastructure and marked shortcuts. |
| `durable` | Maintainable code, dependency checks, stable boundaries, proportionate tests, typing, and documentation. |
| `production` | Durable standards plus security, observability, migrations, rollout, and rollback. |

Ask for the personal default. Ask whether each machine inherits it, asks during installation, or asks for every project or run. A project can always override the machine.

## Stack and project startup

For each relevant language or domain, ask for greenfield preferences and preservation rules. Do not force a choice when the operator lacks one. Record `ask-per-project` and let `astrobyte-project-startup` resolve it from project evidence.

Cover package and environment management, framework, build, lint, format, type checking, tests, data formats, storage, deployment, containers, observability, model providers, local model runtimes, experiment tracking, and external services. Preserve coherent existing projects.

## Repository and machines

Recommend an independent private repository in the operator's account or organization. Ask whether another collaborator retains access. Ask whether the operator wants multi-machine synchronization before creating a registry.

For a synchronized registry, commit only machine aliases, roles, broad capabilities, allowed delivery modes, defaults, and setup status. Keep identifying and secret data local.

Ask about Git isolation, issue tracking, CI, branch protection, the initial pull request, and upstream contribution preferences. Enable CI by default and allow the operator to disable it.

Ask how Git should attribute commits created by an agent. Recommend dual attribution: the operator is author, the active agent product is committer, and an `Agent` trailer names the product. Collect the human identity as machine-local configuration. Store reusable agent product identities in the private profile. Offer agent-only, human with an agent trailer, or disabled attribution. Explain that a separate GitHub push actor requires bot or App credentials.

## External work and updates

Separate interactive and unattended external-action policies. `allow-configured` means only actions already authorized by the active product or run configuration. It does not grant new authority.

Ask for local and cloud time or cost limits, checkpoint frequency, stop rules, and recoverable state. Ask how updates arrive: manual only, notify, open a reviewed pull request, or merge and install automatically after all gates pass.

## Uncertainty

Every material answer must end as `chosen`, `ask-per-project`, or `recommend-when-needed`. Prefer `ask-per-project` when the operator has no stable preference. Show unresolved choices before application.
