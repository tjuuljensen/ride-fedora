# `package.openssh-clients` acceptance draft

Status: `candidate`; Fedora 44 Workstation and Server x86_64 VM checks passed
on 2026-10-30. Product: Fedora `openssh-clients` RPM, installed deployment,
`fedora-rpm` source, system scope. The operation declares only `installed`
and `recovery: none`. It never promises to remove the package or restore a
previous SSH configuration. Fedora's
[subpackage record](https://packages.fedoraproject.org/pkgs/openssh/openssh-clients/)
identifies the client tools and license. The [Windows comparison](../windows-alignment.md)
records the deliberate Linux recovery limit and lack of a Windows OpenSSH row.

| Exact target | Outcome and evidence |
| --- | --- |
| Fedora 44 Workstation x86_64, `VARIANT_ID=workstation` | PASS: pinned image SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`; intact overlay `20261030T074126Z-test-installed-only-package-keeps-existing-client-and-server-c33dc9b7`, repair/failure overlay `20261030T074158Z-test-installed-only-package-repairs-absence-and-refuses-inverse-5ad1de81`, edition gate, and [batch record](openssh-clients-workstation-pilot.md). |
| Fedora 44 Server x86_64, `VARIANT_ID=server` | PASS: pinned image SHA-256 `efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`; intact overlay `20261030T075815Z-test-installed-only-package-keeps-existing-client-and-server-928cb116`, repair/failure overlay `20261030T075842Z-test-installed-only-package-repairs-absence-and-refuses-inverse-76f28e72`, edition gate, and [Server record](server-base-package-pilot.md). |

Both editions passed read-only plan, two unchanged applies, installed status,
signed RPM/file verification, `ssh -V`, unchanged `/etc/ssh/ssh_config`
checksum and package inventory, and active SSH server. Each separate
disposable overlay used `rpm -e --nodeps` solely to create an artificial
absence, then RIDE repaired the package before a later injected failure.
Journals recorded changed and failed steps with `recovery: none`; `dnf check`
passed after repair. Repeat apply was unchanged; restore and explicit remove
refused without changing inventory or configuration. Discarding the overlay
is recovery for the artificial state. The first Workstation attempt failed
before RIDE mutation because DNF correctly refused removal of GNOME-required
client tools; that failure remains in the [batch record](openssh-clients-workstation-pilot.md).
Profile smokes passed. No manual session was needed.

Workstation catalog SHA-256 was
`0a105c19f6d7166d6e59e0810eea96aef7f5ce53feb92b17a8f4a78eae13029d`;
Server catalog SHA-256 was
`27e2a8310a56123488a25a3c9dd74631365e4acbe8085e542247d9280f4d6bf5`.
Source was uncommitted during both runs. Each overlay retains `metadata.json`
and `transcript.jsonl`. Technical review on 2026-10-30: Codex checked the
Fedora [subpackage record](https://packages.fedoraproject.org/pkgs/openssh/openssh-clients/)
against the catalog product, Fedora 44 build, upstream link, and license;
the cited Workstation and Server JUnit suites have no failures. The archived
`lib/v3/providers.sh` and `lib/v3/state.sh` match commit `81f604f` byte for
byte. Relative to the Workstation installed-only archive, this operation
changed only its target list to add Server; the Server suite ran the current
row and both edition gates covered target selection. Owner acceptance and
other-host run inventory remain pending. The local non-disposable run
directory was absent.
