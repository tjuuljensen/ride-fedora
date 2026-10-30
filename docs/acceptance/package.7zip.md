# `package.7zip` acceptance

Status: **PASS; supported** on Fedora 44 x86_64 Workstation, 2026-10-30.
Fedora's signed [`7zip` RPM](https://packages.fedoraproject.org/pkgs/7zip/7zip/)
replaces the v2 `p7zip` archive package. The v3 operation supplies `7z`;
it does not alter user archives.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T113943Z-test-provider-archive-replacement-batch-ba654452`;
candidate catalog SHA-256
`82463b1b2773ce73896b5b6f04ea24f186160caaf3b0846050c6a84023f5e086`.
The pinned image had 7zip installed. Test preparation removed only that RPM,
with no other RPM changed, to create an absent baseline in the disposable VM.
The retained transcript and
`.acceptance-runs/provider-foundation-03-archive.xml` show absent plan,
apply, signed RPM and files, `7z` command detection, status, unchanged
repeat, restore, and explicit remove. Both inverse paths returned the full
RPM inventory to that baseline. See the
[archive replacement review](../migrations/provider-foundation-03.md).
