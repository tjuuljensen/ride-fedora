# `package.powershell` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64, 2026-11-01.

PowerShell 7.6.6 is installed from Microsoft's versioned universal RPM. The
handler checks the release SHA-256 and RPM name, version, and architecture
before DNF sees it. RIDE does not configure the Microsoft repository or key,
run PowerShell profiles, or touch per-user PowerShell data. The test probes
only `pwsh -NoLogo -NoProfile` and checks package removal.

The release page publishes SHA-256 hashes for the versioned RPM. Microsoft's
RHEL install guide documents universal RPMs; it does not declare Fedora 44 a
supported Microsoft OS target, so v3 records this as a Fedora-specific
opt-in candidate and validates the actual target in a disposable VM.

- [Microsoft PowerShell 7.6.6 release and artifact hashes](https://github.com/PowerShell/PowerShell/releases/tag/v7.6.6)
- [Microsoft RHEL installation guidance](https://learn.microsoft.com/en-us/powershell/scripting/install/install-rhel)
- [PowerShell license](https://github.com/PowerShell/PowerShell/blob/v7.6.6/LICENSE.txt)

The disposable guest passed candidate refusal, plan, pinned download verification, RPM identity check, install, no-profile version probe (`7.6.6`), status, unchanged repeat, and removal. Image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`. Transcript: `.tmp-vm-acceptance-publisher-apps-09/fedora-44-workstation-x86_64/20261101T175313Z-test-pinned-publisher-rpm-lifecycle-fedora-powershell-package-powershell-powersh-9d0b6aa1/transcript.jsonl`, SHA-256 `af973399a97054a7070e0f49a7c39391da4b0e7f858decb49efee7bacf66192c`. The catalog used in that run had SHA-256 `5da5556ef6b7d821b07b84dbb54d0117ce6b639415c35a7b5959bdd23af5e283`. TCG emulation was used; GUI behavior and publisher support for Fedora remain unclaimed.
