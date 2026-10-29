# Verify synced skills in Cursor Cloud

Status on 7 October 2026: hosted check pending. This development session has no connected Cursor Cloud Agent environment. Automated checks cover isolated skill folders, runtime preferences, policy layers, Git attribution, and missing resources. They do not prove Cursor discovery or agent behavior.

## Check the baseline

1. Install the current baseline locally for Cursor and verify its manifest.
2. Enable personal skill sync and start a fresh hosted agent on an application repository. Use an environment without the skills source checkout or Astrobyte machine configuration. Check their absence without deleting existing user state.
3. Invoke `/astrobyte-mode` for a small representative task, such as explaining one CLI's behavior against its current code and recording a concise note.
4. Have the agent locate its installed `astrobyte-mode` folder and run its `scripts/runtime_config.py --project <application-root>`. Read its baseline, agreement, and chosen playbook.
5. Confirm it selects the packaged Astrobyte baseline with durable delivery unless task or project instructions override it. It should not clone the skills source or start adoption to resolve defaults.
6. For an authorized change that requires review, confirm it uses packaged review dispatch and obtains an independent read-only PASS. If the needed tool or model is unavailable, it must report that limitation and leave the gate pending.
7. If the task includes a commit, authorize the commit in the normal task scope. Confirm the helper uses that environment's human Git identity, the Cursor committer, and an Agent trailer. Missing human identity should ask only for name and email; it must not trigger onboarding.

## Check automatic routing

Personal skill sync does not copy the local routing rule. Add the account User Rule from [Routing](routing.md#local-synced-and-cloud), then start a fresh hosted agent and request a small change that ends in a commit and push, without invoking `/astrobyte-mode`. Confirm the agent loads `astrobyte-mode` on its own and runs the review gate before pushing. Until that run is observed, record automatic Cloud routing as pending.

## Check portable differences

After the baseline check, install a reviewed delta locally with `--portable-preferences`, re-sync, and start another fresh agent. Confirm its runtime output applies that delta without external config. Then use `--local-preferences`, re-sync again, and confirm a new agent uses the baseline. Do not export private machine facts or credentials.

## Record observations

Record the source revision, selected skills, sync confirmation, environment or Build identity when available, observed discovery, runtime output, task artifact, review or commit evidence, and unresolved limitations. Exclude secrets and private machine details. Mark each unobserved step pending. A successful local subprocess check is not a hosted result.
