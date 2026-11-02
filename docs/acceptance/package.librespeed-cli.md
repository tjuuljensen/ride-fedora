# `package.librespeed-cli` acceptance

Status: **PASS; operable opt-in candidate on Fedora 44 Workstation x86_64**.

The opt-in user-local operation installs LibreSpeed CLI v1.0.14 from the
publisher's Linux amd64 release. It verifies the pinned SHA-256 of the
publisher's checksum manifest and archive, extracts only the binary and
license, and probes the version before placing an owned copy under
`~/.local/opt/ride-fedora/` with a link under `~/.local/bin/`. Status inspects
ownership metadata and file digests without executing the installed program.
Removal refuses changed or unowned files and removes only the exact deployment
and link. User data beside its ownership record remains intact.

The release declares LGPL-3.0-only. The published archive digest is
`89800767ac14085c78a20847ebea23340f6c14a78de0a15c2ac7db8b565c961f`; the
pinned release checksum-manifest digest is
`1cd30f1c4a25b008f2a401ffb4d5617cf5d3b4bc9e44e873f44dd2f2fbd8b3c6`.
Sources: [upstream repository and usage](https://github.com/librespeed/speedtest-cli),
[release v1.0.14](https://github.com/librespeed/speedtest-cli/releases/tag/v1.0.14),
[release asset checksums](https://github.com/librespeed/speedtest-cli/releases/expanded_assets/v1.0.14),
and [tagged license](https://raw.githubusercontent.com/librespeed/speedtest-cli/v1.0.14/LICENSE).

Focused mocked tests cover successful install, repeat, status, exact removal,
manifest/archive digest failures, unsafe archive paths, destination collision,
modified-file refusal, and preservation of adjacent user data. Disposable VM
acceptance runs plan, candidate refusal, apply, repeat, status, and removal as
the target user; it probes only `--version`, preserves a data sentinel, and
confirms the pre-existing `speedtest-cli` RPM query is unchanged. It does not
run a bandwidth test or contact a LibreSpeed server.


The disposable Fedora 44 Workstation x86_64 run passed plan, candidate refusal,
apply, repeat, status, and removal as `ride-test`. The real v1.0.14 Linux amd64
release downloaded successfully; the installed binary reported version 1.0.14.
Removal retained the seeded user-data sentinel, and `speedtest-cli` remained
uninstalled before and after the run. No bandwidth test was run. Image SHA-256:
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
Acceptance transcript:
`/tmp/ride-fedora-librespeed-01/fedora-44-workstation-x86_64/20261031T090243Z-test-librespeed-cli-pinned-user-install-lifecycle-7e44e87c/transcript.jsonl`
(transcript SHA-256 `5fac2b9c47c2394fcfc179da79235b8249afcd95398a844507ec2739d084566b`).
Apply, unchanged repeat, and removal runs are `20261031T090311Z-2527-22458`,
`20261031T090313Z-3079-3379`, and `20261031T090314Z-3322-9590`.
