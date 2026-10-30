# `package.unar` acceptance

Status: **PASS; supported** on Fedora 44 x86_64 Workstation, 2026-10-30.
Fedora's signed [`unar` RPM](https://packages.fedoraproject.org/pkgs/unar/unar/)
is the selected RAR-capable archive extractor replacing the v2 `unrar`
package choice. The `unar` CLI differs from `unrar`; this acceptance does not
claim drop-in command compatibility or test user archive contents.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T113943Z-test-provider-archive-replacement-batch-ba654452`;
candidate catalog SHA-256
`82463b1b2773ce73896b5b6f04ea24f186160caaf3b0846050c6a84023f5e086`.
The retained transcript and
`.acceptance-runs/provider-foundation-03-archive.xml` show absent plan,
apply, signed RPM and files, `unar` command detection, status, unchanged
repeat, restore, and explicit remove. The five introduced RPM identities
were removed by each inverse, returning the full RPM inventory to baseline.
See the [archive replacement review](../migrations/provider-foundation-03.md).
