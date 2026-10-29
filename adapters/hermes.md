# Hermes adapter

Install copies under `~/.hermes/skills/astrobyte`, or configure `~/.agents/skills` as an external directory in `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - ~/.agents/skills
```

Hermes can also consume this repository as a tap:

```bash
hermes skills tap add TheAstroByte/astrobyte-agent-skills
```

A tap of a private fork needs GitHub authentication.

Hermes has no always-loaded routing location in this installer. Installs for Hermes are skills-only and print a warning; invoke `astrobyte-mode` explicitly for substantial work. Add routing support only after this adapter names and verifies a mechanism. See [Routing](../docs/routing.md). Hermes may edit writable external skills through its skill-management tools, so use filesystem permissions or a review workflow when the shared checkout must remain authoritative.

Official reference: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md
