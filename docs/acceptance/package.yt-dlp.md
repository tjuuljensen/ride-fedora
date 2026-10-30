# `package.yt-dlp` acceptance

Status: **PASS; supported** on Fedora 44 Workstation x86_64. Reviewer: Codex,
2026-10-30. Fedora's signed [`yt-dlp` RPM](https://packages.fedoraproject.org/pkgs/yt-dlp/yt-dlp/)
provides a maintained video-downloader CLI under the Unlicense. It is a
separate product and RPM from the already supported `package.youtube-dl`.

One focused disposable VM test passed in 519.58 seconds using the pinned
Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`
and QEMU `tcg` acceleration. The retained overlay is
`20261030T194309Z-test-yt-dlp-native-package-and-youtube-dl-coexistence-c3b3426c`
under `.acceptance-runs/yt-dlp/fedora-44-workstation-x86_64/`. Its
`metadata.json` records candidate catalog SHA-256
`5f30330710525892cae94d954ee9a81d94c41a1d2d03fc23980365a6cb63b117`
and source revision `ea8ab8e`; `transcript.jsonl` and
`.acceptance-runs/yt-dlp-tcg.xml` retain guest commands and the passing result.
The source bundle had uncommitted catalog, test, and documentation changes.

The test checked absent plan, apply, signed RPM and files, executable and
`yt-dlp --version`, installed status, unchanged repeat, restore, explicit
install/remove, and preservation of pre-existing RPM identities. Afterward
it installed `youtube-dl` and `yt-dlp` together, then removed only `yt-dlp`;
`youtube-dl` and its executable remained. The unchanged DNF handler's
mocked failure evidence is in [base package checks](package.exfatprogs.md).
No media was downloaded and no manual session was needed. Site and extractor
compatibility remains H023. The [batch record](../migrations/publisher-apps-05-yt-dlp.md)
and [Windows alignment](../windows-alignment.md#fedora-yt-dlp-downloader-preflight-2026-10-30)
record the scope and contract review. Promotion changed the catalog status
and added an opt-in profile; `default` was not expanded.
