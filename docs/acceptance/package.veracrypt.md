# VeraCrypt Fedora 44 Workstation acceptance

Status: **passed**, 2026-11-01. `package.veracrypt` is supported on Fedora 44
Workstation x86_64. Target: Fedora 44 Workstation x86_64.

VM PASS: `test_veracrypt_rpm_lifecycle_preserves_mounted_and_unmounted_test_volume`
passed on Fedora 44 Workstation x86_64.

The operation uses the VeraCrypt 1.26.30 publisher GUI RPM. Before DNF sees a
local package, RIDE downloads the detached signature and public key, checks
that the imported keyring contains the publisher fingerprint
`5069A233D55A0EEB174A5FC3821ACD02680D16DE`, verifies the signature, and
checks the RPM name. The key stays in a temporary keyring. No key is imported
into the RPM database. DNF local-package signature checking is disabled only
for this already-verified package; repository verification remains enabled.

The mocked provider tests cover verified install dispatch, refusal of a bad
signature before DNF, temporary keyring use, absence of a global RPM key
import, idempotence when VeraCrypt is already installed, failed DNF artifact
cleanup, and mounted and empty mount-list responses.

The disposable-VM test creates a test-only encrypted container, stores a
sentinel file, refuses application removal while the test volume is mounted,
then unmounts it and removes the package. It reinstalls the package, remounts
the same container, reads the sentinel, unmounts, verifies the volume digest,
and removes the package. It does not use any user volume or credential.

VM investigation found that the signed RPM's `%preun` scriptlet refuses
package removal while a VeraCrypt volume is mounted and leaves the package
installed. RIDE checks the CLI mount list first and refuses without starting
DNF when any volume is mounted. VeraCrypt reports an empty mount list as
`Error: No volumes mounted.` and returns 1; RIDE accepts only that exact output
and fails closed for other unknown responses. The passing
`test_veracrypt_rpm_lifecycle_preserves_mounted_and_unmounted_test_volume` run
used the pinned image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Its transcript is
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-publisher-02-veracrypt-final-check/fedora-44-workstation-x86_64/20261101T214026Z-test-veracrypt-rpm-lifecycle-preserves-mounted-and-unmounted-test-volume-bd9cd157/transcript.jsonl`
with SHA-256 `fa06c6d43b553abe2b696c885121a7607ae853fee05959450bef46d90abcddf4`.
The encrypted test container digest was identical before removal, after
removal, and after reinstall:
`4401ff7cf679b32af4966839a0701a5dee55eae4d2852123827d11cc2158c244`.
