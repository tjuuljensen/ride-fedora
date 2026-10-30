# VM acceptance records

The reusable Fedora-first VM runner and its exact commands are in
[VM-HARNESS.md](VM-HARNESS.md). It exercises a shared lifecycle contract from
fresh image overlays. Its generated transcripts are evidence inputs, not an
automatic decision to promote an operation.

Record `docs/acceptance/<operation-id>.md` for each promoted operation. Include
the operation ID and a `PASS` or `FAIL` outcome for each tested target, VM image
digest and overlay identifier, distro edition and release, CPU architecture,
catalog revision, transcript or redacted logs, and reviewer. State the risk
tier, the operation's own checks, and any reused handler evidence.

For low-risk Fedora repository packages, a focused automated check on the exact
target covers plan, apply, repeat, status, signature/files, and the declared
remove or restore. One failure-injection check per unchanged handler batch is
sufficient; record which revision and behavior it covers. For third-party and
desktop behavior, a disposable-VM happy path plus focused mocked checks can
establish an opt-in candidate, with broader recovery or visual checks tracked
for v3.1. A candidate is not advertised as supported. Data, storage,
encryption, security policy, and difficult recovery require deeper safety and
inverse evidence before they are runnable. If that evidence cannot be
obtained, record an unsupported or private disposition rather than claiming a
working operation. For settings, record prior and final values.

Only after a supported target has its risk-appropriate VM evidence should its
catalog status change from `candidate` to `supported` with an
`acceptanceEvidence` path. The [migration progress report](../migrations/progress.md)
counts supported, opt-in candidate, and non-operable dispositions separately.
Acceptance for one Fedora edition, release, or architecture does not imply
another. The initial Fedora Cloud Base target is a generic package pilot and
does not by itself establish Fedora Workstation or Server acceptance.
