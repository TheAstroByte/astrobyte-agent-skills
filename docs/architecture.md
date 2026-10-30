# Architecture

## Layers

1. `astrobyte-mode` classifies the task and resolves whether project startup is required.
2. Installation defaults to the committed Astrobyte profile without an onboarding interview. `adopt-skill-stack` runs personalized adoption only when requested, recording differences from that shared baseline. `setup-astrobyte-skills` installs shared or personalized profiles on a machine. The native installer resolves workflow dependencies for explicit subsets; standalone leaf packages remain independent.
3. `astrobyte-project-startup` records material project choices before implementation.
4. Playbooks define ordered work and checkable completion criteria.
5. Principles constrain implementation and verification.
6. Specialist skills supply deeper procedures when the task requires them.
7. Agent product adapters map portable actions to product-specific tools and paths.

The router owns composition. Leaf skills stay narrow. Machine configuration supplies preferences without embedding local paths, model names, or approval policy in shared instructions.

## Configuration precedence

The runtime [configuration contract](../skills/astrobyte-mode/references/configuration.md) is canonical. It orders task instructions, project configuration and repository evidence, explicit machine policy, local deltas and legacy profiles, portable deltas, then the packaged baseline. The standalone resolver reports JSON preferences and ordered agreement layers. Agents apply task instructions and repository evidence themselves.

Configuration can narrow autonomy. Harness permissions and user authority remain binding. External-action preferences never grant new authority.

## Catalog policy

- `core` carries repeatable work across every harness.
- `builder` adds the software areas most useful to an ML specialist.
- `full` adds operational lifecycle specialists.
- Expensive review, parallelism, and long-run behavior remain explicit or configuration-gated.
- Native product skills stay outside this repository and are detected during setup.
- `unslop` is required in every profile. Other behavioral skills are selected during adoption.
- Optional specialists are cataloged outside the default profiles and require an explicit personal or machine selection. A personal delta can carry the approved selection between machines. Selection does not configure third-party tools or grant runtime permissions.

`builder` and `full` pair Anthropic's `frontend-design` with `frontend-ui-engineering`. The router's package-contained [frontend guidance](../skills/astrobyte-mode/references/frontend.md) orders design, implementation, and browser verification for new interfaces and deliberate visual redesigns, including prototypes. These specialists remain conditional for `core` and explicit workflow subsets. The standalone design package has no sibling dependencies.

## Package dependencies

`catalog.json` declares hard `dependencies`, branch-specific `conditional_dependencies`, related `suggestions`, and required package-contained `runtime_resources`. The native installer expands only hard dependencies. `--skills diagnosing-bugs` installs one standalone leaf; `--skills astrobyte-mode` includes its workflow gates and procedures. `--profile full` returns to the normal catalog selection. Quick updates preserve extra installed skills and unrelated files.

Validation checks hard dependency closure, unknown names, cycles, and all profiles. It validates required files and Markdown references throughout each skill package, excluding fenced project examples. Runtime resources and symlinks must stay inside the copied package. Tests validate copies outside the source checkout. Management skills explicitly require source access and disable automatic model invocation; runtime workflows do not trigger management automatically.

The architect's API specialist and the security skill's `diagnosing-bugs` procedure for privacy incidents are conditional. The security skill's observability reference is a suggestion. External tools remain runtime capabilities to check, not sibling skill dependencies. The installed router's [dependency guidance](../skills/astrobyte-mode/references/dependencies.md) explains when to request missing packages. Standalone specialists carry local steps where another skill is unnecessary. Repository validation rejects cataloged retired skill names in packaged Markdown instructions.

## Personal and machine policy

`profiles/<handle>/profile.json` stores normalized personal defaults. The matching working agreement explains those defaults to agents. `profiles/<handle>/machines.json` stores sanitized aliases, roles, broad capabilities, delivery defaults, and setup status.

Fresh quick installs rely on packaged baseline policy and record inheritance in local configuration. Approved personalization uses `preferences.json` deltas, with portable export only when requested. Legacy full profiles and local agreements remain explicit until migration is approved. The full-profile interview still supports a separately maintained profile. Machine configuration can contain host details and local paths because it remains outside Git. Project configuration remains the final durable override below an explicit current instruction.

Quick installation and requested personalization resolve their inputs through the same validated plan. A personal delta can select optional packages and reusable PR-workflow policy. Explicit machine defaults retain their precedence; an explicit personal optional-package list replaces the saved optional selection. Missing new fields preserve older behavior. The shared baseline is independent of these personal choices.

`astrobyte-pr-workflows` is an optional explicit entrypoint. Its procedures reuse the existing router, independent review, attribution, recall, and PR feedback skills. Its local state helper stores approved council routes by harness and review-bot policy by repository and base branch. Portable policy contains reusable choices; a new host verifies capabilities and asks for its local choices only when the relevant operation is invoked. Both finish aliases remain unmerged, and the package never adds council to an ordinary review automatically.

Git attribution is split the same way. The personal profile stores reusable agent product identities and policy. Explicit machine configuration may store the human author identity. Otherwise the runtime helper resolves Git's effective identity in the current repository and environment. `astrobyte-git-identity` applies both to one commit without changing normal Git configuration.

## Update policy

Vendored upstream files are snapshots. Refresh one source in a dedicated commit, update the pinned commit, review semantic changes, run validation, and record any Astrobyte adaptation. Keep custom logic in `astrobyte-*` skills whenever practical so upstream refreshes remain mechanical.

## Packaged baseline resources

`profiles/astrobyte/profile.json` and its working agreement are the canonical shared policy. Run `python3 scripts/portable_profile.py` after changing them. The generator creates package-contained baseline resources for `astrobyte-mode`, `astrobyte-review`, and `astrobyte-git-identity`. Each JSON resource records its schema, repository version, source paths, and a shared policy content hash. The router also receives the complete working agreement.

Generation exports reusable policy through an allowlist. It excludes human Git identity, machine registries, publication choices, and capability claims. `python3 scripts/portable_profile.py --check` checks consistency without writing; repository validation runs the same check. Edit canonical sources, then regenerate instead of editing generated files.

The router and independent review use their packaged defaults when local configuration is absent. Their packaged `scripts/runtime_config.py` reports file preferences and their sources without importing this repository. Current task instructions and coherent repository evidence remain agent-resolved overrides. The generator also copies that standalone resolver and the router's configuration precedence reference into the independent review package.

Git attribution uses its packaged policy when optional machine config is absent. Explicit configured human identity remains supported; otherwise the helper resolves author environment variables and Git's effective configuration in the current repository. Conditional includes are honored. Missing identity fails before committing instead of disabling attribution or starting onboarding.
