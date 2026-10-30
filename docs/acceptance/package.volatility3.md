# `package.volatility3` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. This is a user-scope core Volatility 3 environment, not a
claim about optional plugins, symbol files, or forensic-image analysis.
The [Volatility 3 release](https://github.com/volatilityfoundation/volatility3/releases)
and [PyPI wheel](https://pypi.org/project/volatility3/2.28.2/) were reviewed;
`requirements/volatility3.txt` pins the 2.28.2 and `pefile` 2024.8.26
wheel SHA-256 values. The license is Volatility Software License 1.0.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T122356Z-test-forensic-volatility3-user-environment-22bc3978`;
candidate catalog SHA-256
`5b0d7f0cd344770296d77758139fc7acba575aaa131e74dbb0bf5458ec4de8a7`.
The retained transcript and
`.acceptance-runs/forensic-isolated-02-volatility3.xml` record one passing
test. As the non-root `ride-test` account, the test passed absent plan,
`--allow-candidate` apply, pinned package/version observation, `vol --help`,
installed status, unchanged repeat, restore, and explicit install/remove.
Both inverse paths removed only the owned venv; a sibling user file stayed
unchanged. No system package or root run journal was used. Focused mocked
tests reject removal of an unmarked path and prove a failed pinned-wheel
install cleans its newly created environment.

The v3.0 claim is limited to the core executable. Broader failure/recovery,
optional plugin dependencies, forensic-image fixtures, and long-term wheel
updates are named in the v3.1 hardening queue. The commented v2 functions
only printed a URL; this VM result is the first working install evidence.
See the [batch review](../migrations/forensic-isolated-02.md).
