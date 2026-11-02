# VeraCrypt encrypted-volume application

The owner kept VeraCrypt in the v3.0 fast-track review on 2026-10-30.
The signed application path and encrypted-volume-preserving recovery remain
high-risk acceptance work.

Status: **supported on Fedora 44 Workstation x86_64**, 2026-11-01. This
isolated high-risk active-preset outcome maps `InstallVeraCrypt` and
`UninstallVeraCrypt`.
The v2 installer scrapes the first matching HTML link, downloads a moving
tarball, extracts a GUI setup script, and executes it silently. The inverse
calls `veracrypt-uninstall.sh` without an ownership or data journal.

## Completion criteria defined before a runnable operation

- Choose the exact Fedora 44 x86_64 GUI or console distribution. Pin its
  publisher artifact and verify the publisher signature/key fingerprint or
  signed RPM before install. Record all files, driver/FUSE requirements,
  launcher, and package identity.
- Detect and preserve existing VeraCrypt deployments and encrypted volumes.
  Test refusal of untrusted/changed bytes, an interrupted install, and
  removal with a mounted and an unmounted seeded test volume in disposable
  VMs. Never delete, format, unlock, or rekey an existing user volume.
- Require this deeper safety and recovery evidence before any runnable
  status; an opt-in candidate does not waive the encryption gate.

The [publisher's current downloads](https://www.veracrypt.jp/en/Downloads.html)
offer signed Fedora 44 x86_64 GUI and console RPMs, with a published key
fingerprint and SHA-256 manifest. The Linux publisher release is 1.26.30 at
this review; the Windows release is independently versioned. v3 is migrating
the GUI RPM as an opt-in candidate using the detached PGP signature checked
against the publisher's published fingerprint. It must not import a key into
the system RPM database; the exact local RPM is independently verified before
DNF installs it. Package removal may remove only the installed application,
never volume files or mounted filesystems.

The high-risk gate passed on the declared Fedora 44 Workstation x86_64 target.
Mocked provider tests reject a bad detached signature before DNF and verify
temporary artifact cleanup after a failed DNF transaction. The disposable VM
run rejected removal while the test volume was mounted, preserved its sentinel
and package, then removed the package after unmount. It reinstalled the package,
remounted the same volume, read the sentinel, and removed the application
cleanly. The volume SHA-256 was identical before removal, after removal, and
after reinstall: `4401ff7cf679b32af4966839a0701a5dee55eae4d2852123827d11cc2158c244`.

The VM test uses only a test-created container and fixed test credential; it
does not use any user volume or credential. Fedora reported the empty mount
list with exit status 1, so the removal guard now accepts only that exact
response and fails closed for other unknown output. The first guarded run
confirmed mounted-volume refusal, then exposed the empty-list exit-status case;
the next run passed after the guard fix. An intervening setup attempt timed out
while Fedora loaded package repositories; the setup timeout was raised from
120 to 300 seconds and the final run completed.

Acceptance transcript: `.tmp-vm-acceptance-publisher-02-veracrypt-final-check/fedora-44-workstation-x86_64/20261101T214026Z-test-veracrypt-rpm-lifecycle-preserves-mounted-and-unmounted-test-volume-bd9cd157/transcript.jsonl`
(SHA-256 `fa06c6d43b553abe2b696c885121a7607ae853fee05959450bef46d90abcddf4`).
The pinned VM image SHA-256 is
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Publication of another VeraCrypt version or Windows acceptance does not
establish Fedora support; repeat this target evidence when the artifact or
trust chain changes.
