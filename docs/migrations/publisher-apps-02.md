# VeraCrypt encrypted-volume application

The owner kept VeraCrypt in the v3.0 fast-track review on 2026-10-30.
The signed application path and encrypted-volume-preserving recovery remain
high-risk acceptance work.

Status: **unsupported for v3.0**, 2026-10-30. This isolated high-risk
active-preset outcome maps `InstallVeraCrypt` and `UninstallVeraCrypt`.
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
fingerprint and hash files. The Linux publisher release is 1.26.30 at this
review; the Windows release is independently versioned. A verified RPM
route is available in principle, but v3 has no publisher-RPM trust/import
handler, installation journal, or seeded encrypted-volume recovery evidence.
This source outcome is **non-runnable unsupported in v3.0**. Reopen for a
specific GUI/console deployment with the signature and volume-preservation
tests above. Publication of a VeraCrypt version or Windows acceptance does
not establish Fedora support.
