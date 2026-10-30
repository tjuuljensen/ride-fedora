# Fedora 44 base package supported-state promotion

Status: **PASS**, 2026-10-30. Reviewer: Codex. The owner confirmed that no
non-disposable machine had run v3 before promotion. These checks used disposable
VM overlays, the pinned Fedora 44 x86_64 images in
`tests/acceptance/targets.json`, and catalog SHA-256
`1593b4ceb44a5ab07f05b17abc12397904a7ff0561e527effcca540402954911`.
The VM metadata records source revision `39d5846` plus uncommitted promotion
changes. The three promoted catalog rows differ from that revision only in
`status` and `acceptanceEvidence`; handler, target, source, and recovery fields
are identical. These two metadata fields are outside the run source signature.

| Exact target | Focused result | Retained overlay and JUnit |
| --- | --- | --- |
| Fedora 44 Cloud Base x86_64, `VARIANT_ID=cloud` | PASS: `package.exfatprogs` planned as supported, installed without `--allow-candidate`, repeated unchanged, passed signed RPM and file verification, reported supported status, restored the new install, and recovered package inventory. | `20261030T090018Z-test-package-apply-repeat-status-restore-and-remove-665a81a8`; `.acceptance-runs/cloud-supported.xml` |
| Fedora 44 Workstation x86_64, `VARIANT_ID=workstation` | PASS: `default` planned exactly `package.less`, `package.openssh-clients`, and `package.exfatprogs` as supported; apply without the override recorded three unchanged steps. Inventory, SSH configuration checksum, and SSH server availability were preserved. | `20261030T090442Z-test-workstation-default-profile-smoke-28783ea1`; `.acceptance-runs/workstation-supported.xml` |
| Fedora 44 Server x86_64, `VARIANT_ID=server` | PASS: `server-base` planned exactly `package.less` and `package.openssh-clients` as supported; apply without the override recorded two unchanged steps. Inventory, SSH configuration checksum, and SSH server availability were preserved. | `20261030T090508Z-test-server-base-profile-smoke-f1ad9b2e`; `.acceptance-runs/server-supported.xml` |

Each JUnit file reports one test, zero failures, zero errors, and zero skips.
Overlay `metadata.json` and `transcript.jsonl` retain the exact image and
source hashes, commands, and outcomes. The earlier per-operation
[exfatprogs](package.exfatprogs.md), [less](package.less.md), and
[OpenSSH clients](package.openssh-clients.md) records provide lifecycle,
failure, target-gate, and recovery evidence for unchanged runtime behavior.
No manual session was needed for these command-line operations.

Local pre-push validation passed shell syntax and ShellCheck for the Bash
client and POSIX bootstrap, catalog/schema and generated-doc checks, burndown,
executable modes, 55 mocked and Firefox tests, Python compilation, and seven
acceptance tests collected without launching guests. The promoted commit's
remote CI result is recorded in the migration plan.
