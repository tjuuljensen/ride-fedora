# `package.chepy` and Python 3.12 runtime acceptance

Status: **PASS; operable opt-in Chepy candidate** on Fedora 44 Workstation
x86_64. Reviewer: Codex, 2026-10-30. `package.python3.12` uses Fedora's
signed RPM and is supported for this exact target. `package.chepy` selects
the [Chepy 7.6.0 PyPI source distribution](https://pypi.org/project/chepy/7.6.0/)
with SHA-256
`f6084689e43d128748c18f79c79d75539abb67ac8245e950b678cfa0da2f5010`.
The [tagged GPL-3.0 license](https://github.com/securisec/chepy/blob/7.6.0/LICENSE)
is linked in the catalog. The exact archive runs in an isolated Python 3.12
user venv; no global pip or PyInstaller step runs. The sdist hash identifies
the acquired bytes, not an independent publisher signature.

One disposable VM test passed in 670.53 seconds on the pinned Fedora 44
Workstation x86_64 image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`
with QEMU TCG. The retained overlay is
`20261030T211617Z-test-chepy-runtime-and-user-cli-a8f20903` under
`.acceptance-runs/chepy/fedora-44-workstation-x86_64/`.
Its `metadata.json` records candidate catalog SHA-256
`ce359e9558c0c92c8e80911acb06c84976c5f62230740281dd2a81f743a355df`,
source revision `04ee690`, and an uncommitted source bundle.
`transcript.jsonl` contains the commands, results, and `pip freeze --all`
output; it recorded 41 installed Python distributions. The catalog was
promoted after this evidence without changing the tested handlers or source.

The VM checked the system profile plan, signed RPM and file verification,
Python version, unchanged repeat, and restore. For the user profile it
checked absent plan, candidate gate, changed journal, exact archive digest,
Chepy 7.6.0 import, CLI help, installed status, unchanged repeat, restore,
explicit install/remove, and sibling user-file preservation. Restore also
preserved every pre-existing RPM name. Focused mocks covered failed download,
wrong digest, occupied destination, failed pip install cleanup, and refusal
to remove an unowned tree. No manual session was needed.

The `chepy-runtime` system profile may be applied without the candidate
flag after promotion. The `forensic-chepy` user profile requires
`--allow-candidate`. Broader transformations, optional plugins, transitive
dependency hash locking, and update behavior remain H029 in v3.1.
[Batch criteria](../migrations/forensic-isolated-01-chepy.md) and
[Windows alignment](../windows-alignment.md#fedora-chepy-isolated-python-preflight-2026-10-30)
record the scope.
