# v3.0 migration release review

Status: **review pending**, 2026-10-30. No v3 release tag has been published;
`master` remains the release line. The checked-in
[progress report](migrations/progress.md) is authoritative for current
counts. At this candidate revision, all 180 scoped v2 outcomes have a
decision: 28 supported, 26 operable opt-in candidates, 13 replaced,
14 retired, and 99 unsupported. Thus 54 source outcomes are runnable; 26
of those require `--allow-candidate`. The 126 non-runnable decisions do
not represent working installs. The two Citrix and 13 host-specific server
exclusions remain outside this denominator.

The support matrix is Fedora 44 x86_64 on the edition declared by each
operation. The small `default` and `server-base` profiles retain their
separate VM acceptance. Optional supported packages and settings live in
curated profiles; they are not silently added to either base profile.

## Candidate use in v3.0

Candidate operations are blocked by default. An operator must explicitly
select the operation or opt-in profile and pass `--allow-candidate` for
state-changing commands. Their focused happy-path evidence is linked from
the [operation reference](OPERATIONS.md); named broader work is in the
[v3.1 hardening queue](migrations/progress.md). The opt-in profiles with
candidate operations are `audio-effects`, `commander-file-managers`,
`forensics`, `gnome-privacy`, `gnome-shell-preferences`, `logitech-unifying`,
`music-player`, `network-analysis-tools`, `remote-comms-tools`,
`spotlight-pointer`, and `workstation-monitoring`.

The candidate catalog also contains individually selectable operations not
included in those curated profiles: `package.audit`,
`artifact.capa-linux`, `setting.auditd-enabled`, `package.volatility3`,
`package.hexchat`, `package.chromium`, `package.qbittorrent`,
`package.thunderbird`, `package.flameshot`, `package.gimp`, `package.dia`,
`package.wine`, `package.vlc`, `package.system-config-printer`, and
`package.gnome-tweaks`. Their presence in the catalog is not a base-profile
selection or a claim of broader desktop behavior.

Security, storage, encryption, VPN credentials, Docker service and data,
host-specific server behavior, and other unsupported source outcomes remain
non-runnable until their ledger review triggers are met. Package-only
KeePassXC and NetworkManager plugin support covers signed RPM lifecycle and
seeded-state preservation; it does not manage vaults or VPN connections.
Installing `smartmontools` enabled `smartd` in a disposable VM, so that
source outcome remains non-runnable pending a service-aware inverse.

## Review checks

- [x] Verify the final generated catalog, burndown, and progress reports,
  mocked and Firefox tests, shell checks, and acceptance test collection.
- [x] Verify the promoted optional package-only profiles on the pinned
  Workstation VM without a candidate override; retain other valid VM
  evidence for unchanged handlers and profiles.
- [ ] Verify migration-branch CI and the last Windows catalog, profile,
  run-state, and product alignment record.
- [ ] Decide separately whether to publish a v3 tag and move the release
  line. This migration branch does neither automatically.
