# `package.bitwarden-appimage` acceptance

Status: **passed on Fedora 44 Workstation x86_64**, 2026-11-01.

VM: Fedora 44 Workstation x86_64. Result: **PASS**.

VM acceptance **passed** for `package.bitwarden-appimage` on Fedora 44
Workstation. The run verified the supported apply path, repeat, status,
AppImage runtime version output, exact inverse, synthetic vault digest/mode,
and unchanged RPM state. The transcript contains no vault contents.

The accepted lifecycle covers the following on the pinned Fedora 44 x86_64
Workstation target:

- Plan and status identify the user-scoped portable AppImage; normal apply
  works as a supported operation.
- Apply verifies the pinned upstream release manifest and AppImage SHA-512,
  repeat is unchanged, and the executable reports its AppImage runtime version.
- Removal deletes only the unchanged RIDE-owned AppImage and ownership
  manifest. Mocked tests verify modified and colliding files are preserved.
- Seeded files under the user's Bitwarden configuration/data directories keep
  their digest and mode through plan, apply, repeat, status, and removal.
- The separate RPM state is unchanged; transcripts contain no vault contents.

The AppImage install does not start the vault UI or access account data. A
visual session is not needed for this file-placement lifecycle. Use only a
disposable VM with synthetic encrypted-data sentinels.

Transcript: [transcript.jsonl](../../.tmp-vm-acceptance-publisher-06-supported/fedora-44-workstation-x86_64/20261101T163802Z-test-bitwarden-appimage-lifecycle-preserves-vault-files-79623341/transcript.jsonl)
(SHA-256 `07031bcc0b334f6f6bb0b13daa7585c302edfa7182d824520a0b1464a1036653`)
on Fedora 44 Workstation x86_64 image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
