# Astrobyte routing

Astrobyte skills are installed for this agent. This pointer says when to load them; the skills hold the policy.

1. Before substantial work, load the `astrobyte-mode` skill and follow its Route step. Substantial work crosses files, spans more than one commit or pull request, runs live or unattended, or ends in a push.
2. Before an agent-created push or pull request, run the `astrobyte-review` gate. When the harness does not offer that skill directly, read `astrobyte-review/SKILL.md` in the same skills directory as `astrobyte-mode`. Do not push or open the pull request until the required independent review records `PASS`.
3. Before an agent-created commit, load `astrobyte-git-identity`.
4. Mode, reviewer, retry, attribution, and verification details live in those skills. Follow them, not this summary.
