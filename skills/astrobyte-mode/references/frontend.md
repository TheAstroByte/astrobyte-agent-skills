# Frontend design and implementation

Apply this sequence to new interfaces and deliberate visual redesigns. Keep the user's requested scope, existing product identity, and established design tokens authoritative.

1. Inspect the brief, current interface, components, and brand rules. Identify the audience and the interface's primary job from available evidence. Ask only for a material missing decision.
2. Use `frontend-design` before coding to establish visual direction. Reuse a supplied direction and existing product tokens. Its design-plan critique is an agent check, not an additional user approval gate.
3. For implementation, use `frontend-ui-engineering` within the project's existing stack. Preserve reusable components, accessibility, responsive behavior, and loading, error, and empty states. For a design-only request, deliver the design artifact without starting implementation.
4. For implemented interfaces, inspect the rendered result with available browser tools. Use `browser-testing-with-devtools` when a Chrome DevTools MCP connection is available. Otherwise use the harness's available browser capability. Check the match to the brief, responsive layouts, and keyboard interaction. Fix observed issues and record unavailable checks.

Resolve sibling skills through the router's package-relative lookup. If an applicable specialist is missing, follow the router's missing-specialist policy. Runtime work does not start installation or onboarding.

Complete when the requested design or implemented interface matches the brief and existing product constraints, with observed verification evidence and any pending checks stated.
