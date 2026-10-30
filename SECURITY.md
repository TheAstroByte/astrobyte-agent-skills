# Security policy

## Report a vulnerability

Use **Security and quality → Report a vulnerability** on GitHub when private reporting is available. Provide the affected revision, a minimal reproduction, impact, and a proposed fix if you have one. Use fictional data and redact credentials, personal paths, and unrelated private information.

Private reporting is a separate repository setting; this file does not enable it. If the reporting control is unavailable, open an issue asking only for the maintainer's preferred private reporting route. Keep vulnerability details, exploit steps, and personal data out of that public request. See [GitHub's private reporting guidance](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately).

For accidentally exposed credentials, revoke or rotate them through the provider. Removing a file or commit does not retract existing copies. Report the affected locations without reposting the credential.

## Scope and expectations

Useful reports include installer data loss, unintended file changes, secret exposure, and instructions that cross trust or authorization boundaries. Report ordinary behavior or compatibility problems through the bug template.

The skills and scripts are provided as-is under their applicable licenses. There is no maintained-version, backport, remediation-deadline, or response-time commitment. Reports against current `main` or the latest published release are easiest to reproduce; include the exact revision either way. Do not access other people's data or systems to demonstrate a problem.
