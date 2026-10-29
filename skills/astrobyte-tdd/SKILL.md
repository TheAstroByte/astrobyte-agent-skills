---
name: astrobyte-tdd
description: Use a pragmatic red-green-refactor loop for behavior changes and bug fixes when a trustworthy test seam is clear and affordable. Use when the user asks for TDD, a regression test, red-green-refactor, or implementation through tests.
---

# Astrobyte TDD

## Choose the seam

Describe one observable behavior and choose the cheapest test that fails for the right reason.

Use TDD when the seam is deterministic and the loop is tight. For expensive training, hardware-specific runtimes, broad end-to-end systems, or unclear failures, first build a smaller reproduction, contract test, smoke check, or measurement harness. State why a red unit test is not trustworthy before using another proof.

## Red

1. Write one test for the requested behavior. Assert public behavior.
2. Run it and observe the expected failure.
3. Fix the test or seam if it fails for setup, syntax, or an unrelated cause.

Red is complete when the failure specifically demonstrates the missing behavior or bug.

## Green

1. Implement the smallest change that can satisfy the test.
2. Run the focused test.
3. Run affected regression coverage after it passes.

Green is complete when the new test and affected tests pass without skips or weakened assertions.

## Refactor

Improve names, duplication, boundaries, and data shapes while keeping the loop green. Stop when the code is direct and the abstraction level matches existing needs.

For empirical ML quality, keep code tests separate from experiment acceptance. A green training test proves the pipeline works; evaluation data proves the model improved.
