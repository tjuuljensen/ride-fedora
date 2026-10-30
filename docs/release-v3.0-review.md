# v3.0 migration release review

Status: **coverage review reopened**, 2026-10-30. No v3 release tag has been published;
`master` remains the release line. The checked-in
[progress report](migrations/progress.md) is authoritative for current
counts. At the earlier candidate revision, all 180 then-scoped v2 outcomes had a
decision: 28 supported, 26 operable opt-in candidates, 13 replaced,
17 retired, and 96 unsupported. Thus 54 source outcomes are runnable; 26
of those require `--allow-candidate`. The 126 non-runnable decisions do
not represent working installs. The two Citrix and 13 host-specific server
exclusions remained outside that historical denominator. The current ledger
has 185 outcomes and eleven exclusions: the six newly scoped generic server
package outcomes remain unresolved. The owner's later
[v3.0 capability clarification](migrations/v30-path-reassessment.md) makes
working package and setting paths or explicit owner retirement part of v3.0
completion. Only 54 of 169
in-scope package/setting capabilities are currently operable, including
six server package outcomes now assigned review batches. Citrix and Opera remain
out of scope. This prior release
review is therefore no longer a release-ready conclusion.

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
- [x] Verify migration-branch CI and the last Windows catalog, profile,
  run-state, and product alignment record.

Implementation commit `445810a` passed the
[v3 validation workflow](https://github.com/tjuuljensen/ride-fedora/actions/runs/41070406118)
and [shell executable-mode workflow](https://github.com/tjuuljensen/ride-fedora/actions/runs/41070406164).
The [final Windows comparison](windows-alignment.md#package-only-security-batch-and-final-v30-alignment-2026-10-30)
found no unexplained shared-contract drift at `4c90577`.

Publishing a v3 tag and moving `master` are separate release decisions. This
migration branch does neither automatically.
