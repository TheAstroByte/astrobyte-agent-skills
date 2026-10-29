# Missing skill dependencies

The source catalog distinguishes hard dependencies from conditional specialists and suggestions. The native installer expands hard dependencies for an explicitly requested workflow. It leaves conditional specialists and suggestions unselected.

When a required skill is missing, identify the incomplete workflow and offer its native installation with `--skills <workflow>`. Installation remains an explicit management action. A runtime task must not clone or configure the source just to read baseline policy.

`astrobyte-architect` uses `api-and-interface-design` for public HTTP or GraphQL contracts. Core covers other architecture tasks; request the specialist only for that branch. Review still requires an available independent reviewer, and browser testing still requires an actual browser tool.

The vendored security skill retains a legacy `debugging-and-error-recovery` reference for privacy incidents. Use the installed `diagnosing-bugs` procedure for that branch, and report its absence if unavailable. Its observability reference is related guidance rather than an unconditional execution dependency.

Standard third-party skill installers may copy only the named skill. They do not necessarily understand this catalog's dependency closure. Install the declared workflow dependencies explicitly, or use the native installer from a readable source checkout. Standalone leaf skills with no dependencies need no workflow bundle.
