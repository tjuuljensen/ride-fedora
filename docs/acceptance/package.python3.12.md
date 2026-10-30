# `package.python3.12` acceptance

Status: **PASS; supported Fedora 44 Workstation x86_64 RPM operation**.
Reviewer: Codex, 2026-10-30. The `chepy-runtime` profile selects Fedora's
signed `python3.12` RPM as a separate optional interpreter. It does not
change the system `python3` command. The [Fedora package record](https://packages.fedoraproject.org/pkgs/python3.12/python3.12/)
identifies the package source and Python-2.0.1 license.

One disposable VM test passed in 670.53 seconds on the pinned Fedora 44
Workstation x86_64 image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`
with QEMU TCG. It shares the Chepy lifecycle overlay
`20261030T211617Z-test-chepy-runtime-and-user-cli-a8f20903` under
`.acceptance-runs/chepy/fedora-44-workstation-x86_64/`.
The `metadata.json` catalog SHA-256 is
`ce359e9558c0c92c8e80911acb06c84976c5f62230740281dd2a81f743a355df`;
the tested catalog marked this RPM candidate and it was promoted only
after passing without a handler or source change. The transcript records
the RPM package signature, `rpm -V`, executable version, changed apply,
unchanged repeat, and restore. Restore preserved every pre-existing RPM
name. The user Chepy profile was tested separately in the same VM; its
candidate status does not limit the signed RPM claim. No manual session
was needed.
