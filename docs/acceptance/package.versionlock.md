# DNF5 versionlock replacement evidence

The legacy `InstallVersionLock`/`RemoveVersionLock` pair targeted the DNF4
`python3-dnf-plugin-versionlock`. On the pinned Fedora 44 Workstation x86_64
image, the DNF5 versionlock command is already available. The acceptance check
ran `rpm -q dnf5` and `dnf5 versionlock --help` read-only and made no package or
policy changes. The v2 package outcome is therefore replaced by the native
Fedora 44 command; RIDE does not manage lock entries.

The focused provider-foundation-04 VM run passed. Transcript:
[provider-foundation-04 VM transcript](../../.acceptance-runs/full-v2-migration/fedora-44-workstation-x86_64/20261030T114934Z-test-provider-editors-and-gnome-utilities-batch-2470cb85/transcript.jsonl),
SHA-256 `43ceda4e0ed5d7489a801f38fa9820dc4fe6f826b4200a10c4d87aa8cb3e5962`.
Image SHA-256: `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
Catalog SHA-256: `75e82decf27356aa62d8ff4fb7a5e4aff96d6733650c5aaca72dd4f685e47bec`.
