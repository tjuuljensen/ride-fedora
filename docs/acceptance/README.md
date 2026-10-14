# VM acceptance records

Record `docs/acceptance/<operation-id>.md` for each promoted operation. Include
the operation ID and a `PASS` or `FAIL` outcome for each tested target. Include VM image
and snapshot identifier, distro edition and release, CPU architecture, catalog
revision, command transcript or redacted logs, apply and repeat apply, status,
remove, restore where declared, failure injection, package signature or hash
result, and reviewer. For system settings, include the prior and final values.

Only after a supported target has this evidence should its catalog status
change from `candidate` to `supported` with an `acceptanceEvidence` path.
Acceptance for one Fedora release or architecture does not imply another.
