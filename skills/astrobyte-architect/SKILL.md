---
name: astrobyte-architect
description: Settle data shapes, interfaces, ownership, and test seams before building. Use for new subsystems, API boundaries, shared state, or cross-stack features.
metadata:
  opencode/autoinvoke: "false"
---

# Astrobyte architect

1. Read the current callers, contracts, data models, and repository conventions.
2. Write the primary usage from the caller's point of view.
3. Name the domain objects, identifiers, states, invariants, and transitions.
4. Mark trust boundaries and ownership of persistence, concurrency, retries, and errors.
5. Sketch the smallest public signatures and module tree that support the usage.
6. Identify a test seam for each risky behavior.
7. Compare a second design when the decision is novel, expensive to reverse, or based on an unproven abstraction.
8. Select the design with the narrowest stable interface and clearest ownership.

Produce:

- example caller usage
- types or schemas
- public signatures
- module ownership map
- invariants and error contract
- test seams
- rejected alternative with one-line reason

Architecture is complete when implementation can proceed without inventing a second source of truth or an unresolved ownership boundary.

For detailed module vocabulary, use `codebase-design`. For public HTTP or GraphQL contracts, also use `api-and-interface-design`: read `../api-and-interface-design/SKILL.md` when it is a sibling, otherwise use it from the session's skill list, for example `astrobyte-web:api-and-interface-design`. If it is unavailable, report the missing capability and the package that provides it before applying that branch. Other architecture tasks do not need it.
