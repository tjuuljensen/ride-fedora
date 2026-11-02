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

The lifecycle passed on 2026-11-01 under QEMU TCG using the Fedora 44
Workstation image `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
The test run ID was `20261101T204618Z-test-autopsy-snap-lifecycle-and-snapshot-recovery-abdcacef`.

The test refused a candidate apply without `--allow-candidate`, installed
Autopsy 4.22.1 from Sleuth Kit Labs, repeated/status-checked the operation,
and verified publisher identity. The installed Snap had publisher-granted
connections for `block-devices`, `dm-crypt`, and `fuse-support`; its two
`system-files` plugs were disconnected. This means installation enables
high-risk disk and FUSE access. RIDE did not create or separately approve those
connections.

Removal created automatic Snap snapshot set `1` (72.5 kB, revision 4). The
external case-output sentinel remained at SHA-256
`6cce7f92e0f85087b1ac989192d899a39cc4afdbae7de927b54838838598ac9c`; a
separate Snap common-data sentinel disappeared on removal and returned after
reinstall plus `snap restore 1 autopsy`. The test removed Autopsy again at the
end. It did not launch the GUI, ingest evidence, or exercise real forensic
case data.

The initial run failed because its assertion expected sensitive interfaces to
be disconnected. The corrected run above records the publisher-granted
connections and passed the lifecycle. `H087` remains queued for channel
freshness and deeper interface and case-data review; the operation stays a
high-risk opt-in candidate.

Evidence files remain in the local `.tmp-vm-acceptance-forensic-09-autopsy-revised/`
run directory. The transcript SHA-256 is
`4bcff199477badb1357157484bbd65b4df80081abc273b5f2b0e4c414d349eef`; the
catalog SHA-256 was `e57ad672e23a4c97da5d09bce71432b0786f03165f6b79df751fbbaafa26b933`.
The source bundle SHA-256 was
`075484563afef919f425ed7e5e044f8a74db078bd665ed20ea63b9aa2afc3d20`.

Sources: the [Autopsy publisher's Linux instructions](https://github.com/sleuthkit/autopsy/blob/develop/Running_Linux_OSX.md)
recommend its Snap on Snap-enabled Linux; the [Snap Store listing](https://snapcraft.io/autopsy)
identifies Sleuth Kit Labs as publisher, shows the `latest/stable` channel and
Apache-2.0 license, and documents the snap's privileged interfaces. The
[Autopsy Snap README](https://github.com/sleuthkit/autopsy/blob/develop/snap/README.md)
describes interface connections and use. Snap documents automatic removal
snapshots in its [snapshot guide](https://snapcraft.io/docs/how-to-guides/manage-snaps/create-data-snapshots/).
