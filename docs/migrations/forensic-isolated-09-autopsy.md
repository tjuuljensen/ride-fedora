# Forensic Isolated 09: Autopsy Snap access and recovery

Status: **high-risk opt-in candidate; Fedora 44 package-presence and empty-case
preservation acceptance passed; GUI and forensic workflow review remains in
v3.1**, 2026-11-02.

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
2025-05-19). A 2026-11-02 source review found signed upstream release 4.23.1
dated 2026-05-07, so the Store channel currently lags upstream. Keep the
Store-backed path for v3.0's reviewed deployment and disclose that lag; do not
claim release parity. The listing describes the Snap as highly privileged,
including interfaces for raw disks, dm-crypt, FUSE, removable media, mount
observation, `/dev`, and huge pages.

## Completion checks

Before accepting the Fedora 44 Workstation x86_64 candidate lifecycle, verify:

1. `plan` identifies the opt-in candidate and `apply` refuses it without
   `--allow-candidate`; apply, repeat, and status identify the Store package
   and publisher.
2. Record `snap connections autopsy` on the exact target. Do not infer the
   effective access from plug declarations; preserve the observed device,
   dm-crypt, FUSE, and system-files states in the evidence.
3. Use Autopsy's documented headless `--createCase` command to create an empty
   synthetic case below the disposable user's Documents directory. Confirm
   the generated `.aut` file and `autopsy.db` exist, verify SQLite integrity,
   wait for the database size to settle, stop only the case-creation app
   session, then hash every file in the case tree.
4. Remove Autopsy through RIDE, verify Snap's automatic snapshot, reinstall,
   restore Snap-owned test state, and prove every case-tree hash and external
   synthetic sentinel is unchanged. Remove Autopsy again and retain the case
   tree until the assertions finish.

The test must not add a disk device or ingest forensic evidence. A case tree
outside Snap's data directory models user-owned case output; RIDE's package
inverse must not delete or rewrite it. This verifies the package lifecycle's
ownership boundary, not Autopsy's forensic analysis accuracy.

## Fedora 44 observation

The first Fedora 44 Workstation x86_64 VM attempt installed the Snap and
confirmed its publisher. `snap connections autopsy` showed automatic
connections for `block-devices`, `dm-crypt`, and `fuse-support`; both
`system-files` plugs (`system-files-dev` and `system-files-hugepages`) were
disconnected. The Snap's own listing says these sensitive interfaces normally
need manual connections, while Snap's policy documentation allows publisher
assertions to grant auto-connect permission. This access is activated by Snap
installation even though RIDE does not create or manage those connections.

This is high-risk and must remain opt-in. Snap's interface documentation
explains that publishers may request permission to auto-connect interfaces;
the acceptance run records the actual connected state on Fedora 44 rather
than inferring it from the listing. The first test expectation that all
privileged interfaces would be disconnected was incorrect and stopped that run
before removal. The corrected acceptance verifies the observed connections,
completes automatic data snapshot and restore, and proves an unrelated
case-output sentinel is unchanged. The follow-up acceptance creates a genuine
empty Autopsy case, checks its SQLite database, and verifies unchanged case
files after package removal and restore. This closes the data-preservation
gate for RIDE's package-presence operation; the separate app's privileged
forensic workflow is outside that operation. `H087` tracks Store freshness,
GUI launch, and synthetic analysis workflow review in v3.1.

## Evidence and next action

- Focused Snap lifecycle unit tests and runtime catalog validation pass.
- The [Fedora 44 acceptance record](../acceptance/package.autopsy.md) passed
  candidate gating, install, repeat/status, interface inspection, empty-case
  database integrity, case-tree preservation, removal, automatic snapshot,
  reinstall, restore, and final removal.
- The package-presence path is operable as an opt-in candidate; H087 remains
  v3.1 hardening for upstream freshness and app-level forensic workflows.
- Windows uses a separate Autopsy MSI path; Fedora's Snap runtime and
  publisher-granted interface behavior do not transfer to Windows.
