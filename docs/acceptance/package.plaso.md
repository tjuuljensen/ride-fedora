# Plaso package acceptance

`package.plaso` is an opt-in Fedora 44 Workstation x86_64 RPM operation using
Plaso's documented GIFT stable COPR. The RIDE provider writes an exact owned
repository file with RPM `gpgcheck=1`, installs `plaso-tools` from that repo,
and removes only that package and repository file. It does not read or process
case inputs, create timelines, or remove user case output. A pre-existing repo
file is preserved; changed RIDE-owned repo content blocks repository cleanup.

Focused mocked checks cover exact COPR configuration, package source selection,
repository conflict refusal, and ownership-preserving removal. Fedora 44
Workstation x86_64 TCG acceptance passed candidate gating, plan, apply with
RPM signature verification, package and repository checks, CLI version, repeat,
status, remove, and case-output sentinel preservation.

- Transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-forensic-02-plaso/fedora-44-workstation-x86_64/20261101T201703Z-test-plaso-copr-package-lifecycle-preserves-case-output-19dcd3f8/transcript.jsonl`
- Transcript SHA-256: `6adf65ecd3172d4a2de28e40177448c5bce2e38286bf9154cd8832b01b199ed3`
- Fedora 44 Workstation image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`
- Catalog SHA-256: `b6212663ff8bdbe6ef5c2d52e1a5632c19c858423c01f1700808dec1da68eef3`

Source: [Plaso Fedora packaged release](https://plaso.readthedocs.io/en/latest/sources/user/Fedora-Packaged-Release.html)
documents Fedora 43/44, `@gift/stable`, and `plaso-tools`. The upstream project
declares Apache-2.0 in its
[`pyproject.toml`](https://github.com/log2timeline/plaso/blob/main/pyproject.toml).
