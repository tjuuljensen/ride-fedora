# `package.clementine` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. Fedora's signed
[`clementine`](https://packages.fedoraproject.org/pkgs/clementine/clementine/)
RPM supplies the music player and library organizer under the package's
listed GPL, LGPL, Apache, BSD, Qt exception, and MIT component licenses.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T130807Z-test-clementine-opt-in-package-and-profile-3951434e`;
candidate catalog SHA-256
`2aea4bc5e832b9d08590f3c30ac5ec286e88857d089174830105cdff42da2793`.
The retained transcript and `.acceptance-runs/publisher-apps-11-clementine.xml`
record one passing test. The RPM was absent at baseline. It passed plan,
candidate-gated apply, signature/files, executable presence, installed
status, unchanged repeat, restore, and explicit install/remove. The
`music-player` profile also passed plan/apply/repeat/restore. Pre-existing
RPM identities were preserved. Mocked DNF failure evidence is reused from
[base acceptance](package.exfatprogs.md).

No music library or graphical session was used. Desktop visual and broader
recovery checks are [v3.1 item H015](../migrations/progress.md). See the
[batch review](../migrations/publisher-apps-11.md).
