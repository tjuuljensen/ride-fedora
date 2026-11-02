# Forensic Isolated 09: Autopsy Snap access and recovery

Status: **high-risk opt-in candidate; Fedora 44 package lifecycle acceptance
passed, while privileged-access and case-data review remain open**, 2026-11-01.

## Outcome and source

The kept v2 `InstallAutopsy` / `RemoveAutopsy` pair only printed a URL and did
not install or remove Autopsy. The current publisher-supported Linux path is
the Sleuth Kit Labs Snap Store package, exposed as `package.autopsy` in
[`fedora-autopsy`](../../profiles/fedora-autopsy.json). It depends on the
separate Fedora Snap runtime operation. RIDE manages Snap presence and does
not launch the application or process forensic case data.

The [publisher's Linux instructions](https://github.com/sleuthkit/autopsy/blob/develop/Running_Linux_OSX.md)
recommend the Snap on Snap-enabled Linux. The [Snap Store listing](https://snapcraft.io/autopsy)
identifies Sleuth Kit Labs, Apache-2.0, and stable version 4.22.1 (last updated
2025-05-19). This stable channel lags the latest publisher ZIP. The listing
describes the Snap as highly privileged, including interfaces for raw disks,
dm-crypt, FUSE, removable media, mount observation, `/dev`, and huge pages.

## Fedora 44 observation

The first Fedora 44 Workstation x86_64 VM attempt installed the Snap and
confirmed its publisher. `snap connections autopsy` showed publisher-granted
connections for `block-devices`, `dm-crypt`, and `fuse-support`; both
`system-files` plugs (`system-files-dev` and `system-files-hugepages`) were
disconnected. The Snap's own listing says these sensitive interfaces normally
need manual connections, while Snap's policy documentation allows publisher
assertions to grant auto-connect permission. This access is activated by Snap
installation even though RIDE does not create or manage those connections.

This is high-risk and must remain opt-in. The first test expectation that all
privileged interfaces would be disconnected was incorrect and stopped that run
before removal. The corrected acceptance verifies the observed connections,
completes automatic data snapshot and restore, and proves an unrelated
case-output sentinel is unchanged. `H087` tracks interface exposure,
stable-channel freshness, and broader disposable case-data behavior before any
promotion beyond candidate.

## Evidence and next action

- Focused Snap lifecycle unit tests and runtime catalog validation pass.
- The corrected [Fedora 44 acceptance record](../acceptance/package.autopsy.md)
  passed candidate gating, install, repeat/status, interface inspection,
  removal, automatic snapshot, reinstall, restore, and final removal.
- Keep this high-risk candidate opt-in and review H087 before promotion.
- Windows uses a separate Autopsy MSI path; Fedora's Snap runtime and
  publisher-granted interface behavior do not transfer to Windows.
