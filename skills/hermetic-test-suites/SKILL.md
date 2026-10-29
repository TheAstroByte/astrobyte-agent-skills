---
name: hermetic-test-suites
description: Make test suites deterministic across local, CI, clean checkout, repeated, and randomized runs. Use when tests depend on environment variables, repository files, external services, background work, process-global caches, execution order, or leftover state.
---

# Hermetic test suites

## Establish the mismatch

Run the failing tests in the developer checkout and a clean checkout from the same commit. Record exact node IDs, environment differences, generated files, warnings, and background failures. Keep stale assertions separate from isolation failures.

The baseline is complete when every observed difference has evidence rather than an assumed CI explanation.

## Inventory ambient inputs

Trace each test through the real runtime boundary and account for:

- environment variables and credential discovery
- default config paths and repository-local data
- network clients, cloud SDKs, clocks, randomness, and host services
- process-global caches, singletons, mutable factories, and dependency maps
- background threads, tasks, subprocesses, and delayed exceptions
- writes outside per-test temporary storage
- state left by earlier tests

Treat a passing dirty checkout as suspect until the same test passes without its leftover state.

## Build explicit seams

Move nondeterminism to injectable boundaries:

- pass config values or explicit fixture paths
- construct services with injected clients, formatters, clocks, launchers, and storage
- use framework-native dependency overrides and restore the previous mapping
- clear every relevant cache before and after tests
- run workers inline for behavior tests; use a recording launcher when only scheduling matters
- store reusable payloads under the test data tree and load them through fakes

Keep production defaults at the composition root. Core behavior should run without credentials, network access, repository config, or mutable class state.

Patch third-party constructors only at their import boundary when constructor wiring is the behavior under test. Prefer dependency injection for application code.

## Repair expectations

Update stale assertions only after isolation is in place. Assert domain results, persisted status transitions, constructor contracts, and scheduled work at their owning seams. Give each API test unique identifiers and use clients as context managers so lifespan cleanup runs.

## Prove hermeticity

Verify in this order:

1. previously failing node IDs in isolation
2. the full suite from a clean checkout with generated directories absent
3. the full suite with provider, credential, tracing, and app-config variables removed
4. two consecutive full runs
5. at least three deterministic shuffled orders
6. unchanged repository status and no repository-local writes
7. no unhandled-thread, unraisable, or delayed background exception

Make thread and unraisable warnings test errors. A network-blocking plugin is optional evidence, not a substitute for injected dependencies.

The suite is trustworthy when every verification mode agrees and no run depends on state that another run created.
