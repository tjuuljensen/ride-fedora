# VM acceptance records

The reusable Fedora-first VM runner and its exact commands are in
[VM-HARNESS.md](VM-HARNESS.md). It exercises a shared lifecycle contract from
fresh image overlays. Its generated transcripts are evidence inputs, not an
automatic decision to promote an operation.

Record `docs/acceptance/<operation-id>.md` for each promoted operation. Include
the operation ID and a `PASS` or `FAIL` outcome for each tested target. Include VM image
digest and overlay identifier, distro edition and release, CPU architecture, catalog
revision, command transcript or redacted logs, apply and repeat apply, status,
remove, restore where declared, failure injection, package signature or hash
result, and reviewer. For system settings, include the prior and final values.

Only after a supported target has this evidence should its catalog status
change from `candidate` to `supported` with an `acceptanceEvidence` path.
Acceptance for one Fedora edition, release, or architecture does not imply
another. The initial Fedora Cloud Base target is a generic package pilot and
does not by itself establish Fedora Workstation or Server acceptance.
