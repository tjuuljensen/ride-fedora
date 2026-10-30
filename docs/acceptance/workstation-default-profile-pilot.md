# Fedora 44 Workstation default profile smoke pilot

Date: 2026-10-30. Target: pinned Fedora 44 Workstation x86_64 image,
`VARIANT_ID=workstation`, base SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
Source revision: `0bfd3c02350c85069c85b3b28457c2396e827d67` with
uncommitted changes. The disposable overlay was
`20261030T074554Z-test-workstation-default-profile-smoke-47c5143c`.
JUnit: `/tmp/ride-acceptance-runs/fedora-44-workstation-default-profile-exact.xml`
(1 passed, 5 deselected; 29.18 seconds). Its `metadata.json` and
`transcript.jsonl` hold the verified target and commands.

PASS: read-only `plan --profile default` reported exactly `package.less`,
`package.openssh-clients`, and `package.exfatprogs` already installed and
selected as candidates. No run journal existed after plan. `apply --profile
default --allow-candidate` completed with three `unchanged` steps in profile
order. Each individual status was installed. Package inventory and
`/etc/ssh/ssh_config` checksum matched the pre-apply values; `openssh-server`
remained installed and `sshd` active.

This smoke check covers combined profile selection and interaction. The
[first package batch](workstation-package-batch-1-pilot.md) and
[OpenSSH client pilot](openssh-clients-workstation-pilot.md) contain the
operation-specific install, failure, and recovery evidence. No manual session
was needed. The operations were candidates during this pilot. The later
[per-operation acceptance records](package.less.md) include source review;
the owner confirmed no non-disposable v3 runs before promotion.
