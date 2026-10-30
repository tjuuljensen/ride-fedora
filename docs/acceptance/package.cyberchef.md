# `package.cyberchef` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64.
Reviewer: Codex, 2026-10-30. The `forensic-cyberchef` profile selects only
`package.cyberchef` and requires `--allow-candidate`. It installs the pinned
CyberChef v11.5.0 offline ZIP in `/opt/ride-fedora/cyberchef`, retains all
30 bundled JavaScript license notices and the tagged Apache-2.0 LICENSE,
and links one owned desktop entry. It neither launches a browser during
apply nor changes user recipes or browser profiles. The official
[release](https://github.com/gchq/CyberChef/releases/tag/v11.5.0) publishes
the ZIP SHA-256; its API digest is publisher metadata, not an independent
signature.

One disposable VM test passed in 261.39 seconds on the pinned Fedora 44
Workstation x86_64 image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`
with QEMU TCG. The retained overlay is
`20261030T210257Z-test-cyberchef-offline-desktop-lifecycle-127b3e8b`
under `.acceptance-runs/cyberchef/fedora-44-workstation-x86_64/`.
Its `metadata.json` records pre-evidence catalog SHA-256
`47a8dcf76ad350363ee06cc3f4185ee82049f7ce71eba8443287f9852232375a`,
source revision `544d887`, and an uncommitted source bundle.
`transcript.jsonl` and `.acceptance-runs/cyberchef-tcg.xml` retain the
commands and passing result.

The VM checked absent plan, candidate gate, complete changed journal,
versioned HTML and assets, tagged LICENSE hash, owned manifest verification,
desktop link and Firefox file URI, a nonempty screenshot from Firefox
headless, installed status, unchanged repeat, restore, and explicit
install/remove. Both inverses removed only the owned tree and link and
preserved `/opt/ride-fedora/keep.txt` and a user document. Focused tests
also rejected a failed download, wrong digest, archive traversal, occupied
desktop link, and removal with extra user data. No manual session was needed.

[Batch criteria](../migrations/forensic-isolated-01-cyberchef.md) and
[Windows alignment](../windows-alignment.md#fedora-cyberchef-offline-archive-preflight-2026-10-30)
record the exact scope. Broader visual interaction, browser compatibility,
and update behavior remain H028 in v3.1. The screenshot check proves
headless startup, not complete UI behavior.
