# `package.bitwarden-rpm` acceptance

Status: **supported on Fedora 44 Workstation x86_64**, 2026-11-01.

VM: Fedora 44 Workstation x86_64. Result: **PASS** for
`package.bitwarden-rpm`.

The operation installs the exact Bitwarden `2026.10.1` x86_64 RPM from the
publisher's signed `desktop-v2026.10.1` release tag after checking its pinned
GitHub release asset SHA-256. It installs a temporary local RPM with Fedora
repositories enabled for dependencies. The RPM does not come with a detached
package signature; verification is the pinned release asset digest plus the
verified release tag. `localpkg_gpgcheck=0` applies only to that digest-checked
local artifact.

The disposable Fedora 44 Workstation test applied both the RPM and the
separate Bitwarden AppImage, preserved a synthetic encrypted vault sentinel,
verified package and AppImage state independently, repeated and checked RPM
status, then removed each deployment without changing the other. The
transcript contains no vault contents. Mocked tests cover hash and
package-identity mismatch, existing-install no-op, temporary-file cleanup,
and exact package removal.

Transcript: [transcript.jsonl](../../.acceptance-runs/legacy-vm/.tmp-vm-acceptance-publisher-12-bitwarden-rpm-retry/fedora-44-workstation-x86_64/20261101T165509Z-test-bitwarden-rpm-coexists-with-appimage-and-preserves-vault-f33217e7/transcript.jsonl)
(SHA-256 `5dee4214d474c6013a0ef9f185a75b5df41f49793da822bfc0fa6ca8cdbbab02`)
on Fedora 44 Workstation x86_64 image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
