# `package.dfir-unfurl` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64.
Reviewer: Codex, 2026-10-30. The v2 `InstallUnfURL` mutates the user's global
pip environment. The v3 operation installs the current
[`dfir-unfurl` 20261007 wheel](https://pypi.org/project/dfir-unfurl/20261007/)
and 36 dependencies with recorded PyPI SHA-256 hashes in a private user venv.
PyPI identifies Apache-2.0, Python 3.11+, and the `unfurl` and `unfurl_app`
entry points. Wheel hashes pin acquisition; they are not independent
publisher authentication.

One disposable VM test passed in 341.09 seconds on the pinned Fedora 44
Workstation x86_64 image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
QEMU used `tcg` acceleration. The retained overlay is
`20261030T195757Z-test-unfurl-user-environment-54f6f564` under
`.acceptance-runs/unfurl/fedora-44-workstation-x86_64/`.
Its `metadata.json` records candidate catalog SHA-256
`d97a7426c7098890195540a8aef879d6adfd9b29c45482119e1d35f2ec5bbc0f`,
source revision `16cd489`, and an uncommitted source bundle;
`transcript.jsonl` and `.acceptance-runs/unfurl-tcg.xml` retain the commands
and passing result.

The VM checked absent plan, apply, complete changed journal, exact package
version, both entry points, local URL parsing, installed status, unchanged
repeat, restore, and explicit install/remove. Both inverses removed the
owned venv and preserved a sibling user file. Focused mocked tests checked
failed-install cleanup and refusal to remove an unmarked path; existing
Volatility 3 tests passed unchanged. No service was started, no public port
was opened, and no case data or external site was used. No manual session was
needed. [Batch criteria](../migrations/forensic-isolated-01-unfurl.md) and
[Windows alignment](../windows-alignment.md#fedora-unfurl-isolated-python-preflight-2026-10-30)
record the scope. Broader UI, parser, and failure coverage is H025/H002 in
v3.1. The opt-in profile requires `--allow-candidate`.
