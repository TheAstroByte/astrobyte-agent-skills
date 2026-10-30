# Missing skill dependencies

The source catalog distinguishes hard dependencies from conditional specialists and suggestions. The native installer expands hard dependencies for an explicitly requested workflow. It leaves conditional specialists and suggestions unselected.

When a hard dependency is missing, identify the incomplete workflow and offer its native installation with `--skills <workflow>`. When a conditional specialist is needed but missing, name it and request adding it only for the active branch. Preserve the current profile or subset when previewing an addition; for an explicit subset, use `--skills <current-selection>,<specialist>` rather than replacing it with the specialist alone. Reinstalling the workflow does not select conditional specialists automatically. Suggestions are related guidance, not execution requirements. Installation remains an explicit management action. A runtime task must not clone or configure the source just to read baseline policy.

`astrobyte-architect` uses `api-and-interface-design` for public HTTP or GraphQL contracts. Core covers other architecture tasks; request the specialist only for that branch. Review still requires an available independent reviewer, and browser testing still requires an actual browser tool.

The security skill uses `diagnosing-bugs` for privacy-incident diagnosis and reports its absence if unavailable. Its observability reference is related guidance rather than an unconditional execution dependency. Other standalone specialists include local steps for diagnosis, change splitting, and completion checks so those branches can run without a workflow bundle.

Standard third-party skill installers may copy only the named skill. They do not necessarily understand this catalog's dependency closure. Install the declared workflow dependencies explicitly, or use the native installer from a readable source checkout. Standalone leaf skills with no dependencies need no workflow bundle.
