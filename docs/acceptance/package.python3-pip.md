# `package.python3-pip` acceptance

Status: **PASS; supported** on Fedora 44 x86_64 Workstation, 2026-10-30.
The v2 `InstallPythonPip`/`RemovePythonPip` pair maps to the signed Fedora
[`python3-pip` RPM](https://packages.fedoraproject.org/pkgs/python-pip/python3-pip/).
RIDE does not repeat the v2 system-wide `pip install --upgrade pip` command.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T113742Z-test-provider-kernel-and-python-packages-batch-79fd1c85`;
candidate catalog SHA-256
`819b73be3d9d30dec5dfcf9fdd9b2be5013443cf471a33026fdb0ee556897a9c`.
The retained transcript and
`.acceptance-runs/provider-foundation-03-kernel-python.xml` show absent
plan, apply, signed RPM and files, `python3 -m pip --version`, status,
unchanged repeat, restore, and explicit remove. Both inverse paths returned
the full RPM inventory to baseline. The [batch review](../migrations/provider-foundation-03.md)
records the intentional Python 3 and DNF-owned replacement.

Status: **PASS; supported** on Fedora 44 x86_64 Server, 2026-10-30.
Pinned Server image SHA-256
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`;
disposable overlay
`20261030T135447Z-test-server-python3-pip-lifecycle-737577dd`;
catalog SHA-256
`3b196d14641540c8c89d2e9d20d732da68cd7e438bde417ea25ed647cfb7fcb2`.
The test passed absent plan, signed RPM apply, repeat, status, pip version,
restore preview and execution, explicit install/remove, and preservation of
pre-existing packages. Preparation removed a preinstalled `python3-pip` RPM
only in the disposable overlay. No global pip self-upgrade occurred. The
unchanged DNF handler's mocked failure tests are reused.
