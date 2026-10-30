# Archive replacement acceptance: `package.7zip` and `package.unar`

Status: **PASS; supported replacement package operations** on Fedora 44
x86_64 Workstation, 2026-10-30. The v2 `InstallPackagingTools` and
`RemovePackagingTools` bundle selected `p7zip` and `unrar`. Fedora 44 has
supported `package.7zip` and `package.unar` operations for equivalent archive
creation/extraction intent, with a changed RAR command. This original
acceptance counted the source outcome as a documented replacement. The later
[Fedora unrar wrapper acceptance](package.unrar.md) restores the command name
and makes the bundle operable through an opt-in profile.

VM evidence: disposable overlay
`20261030T113943Z-test-provider-archive-replacement-batch-ba654452`;
image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
candidate catalog SHA-256
`82463b1b2773ce73896b5b6f04ea24f186160caaf3b0846050c6a84023f5e086`.
The retained transcript and
`.acceptance-runs/provider-foundation-03-archive.xml` record one passing
test. Only the pre-installed 7zip RPM was removed during disposable setup.
Both new operations passed absent plan, apply, signature/files, command
detection, status, unchanged repeat, restore, and explicit remove. Neither
left RPM residue or changed pre-existing RPMs. See the
[batch review](../migrations/provider-foundation-03.md).
