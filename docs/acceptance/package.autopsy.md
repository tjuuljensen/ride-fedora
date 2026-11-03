# Autopsy Snap acceptance

`package.autopsy` is an opt-in Fedora 44 Workstation x86_64 Snap Store package
operation. It depends on the separate `package.snapd` runtime operation and
installs the Sleuth Kit Labs publisher's `autopsy` Snap from `latest/stable`.
RIDE checks and changes app presence only. It does not launch Autopsy, connect
privileged interfaces, inspect disks, or process case data. Removing the Snap
uses the default non-purge path so Snap creates its automatic data snapshot;
Snap documents 31-day automatic snapshot retention and restore through
`snap restore`.

## Fedora 44 Workstation x86_64 acceptance

The package and empty-case preservation lifecycle passed on 2026-11-02 under
QEMU TCG using the Fedora 44
Workstation image `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
The test run ID was
`20261102T223550Z-test-autopsy-snap-lifecycle-and-snapshot-recovery-3212df40`.

The test refused a candidate apply without `--allow-candidate`, installed
Autopsy 4.22.1 from Sleuth Kit Labs, repeated/status-checked the operation,
and verified publisher identity. The installed Snap had automatically
connected `block-devices`, `dm-crypt`, and `fuse-support`; its two
`system-files` plugs were disconnected. This means installation enables
high-risk disk and FUSE access. RIDE did not create or separately approve those
connections.

Using the publisher-documented headless `--createCase` command, the test made
an empty synthetic case under the disposable user's Documents directory. It
verified the `.aut` file, ran SQLite `integrity_check` on `autopsy.db`, then
stopped only the app session created for the fixture. The case-tree hash was
`0071f4053f0451533c0c851e300bec657783ceffa7707d276049730ef17f85ef`; it
remained identical after package removal and after Snap restore. The external
case-output sentinel also remained at SHA-256
`6cce7f92e0f85087b1ac989192d899a39cc4afdbae7de927b54838838598ac9c`.
Removal created automatic Snap snapshot set `1` (10.2 MB, revision 4). A
separate Snap common-data sentinel disappeared on removal and returned after
reinstall plus `snap restore 1 autopsy`. The test removed Autopsy again at the
end. It did not add a data source, ingest evidence, or exercise the GUI.

This meets the v3.0 `private-output-boundary`, `no-evidence-processing`, and
`exact-output-preservation` checks for RIDE's package-presence lifecycle. It
does not validate forensic analysis accuracy or the application's use of its
privileged interfaces.

The initial run failed because its assertion expected sensitive interfaces to
be disconnected. A later attempt under `/tmp` failed after the host's
19,145 MiB user quota was exhausted; QEMU reported guest disk I/O errors. That
failure was investigated and the accepted run stores its overlay under the
workspace on `/home`, outside the exhausted tmpfs quota. The corrected run
above records the connections and passed the lifecycle. A source freshness
review on 2026-11-02 found that the Snap
Store stable channel still serves 4.22.1 (last updated 2025-05-19), while the
upstream GitHub releases page lists signed release 4.23.1 from 2026-05-07.
The Snap path therefore lags upstream; this v3.0 operation remains an opt-in
candidate, not a claim of current upstream parity. `H087` tracks channel
freshness and GUI/forensic workflow review beyond the accepted package-
presence boundary.

Evidence files remain in the ignored local
`.acceptance-runs/autopsy-case-recovery/fedora-44-workstation-x86_64/`
directory. The accepted run used the pinned Fedora image above and TCG
acceleration. Its transcript SHA-256 is
`4e186581f71659b573bd938c3520ce10963d727f947ef6ddbec78cb0c670d8cb`;
the catalog SHA-256 is
`f875387a5356e8d175619c921d289c8771569398429eb33769f0fb3a54252af7`; the
source bundle SHA-256 is
`76126183cb70b8c389a2bbac53132289beef6110b041a27b8ed54ca1a2ad66a5`.

Sources: the [Autopsy publisher's Linux instructions](https://github.com/sleuthkit/autopsy/blob/develop/Running_Linux_OSX.md)
recommend its Snap on Snap-enabled Linux; the [Snap Store listing](https://snapcraft.io/autopsy)
identifies Sleuth Kit Labs as publisher, shows the `latest/stable` channel and
Apache-2.0 license, and documents the snap's privileged interfaces. The
[upstream release page](https://github.com/sleuthkit/autopsy/releases)
lists signed release 4.23.1, newer than the current Snap Store version. Snap's
[interface documentation](https://snapcraft.io/docs/interface-management/)
explains publisher requests for interface auto-connection. The
[Autopsy Snap README](https://github.com/sleuthkit/autopsy/blob/develop/snap/README.md)
describes interface connections and use. Snap documents automatic removal
snapshots in its [snapshot guide](https://snapcraft.io/docs/how-to-guides/manage-snaps/create-data-snapshots/).
