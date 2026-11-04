# Provider foundation batch 06: Security Lab group

Status: **v3.0 migration in progress**, reviewed 2026-10-31.
The owner chose **keep** for the Security Lab capability. Migrate its Fedora
44 group members into explicit package operations and curated opt-in profiles
in focused batches. Do not expose the changing DNF group or broad group removal
as a v3 operation. Reuse accepted package evidence for unchanged operations;
test only new or newly composed behavior.
The commented v2 pair `InstallSecurityLab`/`RemoveSecurityLab` invokes DNF
`group install` and `group remove` for `security-lab`. This is a changing
collection rather than one product. Fedora's
[DNF5 group contract](https://dnf5.readthedocs.io/en/stable/commands/group.8.html)
tracks group membership and package reasons separately from an individual
RPM install. The v3 DNF package handler observes one RPM at a time; it does
not own a DNF group or capture a safe inverse for the group's state.

## Completion criteria defined before resolution

- Query the exact Fedora 44 x86_64 Workstation group and installed-group
  state read-only in a disposable VM. Identify overlap with individually
  tracked v2 outcomes and accepted v3 operations.
- Prefer a bounded opt-in set of Fedora RPM operations, reusing package source
  metadata and accepted handler evidence. Run brief exact-target lifecycles
  for newly selected packages. A direct group migration would additionally
  need a VM inverse preserving pre-existing packages and group marks.
- For each small profile batch, prove every selected package is a member of
  the Fedora 44 group, keep the profile out of `default`, and check plan,
  apply, repeat, status, RPM signature and file verification, removal, and
  preservation of pre-existing RPM name/architecture identities. Record any
  Fedora dependency upgrades caused by a selected package and allow only
  declared package-specific upgrades; do not attempt a downgrade on removal.
  Reuse individual acceptance records for operations whose source and handler
  are unchanged.
- Track the full 137-package inventory against v3 operations. Mark the
  `SecurityLab` source outcome unresolved until the full group capability is
  represented by batches or a reviewed replacement; a curated first profile
  is partial progress, not completion.

## Fedora 44 inspection and v3.0 decision

The pinned Workstation image SHA-256 was
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
In disposable overlay `provider-security-lab-inventory-root`, read-only
`sudo dnf5 group info security-lab` passed and reported **137 default
packages**; the group was not installed. `sudo dnf5 group list --installed`
also passed and showed unrelated installed groups. The retained transcript
is under `.acceptance-runs/full-v2-migration/fedora-44-workstation-x86_64/`.
An initial unprivileged `dnf5 group info` attempt failed before returning
metadata because it could not open the system DNF lock. The privileged
read-only rerun resolved that query failure; neither run installed a package.

The group includes `binwalk`, `dc3dd`, `ewftools`, `htop`, `lynis`, `pwgen`,
`sleuthkit`, `testdisk`, and `vim-enhanced`, among many unrelated tools.
`dc3dd`, `htop`, `lynis`, `pwgen`, and `vim-enhanced` already have separately
accepted Fedora package operations; other listed tools remain candidates or
separate migration outcomes. A group apply would silently include far more
software than those scoped operations. Group removal also cannot be mapped
to RIDE's current per-package run journal without risking changes to
pre-existing package or group state.

### Batch 06A: Reuse accepted Fedora package operations

Start with six exact group members whose package operations are already
supported and accepted on Fedora 44 Workstation: `binwalk`, `dc3dd`, `htop`,
`lynis`, `pwgen`, and `vim-enhanced`. Build the opt-in
`fedora-security-lab-core` profile from those stable IDs. No handler, source,
or package operation changes in this batch. Before the VM run, assert the
target and exact baseline package identities; check plan, apply, repeat,
status, signature and RPM file verification, profile removal, and restoration
of the baseline package identities. A previously installed package must
remain installed after profile removal. `vim-enhanced` may upgrade the
pre-existing `vim-minimal` and `vim-data` packages to Fedora's matching
version; this is recorded and retained after removal instead of downgraded.
Any other package identity or version change fails the batch. The individual
accepted operation records are reused; the combined profile receives its own
brief disposable-VM check.

The `SecurityLab` source outcome remains **in progress** until all 137 group
members are reconciled into opt-in package batches or a reviewed replacement.
Forensic packages already owned by their dedicated source outcomes remain
tracked there as well; this profile composes only the six named IDs and does
not replace those outcomes.

### Batch 06B: Network discovery and packet analysis

Compose the group members `nmap-ncat`, `nmap`, `tcpdump`, `wireshark-cli`, and
`wireshark` in the opt-in `fedora-security-lab-network` profile. Reuse the
accepted Fedora 44 package lifecycles for Ncat, Nmap, tcpdump, and Wireshark;
add an exact Fedora RPM operation for the group member `wireshark-cli` using
the existing DNF provider. Profile ordering must record Ncat and the CLI
package before their higher-level consumers so inverse ownership remains
precise. This batch does not enable capture permissions or start capture
traffic.

Before the VM run, assert all five are Security Lab members and capture their
exact pre-existing package identities. Check candidate gating and plan, apply
with `--allow-candidate`, repeat, status, repository signature metadata,
`rpm -V`, and read-only CLI version/help probes. Restore the apply run and
prove all pre-existing package identities remain, newly installed packages
and unused dependencies are removed, and any Fedora-required upgrades are
limited to packages named in the DNF transactions. `remove --profile` sets
every profile member absent; it is not the exact inverse for packages that
were already installed. Do not attempt package downgrades.
The profile remains opt-in and candidate-gated. Existing per-package VM
evidence is reused for unchanged operations; the new CLI operation and the
profile composition receive focused disposable-VM evidence.

The batch places four previously catalog-only members into a profile and adds
the new `wireshark-cli` operation. At that point seven existing operations
remained catalog-only; 119 group members were still unmapped. Batch 06C places
three of those seven; four catalog-only operations remain after the 06C pass.

### Batch 06C: Forensic image and recovery utilities

Compose the Security Lab members `ewftools`, `sleuthkit`, and `testdisk` in an
opt-in profile. Before the VM run, assert all three group memberships, exact
profile IDs, Fedora 44 Workstation target, candidate gating and plan. Check
first apply, repeat, status, repository signatures, root-run `rpm -V`, and
read-only tool version/help probes. Restore the apply run and prove the
pre-run RPM name/architecture set returns exactly; Fedora-required upgrades
may remain only when named in the transaction output. No evidence image is
mounted or modified. The existing general `forensics` profile remains
separate; this profile records only these three Security Lab group members.
The Fedora 44 Workstation VM passed on 2026-10-31; exact apply/restore
evidence is recorded in [Security Lab forensic profile acceptance](../acceptance/security-lab-forensics.md).

### Batch 06D: Network diagnostics

Compose the remaining catalog-backed members `macchanger`, `mtr`, `nethogs`,
and `whois` in an opt-in profile. Reuse the accepted individual Fedora 44
package lifecycles from the network-tools and ASN batches. The profile check
asserts the four group memberships, candidate refusal, plan, apply, repeat,
status, repository signatures, root-run `rpm -V`, and that each command is
available. Restore the apply run and compare the exact RPM name/architecture
set; version changes may persist only for packages named in DNF upgrade
transactions. It does not run macchanger, capture packets, or contact external
lookup services.

The Fedora 44 Workstation VM passed on 2026-10-31. The first four opt-in
profiles map 18 group members; 119 of the 137 observed packages were then
unmapped. Batch 06E below adds five more, bringing current coverage to 23/137
and leaving 114 unmapped. Its combined lifecycle is recorded in [Security Lab
network utilities acceptance](../acceptance/security-lab-network-utilities.md).

### Batch 06E: Network and terminal utilities

This batch adds the unmapped Security Lab group members `bmon`, `fping`,
`iftop`, `lnav`, and `nload` to the opt-in
`fedora-security-lab-network-utilities` profile. Fedora 44 packages and
metadata are available for all five. Fedora package pages record upstream
projects and licenses: bmon (BSD-2-Clause AND MIT), fping (BSD-4.3TAHOE),
iftop (GPL-2.0-or-later AND BSD-4-Clause-UC), lnav
(LicenseRef-Callaway-BSD), and nload (GPL-2.0-or-later). Install from Fedora's
signed RPM repositories; do not run packet, ping, bandwidth, or log workloads
as part of package lifecycle acceptance.

Completion checks are defined before implementation: assert that each exact
package is a member of the pinned 137-package Fedora 44 `security-lab` group;
use one stable Fedora RPM operation per package and keep the profile out of
the base profiles; test candidate gating and plan/apply/repeat/status for the
five-package profile on Fedora 44 Workstation x86_64; verify repository RPM
signatures and `rpm -V`; restore the apply run; and compare pre-existing RPM
name/architecture identities, allowing residue only for packages explicitly
shown in the DNF transaction. Probe only local version/help output, never
generate network traffic or open log files. Review DNF transaction output if
it upgrades any existing package before retrying. Unchanged package handlers
reuse the focused engine tests; this batch adds the profile acceptance and
inventory cross-check.


### Batch 06E result: passed

The pinned Fedora 44 Workstation x86_64 VM passed the declared checks on
2026-10-31. Candidate apply without `--allow-candidate` failed before creating
a run journal. The opt-in profile plan listed the exact five candidates; the
explicit apply installed them from signed Fedora repositories. RPM signature
metadata was present, `rpm -V` was clean, and local help/version probes worked
for all five (bmon's help exits 1 while printing its help text). A second apply
reported all five unchanged. Restoring the first run removed all five packages
and the otherwise-unused `libconfuse` dependency. The RPM inventory returned
exactly to its 1,913-package baseline; no existing package identity or version
changed. The run used the pinned image SHA-256 recorded in the acceptance
report.

The five operations are now `supported` on Fedora 44 Workstation x86_64 and
remain outside the base profiles in `fedora-security-lab-network-utilities`.
Current coverage is five profiles and 23 of 137 observed group packages; 114
remain unmapped for subsequent focused batches. Continue with another ordinary
four-to-six package batch after reviewing its exact inventory membership and
upstream metadata.

### Batch 06F: Network client and relay utilities

Before implementation, define completion checks for the next four exact
members: `httpie`, `iperf`, `irssi`, and `socat`. Confirm each membership in
the pinned Fedora 44 Security Lab inventory; retain Fedora's signed RPM as
the acquisition path and keep all four in a separate opt-in profile. On the
pinned Workstation x86_64 target, automate plan, candidate refusal without
opt-in, apply, repeat, status, repository signature, `rpm -V`, local help or
version output, and restore. Compare the full RPM inventory before and after; allow an existing
package version change only when the DNF transaction explicitly identifies it
as a dependency upgrade, record its exact before/after versions, and do not
downgrade it during recovery. Do not send HTTP, iperf, IRC, or relay traffic.
Reuse the unchanged DNF package handler checks.

Fedora 44 packages are present for httpie 3.2.4-12.fc44 (BSD-3-Clause), iperf
2.2.1-4.fc44 (BSD-3-Clause), irssi 1.4.5-11.fc44 (Fedora's listed component
licenses), and socat 1.8.1.3-1.fc44 (GPL-2.0-only). Fedora package records
link their upstream projects and provide the license metadata. The existing
`package.screen` is scoped to the Server edition, so it is excluded from this
Workstation batch and its separate Server evidence remains unchanged.


### Batch 06F result: passed

The pinned Fedora 44 Workstation x86_64 VM passed the declared checks on
2026-10-31. Candidate apply without `--allow-candidate` was refused without a
run journal. The opt-in profile installed `httpie`, `iperf`, `irssi`, and
`socat` from Fedora-signed RPMs; all four passed signature checks, `rpm -V`,
local help probes, status, repeat apply, and restore. No network workload was
run.

The DNF transaction for HTTPie upgraded the pre-existing
`python3-requests` package from `2.32.5-5.fc44` to `2.33.1-1.fc44` as an
explicit dependency replacement. That shared package update remains after
restore. All other package state returned to baseline, with no introduced
dependency residue. The 1,913-package baseline was restored except for the
documented version update. This accepted update is recorded in the [combined
acceptance report](../acceptance/security-lab-network-clients.md).

The four operations are now `supported` on Fedora 44 Workstation x86_64 and
remain in the opt-in `fedora-security-lab-network-clients` profile. Six
profiles map 27 of 137 observed group members; 110 remain unmapped for focused
batches. Continue by defining exact membership and recovery checks before
selecting the next four-to-six packages.

### Batch 06G: DNS inspection utilities

Before implementation, define checks for the exact Security Lab members
`dnsenum`, `dnstracer`, `dnstop`, and `fpdns`. Confirm membership against the
pinned Fedora 44 inventory and use the signed Fedora RPM source for each. Keep
them in a separate opt-in profile. On Fedora 44 Workstation x86_64, automate
plan, refusal without candidate opt-in, apply, repeat, status, RPM signature,
`rpm -V`, local help output, and restore. Compare package identities and
versions before and after, and inspect DNF output for any dependency update.
Do not query external DNS, capture live packets, or enumerate any domain; the
acceptance session is package lifecycle only. `fpdns -v` prints its version
and exits 255; validate the exact version output alongside the observed code. Inspect the exact DNF transaction
for any existing package upgrades and allow only the dependency updates it
records; preserve those updates after restore, and require all newly introduced
packages to be removed. Reuse the unchanged DNF handler tests.


### Batch 06G result: passed

The pinned Fedora 44 Workstation x86_64 VM passed the declared lifecycle on
2026-10-31. Candidate apply without `--allow-candidate` created no journal.
The opt-in profile applied four Fedora-signed packages; signature metadata,
`rpm -V`, status, repeat apply, and restore all passed. Local probes sent no
DNS queries and opened no capture interface. `fpdns -v` printed the expected
version and returned 255, which is now explicitly covered by its probe check.

DNSenum's DNF transaction installed 46 packages and upgraded the pre-existing
`perl-Errno`, `perl-interpreter`, and `perl-libs` RPMs to Fedora's recorded
updates. All three exact replacements remain after restore; the 46 introduced
packages and the other three selected tools were removed. Inventory returned
to 1,913 package records with only those three documented version changes.
See the [combined 06G acceptance report](../acceptance/security-lab-dns-tools.md).

The four operations are supported for Fedora 44 Workstation x86_64 and remain
in the opt-in `fedora-security-lab-dns-tools` profile. Eight profiles now map
35 of 137 group members; 102 remain for future batches.

### Batch 06H: Network discovery and audit clients

Before implementation, define checks for the exact Fedora Security Lab group
members `arp-scan`, `argus-clients`, `dnsmap`, and `nmbscan`. Confirm membership
in the pinned inventory, use each Fedora-signed RPM, and place all four in a
new opt-in Workstation profile. Automate candidate refusal, plan/apply/repeat/
status, package signatures, `rpm -V`, local CLI usage output where the option
is safe, and restore. Assert exact baseline package identities and versions
except for dependency upgrades explicitly recorded in the DNF transaction;
remove all introduced packages on restore. Do not issue ARP, DNS, SMB, or Argus
traffic. The DNSmap probe supplies no domain; it must stop after printing
usage. `argus` (the daemon package) stays for a separately reviewed service
batch; this batch includes only `argus-clients`.

### Batch 06H result: passed

The pinned Fedora 44 Workstation x86_64 VM passed the declared package
lifecycle on 2026-10-31. All four RPMs came from Fedora repositories and had
signature metadata; each passed `rpm -V`. `arp-scan --help` and `ra -h`
printed local usage. DNSmap's no-argument probe printed usage and performed
no lookup; `nmbscan` was checked through its installed command and packaged
manual page without starting a scan. No ARP, DNS, SMB, or Argus traffic was
sent.

Repeat apply reported all four packages unchanged. Restore removed all 39
introduced RPMs and returned the inventory from 1,952 to the 1,913-package
baseline, except for three Fedora Perl dependency upgrades recorded by DNF:
`perl-Errno` `1.38-523.fc44` to `1.38-525.fc44`, and `perl-interpreter` plus
`perl-libs` `5.42.1-523.fc44` to `5.42.3-525.fc44`. No pre-existing package
was removed. See the [combined 06H acceptance report](../acceptance/security-lab-network-discovery.md).

All four operations are supported for Fedora 44 Workstation x86_64 and remain
in the opt-in `fedora-security-lab-network-discovery` profile. Eight profiles
now map 35 of 137 group members; 102 remain for future batches. The daemon
package `argus` remains in scope for a service-specific review.

### Batch 06I: HTTP and TCP traffic utilities

Select the exact Fedora Security Lab members `httping`, `httpry`, `tcpflow`,
and `tcpick` for one opt-in profile. Fedora 44 publishes native RPMs for all
four; Fedora package records identify their upstream projects and licenses.
Their tools send HTTP requests or inspect captured traffic when actively used,
so acceptance is limited to install, package verification, local version/help
output, status, repeat, and restore. Do not supply a URL, open an interface,
or read or write a capture. Confirm all four inventory memberships before
implementation. Reuse the unchanged DNF package handler evidence and record
any exact dependency replacement that the transaction makes.

### Batch 06I result: passed

The pinned Fedora 44 Workstation x86_64 VM passed both the candidate lifecycle
and the supported-operation lifecycle on 2026-10-31. All four Fedora RPMs had
signature metadata and passed `rpm -V`; local help probes succeeded for all
four. No URL or interface was supplied and no capture was opened. Repeat apply
reported all packages unchanged. Restore removed all four and returned the
exact 1,913-package baseline; no dependency or pre-existing RPM changed. The
initial `httping -h` probe failed because `-h` needs an argument; after the
transcript confirmed it made no request, the check was corrected to
`httping --help`. See the [06I acceptance report](../acceptance/security-lab-network-traffic.md).

All four operations are supported for Fedora 44 Workstation x86_64 in the
opt-in `fedora-security-lab-network-traffic` profile. Nine profiles now map
39 of 137 group members; 98 remain for future batches.

### Batch 06J: Forensic media and file inspection packages

Select the exact Security Lab members `dcfldd`, `ddrescue`, `foremost`, and
`hexedit`. Fedora 44 publishes signed native RPMs for all four and records
their upstream/license metadata. Use those Fedora RPMs; do not fetch or run
upstream installers. This v3 scope owns package presence only. It does not
image, wipe, recover, carve, open, or edit a disk, device, evidence image, or
user file.

Before implementation, require the pinned inventory to confirm membership
and keep the profile opt-in. On the Fedora 44 Workstation x86_64 VM, verify
candidate refusal without a journal, plan/apply/repeat/status, RPM signature,
`rpm -V`, and restore. Use only local read-only version/help output: `dcfldd
--help`, `ddrescue --version`, `foremost -h`, and `hexedit --help`; supply no
input or output path, device, image, or file. Compare exact RPM inventories
before and after, allowing only dependency replacements explicitly named in
the DNF transaction. The candidate profile must pass this lifecycle before
promotion. Any RIDE-managed data acquisition or image processing remains a
separate higher-risk operation with its own safety and recovery evidence.

### Batch 06J result: passed

The pinned Fedora 44 Workstation x86_64 VM passed the candidate lifecycle and
the supported-operation lifecycle on 2026-10-31. All four RPMs had signature
metadata and passed `rpm -V`; local help/version probes passed (hexedit prints
usage and returns 1). No file, image, or device was supplied. Repeat apply
reported all packages unchanged. Restore returned the exact 1,913-RPM
baseline from 1,917, with no dependency or pre-existing RPM changes. The first
supported-path attempt stopped at plan because the per-operation acceptance
records were not yet present; it created no journal and changed no packages.
After those records were added, the supported path passed. See the [06J
acceptance report](../acceptance/security-lab-forensic-media.md). All four
operations are supported for Fedora 44 Workstation x86_64 in the opt-in
forensic media profile. At that point, ten profiles mapped 43 of 137 observed
group members; 94 remained unmapped before batch 06K.

### Batch 06K: System diagnostics and performance monitoring packages

Select exact Security Lab RPM members `inxi`, `pcp-system-tools`, `powertop`,
and `sysstat`. Fedora 44 publishes all four as native RPMs. Package metadata
lists upstreams and licenses: [inxi](https://packages.fedoraproject.org/pkgs/inxi/inxi/)
is GPL-3.0-or-later, [PCP system tools](https://packages.fedoraproject.org/pkgs/pcp/pcp-system-tools/)
is GPL-2.0-or-later, [PowerTOP](https://packages.fedoraproject.org/pkgs/powertop/powertop/)
is GPL-2.0-only AND LGPL-2.1-only AND ISC, and
[sysstat](https://packages.fedoraproject.org/pkgs/sysstat/sysstat/) is
GPL-2.0-or-later. Keep the profile opt-in. The RIDE operation owns RPM
presence only. Fedora's sysstat RPM enables its `sysstat-summary.timer` when
installed; the RIDE restore disables that package-owned timer when removing
the package. The batch does not start PCP collectors or tune power settings.

Before implementation, require the pinned inventory to confirm membership.
Define acceptance as plan, candidate refusal without a journal, explicit
candidate apply, package signature metadata, `rpm -V`, installed status,
repeat apply, and restore on Fedora 44 Workstation x86_64. Run local read-only
probes `inxi --version`, `powertop --version`, and `sar -V`; for PCP, verify
the subpackage manifest and RPM integrity without invoking a collector or
enabling a service. Compare exact RPM identity before and after and record any
DNF dependency replacements. Do not run PowerTOP calibration or any command
that collects/stores monitoring data. Verify the sysstat timer's before,
installed, and restored states and confirm PCP collectors stay inactive.
Promote to supported after the complete lifecycle passes.

### Batch 06K result: passed

The candidate and supported lifecycle tests passed on the pinned Fedora 44
Workstation x86_64 VM. All four RPMs had signature metadata and passed
`rpm -V`; local `inxi --version`, `powertop --version`, and `sar -V` probes
passed, and PCP's subpackage manifest was verified. Repeat apply was
unchanged. Restore removed the selected RPMs and new dependencies. DNF
explicitly updated three existing Perl RPMs; exact inventory comparison
confirmed those updates remained after restore, with no other unexpected RPM
changes. The sysstat timer was enabled by its RPM and removed on restore;
`pmcd` and `pmlogger` remained inactive. See the [06K acceptance report](../acceptance/security-lab-system-monitoring.md).
All four operations are supported on Fedora 44 Workstation x86_64 in the
opt-in system monitoring profile. Eleven profiles now map 47 of 137 observed
group members; 90 remain unmapped.

### Batch 06L: Packet observation and traffic inspection packages

Select `iptraf-ng`, `netsniff-ng`, `ngrep`, and
`tcptrack`, after confirming all four remain exact Security Lab inventory
members. Fedora 44 publishes native RPMs: [iptraf-ng](https://packages.fedoraproject.org/pkgs/iptraf-ng/iptraf-ng/)
is GPL-2.0-or-later; [netsniff-ng](https://packages.fedoraproject.org/pkgs/netsniff-ng/netsniff-ng/)
is GPL-2.0-only; [ngrep](https://packages.fedoraproject.org/pkgs/ngrep/ngrep/)
has Fedora's `ngrep` license label; upstream describes a BSD-style license
with a regex-library-dependent GPL alternative. Record the Fedora label and
upstream terms separately. [tcptrack](https://packages.fedoraproject.org/pkgs/tcptrack/tcptrack/)
is LGPLv2+. All four can inspect live traffic when a user invokes them. v3
operations will own RPM presence only. Keep the profile opt-in and do not
start an interface, capture packets, open a pcap, or generate/replay traffic
during acceptance. The VM lifecycle should verify plan, apply, repeat,
installed status, RPM signature, `rpm -V`, and restore. Reuse the accepted
DNF package-handler evidence while recording this batch's exact dependency
updates and package scripts' service/state effects.

The four opt-in v3 package operations and
`fedora-security-lab-packet-observation` profile passed candidate and
supported acceptance. Their Fedora sources and license records are linked
above; the `ngrep` catalog preserves Fedora's `ngrep` label alongside the
upstream license note. The first supported run stopped before the package
transaction after a Fedora zchunk checksum error; inspection found no package
change, and a fresh-overlay retry passed.

### Batch 06L result: passed

The pinned Fedora 44 Workstation x86_64 VM passed candidate and supported
package lifecycles. All four signed RPMs passed `rpm -V`; all were absent in
the baseline, installed as separate single-package transactions with no
dependency changes, unchanged on repeat, and removed on restore with the
exact original RPM inventory. No interface, sniffer, capture file, or traffic
generator was used. Twelve profiles now map 51 of 137 observed group members;
86 remain unmapped. See the [06L acceptance report](../acceptance/security-lab-packet-observation.md).

### Batch 06M: Active network probing packages

Select exact Fedora Security Lab members `firewalk`, `lbd`, `masscan`, and
`zmap`. Fedora 44 publishes native RPMs and package license metadata:
[firewalk](https://packages.fedoraproject.org/pkgs/firewalk/firewalk/) is
`LicenseRef-Callaway-BSD`, [lbd](https://packages.fedoraproject.org/pkgs/lbd/lbd/)
is GPL-2.0-or-later,
[masscan](https://packages.fedoraproject.org/pkgs/masscan/masscan/) is
AGPL-3.0-only, and [zmap](https://packages.fedoraproject.org/pkgs/zmap/zmap/)
is Apache-2.0. Their commands can probe hosts and send traffic, including
Internet-scale scans. v3 owns RPM presence only; keep all four in an opt-in,
candidate-gated profile. Never run a scanner, send a packet, resolve a target,
or capture traffic during acceptance.

Completion checks are candidate refusal without a journal; plan; explicit
candidate apply on Fedora 44 Workstation x86_64; Fedora RPM signature,
`rpm -V`, and installed status for each package; repeat apply; restore; and
exact inventory recovery with any DNF-reported dependency replacement named.
Inspect package metadata for service, file-capability, or persistent-state
effects during VM acceptance. Candidate status remains until separate
authorized-scope behavior and recovery review is completed.

### Batch 06M result: passed as candidate

The pinned Fedora 44 Workstation x86_64 VM passed the candidate lifecycle.
All four signed RPMs passed `rpm -V`; all were absent at baseline, unchanged
on repeat, and removed on restore. DNF installed six dependencies and updated
four existing RPMs; exact inventory comparison showed only those explicitly
reported updates remained after restore. The RPM scriptlets were empty and
the executables had no file capabilities. ZMap's default `/etc/zmap` files
were removed on restore. No scanner or network probe was run. Keep these
operations candidate-gated pending H038. Thirteen profiles now map 55 of 137
observed group members; 82 remain unmapped. See the [06M acceptance
report](../acceptance/security-lab-network-probing.md).


### Batch 06N: Host integrity and compliance package set

The exact next five unmapped group members are `aide`, `chkrootkit`,
`openscap-scanner`, `rkhunter`, and `scap-security-guide`. Fedora 44 package
records list maintained package versions and upstream/license metadata:
[AIDE](https://packages.fedoraproject.org/pkgs/aide/aide/),
[chkrootkit](https://packages.fedoraproject.org/pkgs/chkrootkit/chkrootkit/),
[OpenSCAP](https://packages.fedoraproject.org/pkgs/openscap/openscap/),
[rkhunter](https://packages.fedoraproject.org/pkgs/rkhunter/rkhunter/), and
[SCAP Security Guide](https://packages.fedoraproject.org/pkgs/scap-security-guide/scap-security-guide/).
Use Fedora's signed RPMs and keep the five operations together in the opt-in
`fedora-security-lab-host-integrity` profile. OpenSCAP Scanner is the `oscap`
subpackage from the OpenSCAP project; SCAP Security Guide supplies policy
content and does not itself evaluate or apply a profile.

Completion checks were defined before implementation: assert exact group
membership and operation/profile mapping; refuse candidate apply without a
journal; check plan, explicit apply, package signatures, `rpm -V`, status,
repeat, and restore on Fedora 44 Workstation x86_64; inspect RPM scriptlets and
file-capability metadata; compare exact RPM inventories and report
any DNF dependency updates. Do not run any scanner, initialize an AIDE
database, evaluate or remediate a SCAP profile, refresh scanner data, or
inspect host files. Reuse the unchanged DNF package-handler checks. Keep the
operations candidate-gated and out of base profiles pending H039 review of
scan behavior, generated data, network activity, and recovery.

### Batch 06N result: passed as candidate

The pinned Fedora 44 Workstation x86_64 VM passed the declared candidate
lifecycle on 2026-10-31. All five RPM signatures and root-run `rpm -V` checks
passed; status, repeat apply, and restore passed. The exact package inventory
returned to baseline with no pre-existing package identities or versions
changed. DNF installed seven dependency package identities: `apt-libs`,
`opendbx`, `openscap`, `cronie`, `cronie-anacron`, `crontabs`, and `s-nail`.
The roughly 733 MiB installed footprint comes mainly from SCAP Security Guide.
The `cronie` RPM enabled `crond.service`, which remained inactive; restore
removed the dependency and returned the unit to baseline `not-found` / `inactive`.
No scan, database initialization, profile evaluation, or remediation ran. Keep
all five operations candidate-gated pending H039. Fourteen profiles now map
60 of 137 group members; 77 remain unmapped. See the [06N acceptance
report](../acceptance/security-lab-host-integrity.md).

### Batch 06O preflight: SNMP tools and agent package

The next four exact unmapped members are `net-snmp`, `net-snmp-utils`,
`onesixtyone`, and `snmpcheck`. Fedora identifies the first pair as the
NET-SNMP project's agent/tool and utilities; Fedora 44 package pages list
current builds and licenses for [net-snmp](https://packages.fedoraproject.org/pkgs/net-snmp/net-snmp/),
[net-snmp-utils](https://packages.fedoraproject.org/pkgs/net-snmp/net-snmp-utils/),
[onesixtyone](https://packages.fedoraproject.org/pkgs/onesixtyone/onesixtyone/),
and [snmpcheck](https://packages.fedoraproject.org/pkgs/snmpcheck/snmpcheck/).
The utilities depend on `net-snmp`; retain the explicit two-package mapping
rather than hiding that acquisition relationship. `net-snmp` also packages
`snmpd` and `snmptrapd` services, so include service-state recovery in the
candidate acceptance. `onesixtyone` is an active scanner and `snmpcheck`
queries remote SNMP agents; never run either tool during package acceptance.

Before implementation, completion checks are set: confirm all four names in
the pinned 137-member Security Lab inventory; add stable Fedora RPM operation
IDs and one opt-in profile; assert candidate refusal without a journal, plan,
explicit apply, signed RPMs, root-run `rpm -V`, status, repeat, and restore on
the pinned Fedora 44 Workstation x86_64 VM. Record `snmpd` and `snmptrapd`
enabled/active state before apply, after apply, and after restore; inspect RPM
scriptlets and file capabilities; compare exact RPM inventory and named DNF
updates. Do not run an SNMP query, scanner, daemon, trap listener, or network
workload. Keep all operations candidate-gated and out of base profiles pending
H040 review of authorized target scope, daemon ownership/configuration, and
recovery. Reuse the unchanged DNF package-handler unit checks.


### Batch 06O result: passed as candidate

The pinned Fedora 44 Workstation x86_64 VM passed the candidate lifecycle on
2026-10-31. All four RPM signatures and root-run `rpm -V` checks passed; status,
repeat apply, restore, and exact package inventory recovery passed. The four
requested RPMs were absent at baseline. DNF added 18 dependency package
identities (three for `net-snmp`; fifteen for Ruby-based `snmpcheck`, including
five weak dependencies), then removed all 18 on restore. No existing RPM
identity or version changed. After a systemd unit-cache reload, both `snmpd`
and `snmptrapd` were observed as `not-found / inactive` before, during, and
after the lifecycle; no daemon or network query ran. Although the RPM metadata
lists unit files and a post-install helper, this package operation left both
daemons inactive. Keep all four operations candidate-gated pending H040.
Fifteen profiles now map 64 of 137 group members; 73 remain unmapped. See the
[06O acceptance report](../acceptance/security-lab-snmp.md).

### Batch 06P preflight: Offline password and credential recovery tools

The next five exact unmapped members are `bkhive`, `cmospwd`, `john`,
`ophcrack`, and `pdfcrack`. Fedora 44 package records provide current package
versions, upstream project references, and licenses for [bkhive](https://packages.fedoraproject.org/pkgs/bkhive/bkhive/),
[CmosPwd](https://packages.fedoraproject.org/pkgs/cmospwd/cmospwd/),
[John the Ripper](https://packages.fedoraproject.org/pkgs/john/john/),
[Ophcrack](https://packages.fedoraproject.org/pkgs/ophcrack/ophcrack/), and
[PDFCrack](https://packages.fedoraproject.org/pkgs/pdfcrack/pdfcrack/).
These cover older Windows Syskey/SAM evidence, CMOS setup passwords, local
password auditing, and PDF password recovery; keep them available as opt-in
package operations without implying support for every legacy evidence format.

Before implementation, completion checks are set: assert these exact five
members are unmapped in the pinned Security Lab inventory; create stable
Fedora RPM operations and one opt-in profile; candidate refusal without a
journal; plan, explicit apply, signed RPMs, root-run `rpm -V`, status, repeat,
and restore on Fedora 44 Workstation x86_64. Inspect package scriptlets and
file-capability metadata; compare exact RPM inventory and report dependency
updates. Never run a password cracker, extract credentials, open a user PDF or
Windows hive, access BIOS/CMOS state, or inspect user data. Keep operations
candidate-gated pending H041 review of authorized evidence scope and private
input/output handling. Reuse unchanged DNF package-handler checks and keep the
profile out of base presets.


### Batch 06P result: passed as candidate

The pinned Fedora 44 Workstation x86_64 VM passed the candidate lifecycle on
2026-10-31. All five RPM signatures and root-run `rpm -V` checks passed; status,
repeat apply, restore, and exact package inventory recovery passed. All five
requested packages were absent at baseline, and no existing RPM identity or
version changed. DNF installed 13 Qt dependencies for Ophcrack (10 required,
3 weak) and restore removed all 13. John the Ripper is published in the Fedora
44 repository as `1.9.0-12.fc43`; its signed RPM passed verification on Fedora
44. No evidence files or hardware state were accessed, and no tool or GUI ran.
Keep all five operations candidate-gated pending H041. Sixteen profiles now
map 69 of 137 group members; 68 remain unmapped. See the [06P acceptance
report](../acceptance/security-lab-password-recovery.md).

### Batch 06Q preflight: Wireless auditing and capture tools

The next four exact unmapped members are `aircrack-ng`, `cowpatty`, `kismet`,
and `reaver`. Fedora 44 publishes these signed packages with upstream and
license metadata: [Aircrack-ng](https://packages.fedoraproject.org/pkgs/aircrack-ng/aircrack-ng/),
[Cowpatty](https://packages.fedoraproject.org/pkgs/cowpatty/cowpatty/),
[Kismet](https://packages.fedoraproject.org/pkgs/kismet/kismet/), and
[Reaver](https://packages.fedoraproject.org/pkgs/reaver/reaver/). Their tools
can passively capture WLAN traffic, inject frames, crack captured handshakes,
attack WPS PINs, or run wireless monitoring services. Keep the v3 operations
limited to package presence and expose them through one opt-in candidate
profile.

Before implementation, completion checks are set: assert these exact four
members are unmapped in the pinned Security Lab inventory; candidate refusal
without a journal; plan, explicit apply, signatures, root-run `rpm -V`, status,
repeat, and restore on Fedora 44 Workstation x86_64; inspect RPM scriptlets and
file-capability metadata; compare exact RPM inventory and dependency updates.
Observe Kismet service enablement/activity before, during, and after apply,
refreshing systemd's view but never starting it. Do not attach a wireless
adapter, change interfaces, capture traffic, inject frames, crack keys, or
run any package executable. Keep the profile out of base presets and all
operations candidate-gated pending H042 review of authorized radio scope,
privileges, service ownership, and recovery.


### Batch 06Q result: passed as candidate

The pinned Fedora 44 Workstation x86_64 VM passed the candidate lifecycle on
2026-10-31. All four RPM signatures and root-run `rpm -V` checks passed; status,
repeat apply, restore, and exact package inventory recovery passed. All four
requested packages were absent initially; DNF added nine dependencies and
restore removed all nine. No existing RPM identity or version changed. After
refreshing systemd's unit cache, `kismet.service` remained `not-found / inactive`
before, during, and after; no `kismet` system account appeared. No radio,
wireless tool, or daemon was used. Keep all four operations candidate-gated
pending H042. Seventeen profiles now map 73 of 137 group members; 64 remain
unmapped. See the [06Q acceptance report](../acceptance/security-lab-wireless.md).

### Batch 06R preflight: SIP and network load generators

The next five exact unmapped members are `siege`, `sipp`, `sipsak`, `sockperf`,
and `uperf`. Fedora 44 package pages document each upstream and license:
[Siege](https://packages.fedoraproject.org/pkgs/siege/siege/),
[SIPp](https://packages.fedoraproject.org/pkgs/sipp/sipp/),
[SIPSAK](https://packages.fedoraproject.org/pkgs/sipsak/sipsak/),
[sockperf](https://packages.fedoraproject.org/pkgs/sockperf/sockperf/), and
[uperf](https://packages.fedoraproject.org/pkgs/uperf/uperf/). These packages
generate HTTP/SIP/socket traffic when used, so v3 manages signed RPM presence
only and exposes them in one opt-in candidate profile.

Before implementation, completion checks are set: assert the exact five group
members remain unmapped; candidate refusal without a journal; plan, explicit
apply, RPM signatures, root-run `rpm -V`, status, repeat, restore, and exact
inventory recovery on Fedora 44 Workstation x86_64. Inspect package scripts
and file-capability metadata; report all DNF dependencies and any existing
package changes. Do not start a load test, send HTTP/SIP traffic, open sockets
for a benchmark, or execute these tools. Keep the profile out of base presets
and operations candidate-gated pending H043 review of authorized endpoints,
traffic limits, and service/data recovery.

The pinned Fedora 44 Workstation x86_64 VM passed the candidate lifecycle on
2026-10-31. All five RPM signatures and root-run `rpm -V` checks passed; status,
repeat apply, restore, and exact package inventory recovery passed. The packages
were absent initially. DNF installed three dependencies: `libjoedog` for Siege,
and `gsl` plus `pugixml` for SIPp. No existing RPM identity or version
changed. No traffic was generated and none of the tools was executed. Keep all
five operations candidate-gated pending H043. Eighteen profiles now map 78 of
137 group members; 59 remain unmapped. See the [06R acceptance report](../acceptance/security-lab-network-load-tools.md).

### Batch 06S preflight: network credential auditing and interception

The next focused set is the exact Security Lab membership `hydra`, `medusa`,
`ncrack`, `dsniff`, and `ettercap`. Fedora 44 provides all five signed RPMs
with published upstream and license metadata: [Hydra](https://packages.fedoraproject.org/pkgs/hydra/hydra/),
[Medusa](https://packages.fedoraproject.org/pkgs/medusa/medusa/),
[Ncrack](https://packages.fedoraproject.org/pkgs/ncrack/ncrack/),
[dsniff](https://packages.fedoraproject.org/pkgs/dsniff/dsniff/), and
[Ettercap](https://packages.fedoraproject.org/pkgs/ettercap/ettercap/).
They provide login auditing, credential capture, and interception features.
The migration manages signed Fedora RPM presence only in the opt-in candidate
profile; it does not execute any tool.

Completion checks are defined before VM acceptance: assert the exact five
group members and catalog/profile mapping; check candidate refusal without a
journal, plan, apply, RPM signature and root-run `rpm -V`, status, repeat apply,
restore, and exact package inventory recovery on Fedora 44 Workstation x86_64.
Inspect package scripts and file-capability metadata; record DNF dependencies
and any pre-existing RPM changes. Do not attempt logins, sniff, intercept,
generate traffic, or start services. Keep candidates gated pending H044 review
of authorized targets, rate limits, capture handling, and recovery.

The pinned Fedora 44 Workstation x86_64 VM passed candidate lifecycle checks
on 2026-10-31. All five signatures and root-run `rpm -V` checks passed; status,
repeat apply, restore, and the expected package identity set passed. Hydra's
transaction upgraded the image's preinstalled `expat` from 2.7.3-2.fc44 to
2.9.0-1.fc44 and installed 14 dependencies. Restore removed the five requested
packages and their newly installed dependencies; Fedora's expat update remains
because safe RPM downgrade is not available. dsniff installed `libdb` and
`libnids`; the other three required no dependencies. No other existing RPM
changed. Package scripts and file-capability metadata were inspected. No
logins were attempted and no traffic was captured or intercepted. Keep all five
operations candidate-gated pending H044. Nineteen profiles now map 83 of 137
group members; 54 remain unmapped. See the [06S acceptance report](../acceptance/security-lab-network-credential-tools.md).

### Batch 06T preflight: network activity monitoring

The next four exact unmapped members are `argus`, `nfswatch`, `nicstat`, and
`vnstat`. Fedora 44 provides each as a signed RPM; metadata records upstream
and license details for [Argus](https://packages.fedoraproject.org/pkgs/argus/argus/),
[NFSwatch](https://packages.fedoraproject.org/pkgs/nfswatch/nfswatch/),
[nicstat](https://packages.fedoraproject.org/pkgs/nicstat/nicstat/), and
[vnStat](https://packages.fedoraproject.org/pkgs/vnstat/vnstat/). These tools
monitor or record network activity. The opt-in candidate profile manages
package presence only and does not capture or analyze live traffic.

Completion checks: assert exact group membership and profile mapping; candidate
refusal without a journal; plan, apply, RPM signature and root-run `rpm -V`,
status, repeat, restore, and package identity recovery on Fedora 44 Workstation
x86_64. Inspect scriptlets, file capabilities, service state, and vnStat
account/database effects before and after the lifecycle. Record dependencies
and existing package upgrades. Do not capture traffic, start services, or run
the tools. Keep operations candidate-gated pending H045 review of authorized
interfaces, service ownership, and data recovery.

The pinned Fedora 44 Workstation x86_64 VM passed candidate lifecycle checks
on 2026-10-31. All four signatures and root-run `rpm -V` checks passed; plan,
candidate refusal, status, repeat apply, restore, and package identity recovery
passed. DNF added no dependencies and changed no pre-existing RPM. `vnstat.service`
remained `not-found / inactive`, and `/var/lib/vnstat` had no data files before,
during, or after. The vnStat RPM created system user/group `vnstat` (UID/GID 964);
that account persisted after RPM removal. No traffic was captured and no tool
or service was run. Keep all four operations candidate-gated pending H045.
Twenty profiles now map 87 of 137 group members; 50 remain unmapped. See the
[06T acceptance report](../acceptance/security-lab-network-monitoring.md).

### Batch 06U preflight: packet crafting and replay

The exact five unmapped members are `hping3`, `packETH`, `sing`, `tcpreplay`,
and `thc-ipv6`. Fedora 44 has signed RPMs with upstream and license metadata:
[hping3](https://packages.fedoraproject.org/pkgs/hping3/hping3/),
[packETH](https://packages.fedoraproject.org/pkgs/packETH/packETH/),
[sing](https://packages.fedoraproject.org/pkgs/sing/sing/),
[tcpreplay](https://packages.fedoraproject.org/pkgs/tcpreplay/tcpreplay/), and
[THC-IPv6](https://packages.fedoraproject.org/pkgs/thc-ipv6/thc-ipv6/).
hping3's upstream states it is no longer actively developed; preserve the
available Fedora package for v3.0, and consider Scapy or Nping as a v3.1
alternative. The opt-in candidate profile manages RPM presence only.

Completion checks: exact group membership and operation/profile mapping;
candidate refusal without a journal; plan, apply, RPM signatures and root-run
`rpm -V`, status, repeat, restore, and package identity recovery on Fedora 44
Workstation x86_64. Inspect scripts, file capabilities, dependencies, and
pre-existing RPM updates. Record the exact package transaction and any Fedora
weak dependencies retained after restore. Never craft or replay packets, open
a network interface, or execute these tools. Keep candidates gated pending
H046 review of authorized links, traffic bounds, and replay recovery.

The pinned Fedora 44 Workstation x86_64 VM passed candidate lifecycle checks
on 2026-10-31. All five signatures and root-run `rpm -V` checks passed; status,
repeat apply, restore, and package identity recovery passed. DNF added `tcl8`,
`gtk2`, `ibus-gtk2`, weak dependency `libcanberra-gtk2`, `libnet10`, `libdnet`,
and `libnetfilter_queue`; it changed no existing RPM. Restore removed all five
requested packages and all new dependencies except `gtk2`, `ibus-gtk2`, and
`libcanberra-gtk2`, which DNF retained as the weak-dependency closure of
packETH. The acceptance test constrains this residue to those exact three
packages. No packet was crafted or replayed, and no interface or tool was used.
Keep all five operations candidate-gated pending H046. Twenty-one profiles now
map 92 of 137 group members; 45 remain unmapped. See the [06U acceptance
report](../acceptance/security-lab-packet-generation.md).

### Batch 06V: network observation and packet analysis

The next five exact unmapped members are `etherape`, `p0f`, `pads`, `pcapdiff`,
and `ssldump`. Fedora 44 package metadata lists current RPMs, upstreams, and
licenses: [EtherApe](https://packages.fedoraproject.org/pkgs/etherape/etherape/),
[p0f](https://packages.fedoraproject.org/pkgs/p0f/p0f/),
[PADS](https://packages.fedoraproject.org/pkgs/pads/pads/),
[pcapdiff](https://packages.fedoraproject.org/pkgs/pcapdiff/pcapdiff/), and
[ssldump](https://packages.fedoraproject.org/pkgs/ssldump/ssldump/). They
observe live network traffic or analyze existing packet captures. Create one
opt-in candidate profile and keep all operations package-presence-only.

Completion checks are set before implementation: verify all five exact group
members and profile mapping; candidate refusal with no journal; plan, apply,
RPM signature and root-run `rpm -V`, status, repeat, restore, and package
inventory recovery on Fedora 44 Workstation x86_64. Inspect RPM scripts and
file capabilities; observe `pads.service` enablement and activity before,
during, and after apply; record dependencies and existing package changes.
Do not open a capture file, capture traffic, start a service, or run any tool.
Keep operations candidate-gated pending H047 review of authorized interfaces,
capture permissions, sensitive PCAP handling, and service/data recovery.

The pinned Fedora 44 Workstation x86_64 VM passed 06V candidate lifecycle
acceptance on 2026-10-31. All five RPM signatures, root-run file verification,
candidate refusal, status, repeat, and restore checks passed. DNF added `pcre`
and `python3-pcapy`, both removed as unused dependencies during restore; no
pre-existing RPM changed. PADS's systemd helpers only registered/unregistered
its unit; `pads.service` stayed not-found/inactive. No PCAP or traffic was
accessed and no tool was run. Keep all five operations candidate-gated pending
H047. Twenty-two profiles now map 97 of 137 group members; 40 remain unmapped.
See the [06V acceptance report](../acceptance/security-lab-network-observation.md).

### Batch 06W: filesystem tools and file recovery

The next four related unmapped members are `extundelete`, `hfsutils`,
`ntfs-3g`, and `ntfsprogs`. Fedora 44 packages them from Fedora's signed
repositories: [extundelete](https://packages.fedoraproject.org/pkgs/extundelete/extundelete/),
[hfsutils](https://packages.fedoraproject.org/pkgs/hfsutils/hfsutils/),
[ntfs-3g](https://packages.fedoraproject.org/pkgs/ntfs-3g/ntfs-3g/), and
[ntfsprogs](https://packages.fedoraproject.org/pkgs/ntfs-3g/ntfsprogs/).
Upstream extundelete is unmaintained and limited on modern ext4; retain the
Fedora package path for v3.0 while recording that limitation. The package
operations manage RPM presence only and do not inspect, mount, repair, recover,
or write to any filesystem. Dislocker is separated into a later encryption
batch with its own safety review.

Completion checks before implementation: verify the four exact group members
and opt-in profile mapping; candidate refusal creates no journal; plan, apply,
RPM signatures and root-run `rpm -V`, status, repeat, restore, and package
inventory recovery on Fedora 44 Workstation x86_64. Inspect package scripts,
file capabilities, services, dependencies, and changes to pre-existing RPMs.
Never attach a disk, mount a filesystem, run a recovery or repair utility, or
access user data. Keep the operations candidate-gated pending H048 review of
data-preserving use, device boundaries, and recovery expectations.

The pinned Fedora 44 Workstation x86_64 VM passed 06W candidate lifecycle
acceptance on 2026-10-31. Candidate refusal, package signatures, root-run file
verification, status, repeat, restore, and the unchanged mount table all
passed. `extundelete` and `hfsutils` were installed then removed;
`ntfs-3g` and `ntfsprogs` were already installed and remained unchanged. No
dependencies, pre-existing RPM changes, file capabilities, or package
scriptlets were found. No disk was attached, filesystem mounted, data read, or
recovery utility run. Keep all four operations candidate-gated pending H048.
Twenty-three profiles now map 101 of 137 group members; 36 remain unmapped.
See the [06W acceptance report](../acceptance/security-lab-filesystem-tools.md).

### Batch 06X preflight: BitLocker access utility

`dislocker` is isolated from the ordinary filesystem batch because it exposes
BitLocker encrypted volumes. Fedora 44 provides a signed RPM with upstream and
license metadata in its [Fedora package record](https://packages.fedoraproject.org/pkgs/dislocker/dislocker/),
and the upstream project is [Aorimn/dislocker](https://github.com/Aorimn/dislocker).
The v3 operation is package-presence-only. Acceptance will not attach or
decrypt a volume, request or expose a recovery key, create a decrypted image,
or mount data. Keep the operation candidate-gated pending H049 review of
secret handling, read-only source access, output sizing, and encrypted-volume
recovery.

Completion checks before implementation: exact group membership and opt-in
profile mapping; candidate refusal without a journal; plan, apply, RPM
signature and root-run `rpm -V`, status, repeat, restore, and package inventory
recovery on Fedora 44 Workstation x86_64. Inspect scripts, file capabilities,
dependencies, and changes to existing RPMs. Do not provide a key, attach a
volume, invoke dislocker, decrypt, or mount anything.

The pinned Fedora 44 Workstation x86_64 VM passed 06X candidate lifecycle
acceptance on 2026-10-31. Candidate refusal, RPM signature and file checks,
status, repeat, restore, and alternatives cleanup passed. DNF installed the
Dislocker RPM plus 16 dependencies (including weak dependencies); restore
removed all 17, and no pre-existing RPM changed. Fedora's package scriptlet
added and removed `/usr/bin/dislocker` as expected. No key or volume was used.
Keep the operation candidate-gated pending H049. Twenty-four profiles now map
102 of 137 group members; 35 remain unmapped. See the
[06X acceptance report](../acceptance/security-lab-dislocker.md).

### Batch 06Y: console messaging and session clients

The next four exact unmapped members are `mcabber`, `mutt`, `screen`, and
`telnet`. Fedora 44 provides signed RPMs and package metadata for
[Mcabber](https://packages.fedoraproject.org/pkgs/mcabber/mcabber/),
[Mutt](https://packages.fedoraproject.org/pkgs/mutt/mutt/),
[GNU Screen](https://packages.fedoraproject.org/pkgs/screen/screen/), and
[Telnet](https://packages.fedoraproject.org/pkgs/telnet/telnet/). Mcabber's
Fedora 44 RPM is available from the Fedora release repository and declares
GPL-2.0-or-later; its 2026 Fedora build refreshes the older upstream snapshot.
Telnet is a legacy cleartext protocol client with an archived upstream
reference. Keep both capabilities in v3.0 as opt-in package operations; do not
launch clients, connect to services, or read/write user mail, chat, or session
data. The existing `package.screen` operation is currently Server-only and
install-only; preserve the published ID while adding Workstation targeting and
the exact RPM removal state. Reuse its Server install/restore evidence and
verify the new Workstation target. H050 tracks protocol and user-data
hardening.

Completion checks before implementation: exact group membership and profile
mapping; candidate refusal without a journal; plan, apply, RPM signatures and
root-run `rpm -V`, status, repeat, restore, and package inventory recovery on
Fedora 44 Workstation x86_64. Inspect package scripts, file capabilities,
dependencies, and changes to pre-existing RPMs. Keep all four candidate-gated
and execute no client or network operation.

The pinned Fedora 44 Workstation x86_64 VM passed 06Y candidate lifecycle
acceptance on 2026-10-31. All four RPM signatures, root-run file verification,
candidate refusal, status, repeat, and restore checks passed. Mcabber added
four dependencies and Mutt added three; all seven were removed on restore. No
pre-existing RPM changed, and no RPM scripts or file capabilities were found.
No client was launched or network connection opened. `package.screen` passed
its newly declared Workstation lifecycle; its Server install/restore path is
covered by prior generic Server acceptance. Keep all four candidate-gated
pending H050. Twenty-five profiles now map 106 of 137 group members; 31 remain
unmapped. See the [06Y acceptance report](../acceptance/security-lab-console-clients.md).

### Batch 06Z preflight: web retrieval and HTTP analysis tools

The next four related unmapped members are `goaccess`, `httpd-tools`,
`httrack`, and `wget2-wget`. Fedora 44 provides signed RPMs and package
metadata for [GoAccess](https://packages.fedoraproject.org/pkgs/goaccess/goaccess/),
[httpd-tools](https://packages.fedoraproject.org/pkgs/httpd/httpd-tools/),
[HTTrack](https://packages.fedoraproject.org/pkgs/httrack/httrack/), and
[Wget2](https://packages.fedoraproject.org/pkgs/wget2/wget2/). Keep the
maintained Fedora Wget2 provider alongside existing wget1 as an explicit
alternative. GoAccess can parse private web logs, and HTTrack/Wget2 can
retrieve sites; the v3 package operations manage RPM presence only. Acceptance
must not read logs, download pages, start an HTTP server, or connect to any
site. H051 tracks private data and authorized retrieval review.

Completion checks before implementation: verify exact source group membership
and profile mapping; candidate refusal creates no journal; plan, apply, RPM
signatures and root-run `rpm -V`, status, repeat, restore, and package inventory
recovery on Fedora 44 Workstation x86_64. Inspect package scripts, file
capabilities, services, dependencies, and changes to pre-existing RPMs. Keep
all four candidate-gated and perform no log parsing, site retrieval, or network
request.

The pinned Fedora 44 Workstation x86_64 VM passed 06Z candidate lifecycle
acceptance on 2026-10-31. RPM signature and root-run file verification,
candidate refusal, status, repeat, restore, and package identity recovery
passed. GoAccess and HTTrack were installed then removed; `httpd-tools` and
`wget2-wget` were already installed and stayed unchanged. No dependencies or
pre-existing RPM changes occurred. `httpd.service` stayed not-found/inactive.
No log was read and no site accessed. Keep all four candidate-gated pending
H051. Twenty-six profiles now map 110 of 137 group members; 27 remain unmapped.
See the [06Z acceptance report](../acceptance/security-lab-web-tools.md).

### Batch 06AA preflight: data sanitization utilities

The next three unmapped members are `nwipe`, `scrub`, and `wipe`. Fedora 44
provides signed RPMs with upstream and license metadata: [nwipe](https://packages.fedoraproject.org/pkgs/nwipe/nwipe/),
[scrub](https://packages.fedoraproject.org/pkgs/scrub/scrub/), and
[wipe](https://packages.fedoraproject.org/pkgs/wipe/wipe/). These tools can
irreversibly destroy file or disk contents, so isolate them from ordinary
package batches. v3.0 operations manage RPM presence only; acceptance must not
enumerate target block devices for these tools, open files for wiping, or run
any sanitizer. H052 tracks device selection, media-type limits, authorization,
and recovery before actual sanitization behavior is offered.

Completion checks before implementation: verify the three exact source
members and isolated opt-in profile; candidate refusal creates no journal;
plan, apply, RPM signatures and root-run `rpm -V`, status, repeat, restore,
package inventory recovery, and unchanged mount table on Fedora 44 Workstation
x86_64. Inspect package scripts, file capabilities, dependencies, and changes
to existing RPMs. Do not run any tool, access user data, or attach storage.

The pinned Fedora 44 Workstation x86_64 VM passed 06AA candidate lifecycle
acceptance on 2026-10-31. Candidate refusal, RPM signatures, root-run file
verification, status, repeat, restore, and the unchanged mount table all
passed. `nwipe` and `wipe` were installed then removed; `scrub` was already
installed and stayed unchanged. Nwipe added three dependencies, all removed on
restore. No pre-existing RPM changed, and none of the requested packages had
file capabilities or RPM scripts. No device was enumerated and no sanitizer
was run. Keep all three candidate-gated pending H052. Twenty-seven profiles
now map 113 of 137 group members; 24 remain unmapped. See the
[06AA acceptance report](../acceptance/security-lab-data-sanitizers.md).

### Batch 06AB preflight: network interception and manipulation tools

The next four unmapped members are `ArpON`, `hunt`, `netsed`, and `sslsplit`.
Fedora 44 provides signed RPMs with current package records for
[ArpON](https://packages.fedoraproject.org/pkgs/ArpON/ArpON/),
[Hunt](https://packages.fedoraproject.org/pkgs/hunt/hunt/),
[NetSED](https://packages.fedoraproject.org/pkgs/netsed/netsed/), and
[SSLsplit](https://packages.fedoraproject.org/pkgs/sslsplit/sslsplit/).
Their uses include ARP attack prevention, connection takeover, live packet
modification, and TLS interception. Migrate package presence only and keep
the operations opt-in candidates. Acceptance must not attach an interface,
alter routes or firewall rules, capture or modify traffic, terminate TLS, or
run any tool. H053 tracks authorization, credential/data handling, and
network recovery before behavior is exercised.

Completion checks before implementation: verify exact source group membership
and profile mapping; candidate refusal creates no journal; plan, apply, RPM
signatures and root-run `rpm -V`, status, repeat, restore, and package
inventory recovery on Fedora 44 Workstation x86_64. Inspect package scripts,
file capabilities, services, dependencies, and changes to existing RPMs.
Observe `arpon.service` state without starting it. Keep all four
candidate-gated and perform no network operations.


The pinned Fedora 44 Workstation x86_64 VM passed 06AB candidate lifecycle
acceptance on 2026-10-31. Candidate refusal, plan, signature and file checks,
status, repeat, restore, package inventory recovery, and inactive
`arpon.service` all passed. All four requested RPMs were initially absent;
restore removed them and the one added dependency (`libdnet`). None had file
capabilities or RPM scriptlets. No pre-existing RPM changed, and no network
tool or behavior was exercised. Twenty-eight opt-in profiles map 117 of 137
observed Security Lab members; 20 remain unmapped. H053 tracks authorized
network behavior and recovery. See the [06AB acceptance report](../acceptance/security-lab-network-interception.md).


### Batch 06AC preflight: security and network diagnostics

The four selected unmapped Fedora Security Lab members are `flawfinder`,
`sslscan`, `subnetcalc`, and `swaks`. Fedora 44 has repository records for
[Flawfinder](https://packages.fedoraproject.org/pkgs/flawfinder/flawfinder/),
[SSLScan](https://packages.fedoraproject.org/pkgs/sslscan/sslscan/),
[SubNetCalc](https://packages.fedoraproject.org/pkgs/subnetcalc/subnetcalc/),
and [Swaks](https://packages.fedoraproject.org/pkgs/swaks/swaks/). Flawfinder
scans C/C++ sources; SSLScan probes TLS services; SubNetCalc calculates
addresses locally; Swaks performs SMTP transactions. Keep all four operations
opt-in candidates and manage signed RPM presence only.

Completion checks before implementation: confirm the exact four source-group
entries and profile mapping; confirm candidate refusal creates no journal; on
the disposable Fedora 44 Workstation x86_64 VM, plan, apply, verify repository
signatures and root-run `rpm -V`, query status, repeat, restore, and verify
package inventory recovery. Inspect RPM scripts, file capabilities, dependencies,
changes to existing RPMs, and service activation. Do not scan local source,
contact TLS or SMTP endpoints, send mail, or run the tools. H054 will track
authorized destinations, source-data handling, SMTP side effects, and output
retention before behavioral use.


The pinned Fedora 44 Workstation x86_64 VM passed 06AC candidate lifecycle
acceptance on 2026-10-31. All four RPMs installed and restored with all 15 new
dependencies removed; no existing RPM changed. Signature and file checks,
repeat, status, and exact package inventory recovery passed. The packages had
no file capabilities, scriptlets, or service units. No source scan, network
connection, or SMTP transaction occurred. The first test attempt exposed a
noisy whole-VM service-state assertion; investigation showed unrelated
transient VM services, so the test was narrowed to package-owned units and
passed on a fresh overlay. DNF logged recoverable HTTP 500 responses from one
mirror but completed the verified transactions. H054 tracks behavior and data
handling review. Twenty-eight profiles now map 121 of 137 Security Lab
packages; 16 remain unmapped. See the
[06AC acceptance report](../acceptance/security-lab-network-diagnostics-2.md).


### Batch 06AD preflight: GParted storage application

The next unmapped storage outcome is `gparted`. Fedora 44 publishes signed
`gparted` 1.7.0-3, licensed GPL-2.0-or-later; the upstream project is active
and currently lists 1.8.1. Use Fedora's native RPM for the v3.0 Workstation
path. Keep it in a separate opt-in profile and candidate-gated.
[Fedora package record](https://packages.fedoraproject.org/pkgs/gparted/gparted/)
[Upstream project and license](https://gparted.org/)

Completion checks before implementation: confirm exactly one unmapped inventory
entry and isolated profile membership; candidate refusal must leave no journal;
on disposable Fedora 44 Workstation x86_64, plan, apply, verify RPM signature
and root-run `rpm -V`, query status, repeat, restore, and compare package
inventory and mount table. Inspect RPM scripts, file capabilities, service
units, dependencies, and existing RPM changes. Never launch GParted, enumerate
block devices, invoke partition tools, or change storage. H055 tracks explicit
device authorization, backups, filesystem constraints, and recovery before
any partition behavior is managed.


The pinned Fedora 44 Workstation x86_64 VM passed 06AD candidate lifecycle
acceptance on 2026-10-31. GParted 1.7.0-3.fc44 installed, repeated unchanged,
and restored with no dependency or pre-existing RPM changes. Signature and
file checks passed; no scripts, capabilities, or service units were present.
The mount table remained unchanged. GParted was never launched and no block
devices or partition tools were touched. Thirty profiles map 122 of 137
Security Lab group members; 15 remain unmapped. H055 tracks storage safety,
recovery, and review of the Fedora package against current upstream. See the
[06AD acceptance report](../acceptance/package.gparted.md).


### Batch 06AE preflight: AFF forensic image utilities

The next unmapped forensic member is `afftools`, Fedora's utilities subpackage
of AFFLIB. Fedora 44 publishes signed `afftools` 3.7.22-4.fc44 with
`LicenseRef-Callaway-BSD-with-advertising`; upstream AFFLIBv3 remains active.
Use the Fedora RPM and keep it in an isolated opt-in candidate profile.
[Fedora package record](https://packages.fedoraproject.org/pkgs/afflib/afftools/)
[Upstream AFFLIBv3](https://github.com/sshock/AFFLIBv3)

Completion checks before implementation: confirm exactly one unmapped inventory
entry and isolated profile mapping; candidate refusal must leave no journal;
on disposable Fedora 44 Workstation x86_64, plan, apply, verify RPM signature
and root-run `rpm -V`, query status, repeat, restore, and compare package
inventory and mount table. Inspect RPM scripts, file capabilities, service
units, dependencies, and changes to existing RPMs. Never open, convert, mount,
hash, or otherwise process an evidence image; do not enumerate devices. H056
tracks evidence provenance, read-only handling, cryptographic material, and
recovery before any AFF behavior is managed.


The pinned Fedora 44 Workstation x86_64 VM passed 06AE candidate lifecycle
acceptance on 2026-10-31. `afftools` 3.7.22-4.fc44 and its `afflib` dependency
installed, repeated unchanged, and restored. No pre-existing RPM changed. RPM
signature and file checks passed; no capabilities, scriptlets, or service units
were present. Package inventory and mount table recovered exactly. No AFF tool
was run and no evidence image was accessed. Thirty-one opt-in profiles map 123
of 137 Security Lab members; 14 remain unmapped. H056 tracks provenance and
recovery before behavior is managed. See the
[06AE acceptance report](../acceptance/package.afftools.md).


### Batch 06AF preflight: proxy routing and packet construction tools

The exact two package-only outcomes are `proxychains-ng` and `python3-scapy`.
Fedora 44 publishes signed `proxychains-ng` 4.17-9.fc44 (GPL-2.0-or-later)
and Scapy 2.7.0-3.fc44 (GPL-2.0-only). ProxyChains-NG is an active
continuation of the abandoned ProxyChains project and redirects TCP calls from
dynamically linked programs through configured proxies. Scapy is an active
packet manipulation program and Python library. Fedora's package source is
used for both; no third-party repositories or downloads are needed.
[Fedora ProxyChains-NG package](https://packages.fedoraproject.org/pkgs/proxychains-ng/proxychains-ng/)
[ProxyChains-NG upstream](https://github.com/rofl0r/proxychains-ng)
[Fedora Scapy package](https://packages.fedoraproject.org/pkgs/scapy/python3-scapy/)
[Scapy upstream and license](https://github.com/secdev/scapy)

Keep these closely related network manipulation packages together in an
isolated opt-in candidate profile. Their candidate operation is package
presence only. Completion checks before implementation: confirm exactly two
unmapped inventory entries and exact isolated profile membership; candidate
refusal creates no journal; on Fedora 44 Workstation x86_64, plan, apply,
verify RPM signatures and root-run `rpm -V`, query status, repeat, restore,
and compare package inventory. Inspect dependency changes, updates to
pre-existing RPMs, RPM scriptlets, file capabilities, and service units.
Do not launch ProxyChains-NG or Scapy, load a proxy configuration, connect to
a proxy, open a network interface, capture or craft packets, or send traffic.
H046 retains Scapy packet-scope and recovery controls; H057 tracks proxy
configuration, endpoint authorization, and routing recovery before any
ProxyChains behavior is managed.

The pinned Fedora 44 Workstation x86_64 VM passed the 06AF package lifecycle
on 2026-11-01. Candidate refusal created no journal; apply and repeat passed;
both signed RPMs passed root-run `rpm -V`; status, restore, and requested
package recovery passed. Scapy's Fedora DNF transaction installed 357 packages
including Scapy, and the combined profile added 358 RPMs including
ProxyChains-NG. Restore removed 355 packages in the Scapy transaction and
removed ProxyChains-NG separately. The exact remaining DNF dependencies were
`python3-tkinter` and `tk`; no pre-existing RPM changed. Neither RPM had
capabilities, scriptlets, or systemd units. No proxy configuration, endpoint,
network interface, or packet behavior was touched. The first inventory check
found the two package remnants; transaction review led to an exact-residue
assertion and a passing fresh-overlay rerun. H058 tracks dependency ownership
and cleanup. Thirty-two opt-in profiles map 125 of 137 group members; 12
remain unmapped. See the [06AF acceptance report](../acceptance/security-lab-network-path-tools.md).


### Batch 06AG preflight: Security Lab menu and SELinux policy GUI

The exact next two unmapped members are `security-menus` and `setools-gui`.
Fedora 44 provides `security-menus` 38-8.fc44 (GPL-2.0-only), which adds a
Security Lab menu category, and `setools-gui` 4.6.0-6.fc44 (GPL-2.0-only), the
SETools graphical SELinux policy analysis package. The former's Fedora-listed
Pagure source is now a read-only archive, while Fedora still builds and ships
the package; the latter remains actively maintained in the SELinuxProject
repository and has a Fedora 44 rebuild against current SELinux userspace. Use
the Fedora RPMs for v3.0 and preserve both as candidate opt-in operations.
`security-menus` declares `redhat-menus` and `xfce4-terminal` dependencies;
`setools-gui` declares Python 3.14, PyQt6, and SETools runtime dependencies.
Record the actual DNF closure and recovery residue in acceptance evidence.
[Fedora security-menus package](https://packages.fedoraproject.org/pkgs/security-menus/security-menus/)
[Fedora Security Lab](https://fedoraproject.org/labs/security/)
[Fedora SETools GUI package](https://packages.fedoraproject.org/pkgs/setools/setools-gui/)
[SETools upstream](https://github.com/SELinuxProject/setools)

Completion checks before implementation: confirm exactly these two unmapped
inventory entries and exact isolated profile membership; candidate refusal
creates no journal; on Fedora 44 Workstation x86_64, plan, apply, verify RPM
signatures and root-run `rpm -V`, query status, repeat, restore, and compare
package inventory. Inspect dependencies, changes to pre-existing RPMs, file
capabilities, scriptlets, package-owned menu or desktop files, and systemd
units. Do not launch the menu or Apol, query or alter the host SELinux policy,
or inspect a user's policy data. H059 tracks later menu visibility, application
launch, and read-only policy-fixture review; broader visual checks can remain
in v3.1 while both RPMs stay opt-in candidates.

The Fedora 44 Workstation x86_64 VM passed the 06AG package lifecycle on
2026-11-01. Candidate refusal created no journal; both operations applied,
repeated unchanged, passed signed-RPM and root-run `rpm -V` checks, and
restored. The owned files included `security-lab.menu`, its category
directories, launcher files, and `/usr/bin/apol`; neither package had
capabilities, scriptlets, or systemd units. The DNF transactions installed 8
and 29 packages and updated 11 pre-existing Qt/GStreamer RPMs; restore removed
new packages but did not roll back those updates. No extra package remained.
No menu, launcher, or Apol application was opened and no SELinux policy was
read or changed. The menu package provides launchers for the full Security Lab
collection, including absent applications, so both operations stay
candidate-gated pending H059 review. Thirty-four opt-in profiles now map 127
of 137 group members; 10 remain unmapped. See the
[06AG acceptance report](../acceptance/security-lab-security-desktop-tools.md).


### Batch 06AH preflight: process and host visibility tools

The next two unmapped Security Lab members selected for 06AH are `scanmem`
and `unhide`. Fedora 44 publishes `scanmem` 0.17-23.fc44.1 under GPL-3.0-or-
later AND LGPL-3.0-or-later and `unhide` 20240510-3.fc44 under GPL-3.0-or-later
AND MIT. Both have Fedora repository sources and current Fedora 44 builds.
`scanmem` inspects and can modify an executing process's memory; `unhide`
searches process and TCP/UDP visibility for rootkit-like hiding. v3.0 will
manage the signed RPMs only. `rats` is kept visible for a separate source
review: Fedora's package landing page currently lists only Fedora 39-41 even
though Fedora 44 mirror metadata advertises an RPM, and the tool's source
location is a legacy Google Code project. This is an unresolved acquisition
path, not a retirement decision.
[Fedora scanmem](https://packages.fedoraproject.org/pkgs/scanmem/scanmem/)
[scanmem upstream](https://github.com/scanmem/scanmem)
[Fedora unhide](https://packages.fedoraproject.org/pkgs/unhide/unhide/)
[Fedora rats](https://packages.fedoraproject.org/pkgs/rats/rats/)

Completion checks before implementation: confirm only `scanmem` and `unhide`
are moved out of `unmapped`, create an isolated opt-in profile containing both
IDs, and keep both operations as Fedora 44 Workstation x86_64 candidates. In
the pinned disposable VM, check candidate refusal, absent plan, apply, signed
RPM verification, root-run `rpm -V`, executable presence, status, unchanged
repeat, restore, explicit absent state, and exact RPM inventory. Inspect each
RPM's dependency closure, scriptlets, capabilities, services, and pre-existing
package updates. Do not attach to or read/write any process memory, run
rootkit/port scans, change system security state, or inspect user data. Reuse
the established unchanged DNF handler tests. Record dependency changes and
remain candidate-gated; behavioral safety review can move to v3.1.

Windows alignment for 06AH: no shared lifecycle, catalog, profile, or journal
contract changes. These are Fedora-specific package operations; Windows has
no matching Linux RPM provider. Revisit if either product is offered on
Windows or the shared package source contract changes.

The Fedora 44 Workstation x86_64 VM passed the 06AH package-only lifecycle on
2026-11-01. Candidate refusal created no journal; both RPMs applied, repeated
unchanged, passed signed-RPM and `rpm -V` checks, and restored to the exact
baseline. `scanmem` installed `scanmem-libs`, which restore removed; `unhide`
had no dependencies. Neither package had scriptlets, capabilities, or service
units. No scanner was run. H060 tracks later behavior review. Thirty-five
opt-in profiles now map 129 of 137 group members; eight remain unmapped. See
the [06AH acceptance report](../acceptance/security-lab-process-inspection.md).


### Batch 06AI preflight: default editor package

The next unmapped member selected is `default-editor`. Fedora describes that
name as a metapackage for a DNF group; the current concrete Fedora 44
implementation is `nano-default-editor` 8.7.1-2.fc44, GPL-3.0-or-later, which
depends on `nano` and owns shell startup files that set `EDITOR` to nano when
the user has not already selected an editor. Migrate the capability as
`package.nano-default-editor`; preserve the existing standalone `package.nano`
operation without changing its meaning. Keep the new operation opt-in because
it sets a user-visible system default.
[Fedora nano-default-editor](https://packages.fedoraproject.org/pkgs/nano/nano-default-editor/)
[Fedora's default editor change](https://fedoraproject.org/wiki/Changes/UseNanoByDefault)

Completion checks before implementation: verify that only the `default-editor`
inventory member is mapped and the new profile contains exactly the new
candidate operation. In a disposable Fedora 44 Workstation x86_64 VM, create
an absent baseline by removing only the known `nano`, `nano-default-editor`,
and `default-editor` packages; reject any other removal. Exercise candidate
refusal, plan, apply, signatures, `rpm -V`, status, repeat, restore, and explicit
remove. Confirm the owned shell startup files set `EDITOR=/usr/bin/nano` only when the
caller has not set `EDITOR`, and verify package recovery returns the RPM
inventory to the prepared baseline. Inspect dependencies, scriptlets,
capabilities, and service units. No visual/manual session is required.

Windows alignment for 06AI: no shared contract change; this operation uses a
Fedora-owned RPM and shell startup files. Windows default-editor handling is
platform-specific and is outside this Linux package operation.

The Fedora 44 Workstation x86_64 VM passed the 06AI package and Bash
environment lifecycle on 2026-11-01. Candidate refusal created no journal;
preparation removed exactly the three known editor RPMs. Apply installed
`nano` and `nano-default-editor`; Bash selected `/usr/bin/nano` only when
`EDITOR` was unset and preserved an explicit `EDITOR=vi`. Restore and explicit
remove returned the package inventory to the prepared baseline. The RPM had
no scriptlets, file capabilities, or systemd units. CSH/fish runtime behavior
remains under H061. The first run revealed only a mistaken expected string;
after investigating the observed `/usr/bin/nano` value, the corrected check
passed on a fresh overlay. Thirty-six opt-in profiles now map 130 of 137
group members; seven remain unmapped. See the
[06AI acceptance report](../acceptance/security-lab-default-editor.md).

### Batch 06AJ preflight: Nebula package presence

The next unmapped member selected is `nebula`. Fedora 44 provides the
maintained `nebula` 1.11.2-1.fc44 RPM under Fedora repository signatures; its
license expression is Apache-2.0 AND BSD-2-Clause-Views AND BSD-3-Clause AND
GPL-2.0-only AND ISC AND MIT AND Zlib. The RPM ships the Nebula binaries, a
sample `/etc/nebula/config.yml`, and a systemd unit. v3.0 will manage RPM
presence only as an opt-in candidate. It will not create certificates or
configuration, start or enable the service, add interfaces or routes, or join
an overlay network.
[Fedora Nebula package](https://packages.fedoraproject.org/pkgs/nebula/nebula/)
[Nebula upstream](https://github.com/slackhq/nebula)

Completion checks before implementation: map only the `nebula` inventory
member into a one-operation opt-in profile and declare a Fedora 44 Workstation
x86_64 candidate. In the pinned disposable VM, verify candidate refusal,
absent plan, apply, repository signature, `rpm -V`, executable and sample
configuration presence, service remains inactive and disabled, status,
unchanged repeat, restore, explicit install/remove, and exact RPM inventory
recovery. Inspect dependency changes, RPM scriptlets, file capabilities, and
unit ownership. Do not execute Nebula or its certificate/service tools, create
certificates or configuration, inspect endpoints, or change network state.
Reuse the established DNF handler tests. Record overlay networking, config and
certificate ownership, and service recovery as H062 for v3.1.

Windows alignment for 06AJ: no shared lifecycle, profile, journal, or package
source contract change. This operation uses Fedora's signed RPM provider and
systemd packaging; Windows tunnel support remains platform-specific. Revisit
if Nebula becomes a shared product contract or a Windows operation is added.


### Batch 06AJ result: Nebula package presence

The Fedora 44 Workstation x86_64 VM passed the 06AJ package-only lifecycle on
2026-11-01. Candidate refusal created no journal. Apply installed only the
signed `nebula` 1.11.2-1.fc44 RPM with no dependency changes or pre-existing
RPM updates. `rpm -V`, signature verification, executable/config presence,
status, unchanged repeat, restore, explicit install/remove, and exact RPM
inventory recovery passed. Fedora's RPM scriptlets register the systemd unit
through the systemd update helper; the service remained inactive and disabled.
The RPM sets no file capabilities. Nebula and certificate utilities were not
run; no configuration, certificate, interface, route, or overlay connection
was created. H062 tracks later configuration and service recovery. Thirty-seven
opt-in profiles now map 131 of 137 group members; six remain unmapped. See the
[06AJ acceptance report](../acceptance/security-lab-nebula.md).

### Batch 06AK preflight: NTPsec package presence

The next unmapped member selected is `ntpsec`. Fedora 44 publishes the
maintained NTPsec 1.2.6-1.fc44 package. Fedora records the license expression
as NTP AND BSD-2-Clause AND BSD-3-Clause AND BSD-4-Clause AND ISC AND
Apache-2.0 AND Beerware. The RPM includes a time daemon, configuration,
multiple systemd units/timers, and a sysusers definition. Since Fedora
Workstation normally uses chrony, installing an NTP daemon can affect the host
clock service even if RIDE never edits configuration. v3.0 will expose package
presence only as an opt-in candidate; it will not start/enable NTPsec, edit
clock sources, synchronize time, or change firewall/network state.
[Fedora NTPsec package](https://packages.fedoraproject.org/pkgs/ntpsec/ntpsec/)
[NTPsec upstream](https://ntpsec.org/)
[NTPsec source and releases](https://ntpsec.org/downloads.html)
[Fedora time-service replacement notes](https://fedoraproject.org/wiki/Changes/NtpReplacement)

Completion checks before implementation: map only the `ntpsec` inventory
member to a one-operation opt-in candidate profile on Fedora 44 Workstation
x86_64. In the pinned disposable VM, verify candidate refusal, absent plan,
apply, Fedora signature, `rpm -V`, binary/config presence, `ntpd.service`
remains inactive and disabled, existing `chronyd` package/service state is
preserved, status, unchanged repeat, restore, explicit install/remove, and
exact RPM inventory recovery. Record package additions and removals, RPM
scriptlets, capabilities, systemd unit/timer ownership, and whether the `ntp`
sysuser remains after package removal. Do not run NTPsec utilities or daemon,
query peers, edit configuration, contact time servers, or change the clock.
If Fedora enables/starts NTPsec, displaces chrony, or changes clock/network
state, stop and investigate before retrying. Track service configuration, user
ownership, and clock recovery as H063 for v3.1.

Windows alignment for 06AK: no shared lifecycle, profile, journal, or source
contract changes. This package uses Fedora's RPM and systemd service model;
Windows time synchronization remains platform-specific. Revisit if the
operation expands into shared clock configuration or a Windows daemon package.


### Batch 06AK result: NTPsec package presence

The Fedora 44 Workstation x86_64 VM passed the 06AK package-only lifecycle on
2026-11-01. Candidate refusal created no journal. Apply installed only signed
`ntpsec` 1.2.6-1.fc44, with no dependency changes or pre-existing RPM updates.
Signature and `rpm -V` passed. `ntpd.service` remained inactive and disabled,
while existing chronyd remained active and enabled. Apply/restore, status,
repeat, explicit install/remove, and exact RPM inventory recovery passed.
Fedora's RPM hooks register systemd units; the `ntp` sysuser/group were created
and persisted after package removal as a nologin account with home
`/var/lib/ntp`. No daemon, utility, peer, time source, or clock behavior was
run. H063 tracks sysuser, service, configuration, network, and clock recovery.
Thirty-eight opt-in profiles now map 132 of 137 group members; five remain
unmapped. See the [06AK acceptance report](../acceptance/security-lab-ntpsec.md).

### Batch 06AL preflight: OpenSSH core package mapping

The next unmapped member is `openssh`. Fedora documents this as the shared
core package for both OpenSSH client and server; the core package is useful
when one of those subpackages is installed. The repository already has the
supported `package.openssh-clients` operation with Fedora 44 Workstation and
Server VM evidence. The workstation and server baselines already select that
client operation. Map the legacy Security Lab core-package outcome to this
existing operation and profile, recording the client-tool expansion explicitly.
Do not add a duplicate package operation or imply that the mapping installs or
configures an SSH server.
[Fedora OpenSSH core package](https://packages.fedoraproject.org/pkgs/openssh/openssh/)
[Fedora OpenSSH subpackages](https://packages.fedoraproject.org/pkgs/openssh/)
[Verified client operation](../acceptance/package.openssh-clients.md)

Completion checks before implementation: only `openssh` moves from unmapped;
its inventory mapping records `v3PackageName: openssh-clients` and
`package.openssh-clients`; a single-operation Security Lab profile matches
that mapping; the existing operation remains supported and unchanged. Reuse
the exact Fedora 44 Workstation and Server lifecycle evidence, including its
package inventory, signed RPM verification, client executable, and active SSH
server checks. Run the catalog/profile/migration consistency checks. Do not
repeat VM acceptance because the handler, operation contract, and tested targets
are unchanged. Windows alignment remains the existing Linux recovery-limit
record; no Windows SSH operation or shared contract change is proposed.


### Batch 06AL result: OpenSSH core package mapping

The legacy `openssh` member now maps to the existing supported
`package.openssh-clients` operation and a one-operation opt-in profile. Fedora
44 Workstation and Server acceptance evidence was reused because the operation,
handler, contract, and declared targets are unchanged. This mapping supplies
client tools through Fedora's shared OpenSSH core dependency; it does not
configure an SSH server. Thirty-nine opt-in profiles now map 133 of 137 group
members; four remain unmapped. See the
[06AL mapping report](../acceptance/security-lab-openssh-core.md).

### Batch 06AM preflight: PSAD package presence

The next unmapped member selected is `psad`. Fedora 44 ships PSAD 2.4.6-24.fc44
under Fedora signatures, GPL-2.0-or-later. PSAD is a privileged port-scan
alert daemon that consumes firewall logs and can automatically add blocking
rules. The Fedora RPM includes configuration, signatures/rules, logs and state
directories, and `psad.service`. v3.0 will manage package presence only as an
opt-in candidate; no service activation, firewall rule, log scan, alert, or
configuration change is in scope.
[Fedora PSAD package](https://packages.fedoraproject.org/pkgs/psad/psad/)
[PSAD upstream](https://www.cipherdyne.org/psad/)

Completion checks before implementation: map only `psad` to a one-operation
Fedora 44 Workstation x86_64 candidate profile. In the pinned disposable VM,
verify candidate refusal, absent plan, apply, signature, `rpm -V`, executable
and default config presence, `psad.service` remains inactive/disabled, exact
nftables ruleset is unchanged, status, unchanged repeat, restore, explicit
install/remove, and exact package inventory recovery. Record DNF additions and
removals, scriptlets, file capabilities, service state, and any psad user or
state directories that persist after removal. Do not run PSAD, read firewall
logs, send packets, generate alerts, or add/remove firewall rules. Track
configuration, firewall ownership, and alert/block recovery as H064 for v3.1.

Windows alignment for 06AM: no shared lifecycle, profile, journal, or package
contract changes. The Fedora RPM and Linux firewall integration are
platform-specific; revisit only if this becomes a shared threat-detection
contract or Windows gains an equivalent operation.


### Batch 06AM result: PSAD package presence

The Fedora 44 Workstation x86_64 VM passed the 06AM package-only lifecycle on
2026-11-01. Candidate refusal created no journal. Apply installed signed PSAD
2.4.6-24.fc44 plus 14 dependency/weak-dependency RPMs; restore removed exactly
those 15 packages with no pre-existing RPM changes. Signature and `rpm -V`
passed; the service remained inactive and disabled, and the nftables ruleset
was unchanged throughout. No PSAD user/group or file capabilities were added.
No daemon, log, packet, alert, or firewall-rule behavior was exercised. H064
tracks later configuration and firewall recovery. Forty opt-in profiles now
map 134 of 137 group members; three remain unmapped. See the
[06AM acceptance report](../acceptance/security-lab-psad.md).

### Batch 06AN preflight: RATS source-audit tool

The next unmapped member selected is `rats`, the Rough Auditing Tool for
Security. Fedora's package index is stale and lists only older releases, but
Fedora 44's official release repository contains the signed `rats` 2.4-31.fc44
x86_64 RPM. The upstream is an old Google Code export with no current release
activity, so preserve the legacy package as an opt-in candidate and document
Flawfinder as the maintained Fedora alternative for C/C++ only. Flawfinder is
not a full replacement for RATS' C/C++, Perl, PHP, Python, and Ruby scanners.
[RATS Fedora package record](https://packages.fedoraproject.org/pkgs/rats/rats/)
[Fedora 44 RATS RPM](https://download.fedoraproject.org/pub/fedora/linux/releases/44/Everything/x86_64/os/Packages/r/rats-2.4-31.fc44.x86_64.rpm)
[RATS upstream archive](https://github.com/stgnet/rats)
[Fedora Flawfinder package](https://packages.fedoraproject.org/pkgs/flawfinder/flawfinder/)

Completion checks before implementation: only `rats` moves from unmapped and
an isolated profile contains only `package.rats`. Confirm the Fedora 44 RPM
version, signed repository source, executable/database presence, dependencies,
scriptlets, capabilities, and exact package lifecycle on Fedora 44 Workstation
x86_64. Verify refusal, plan, apply, signature, `rpm -V`, status, repeat,
restore, explicit remove, and exact package inventory recovery. Do not scan
source code or execute the old vulnerability database. Keep Flawfinder as a
separate existing operation and document its narrower C/C++ scope. H065 tracks
future upstream vitality and comparison with a broader maintained multi-
language analyzer.

Windows alignment for 06AN: no shared lifecycle or package contract change.
The Fedora RPM is platform-specific; the old upstream repository has a
Windows README but no current release path, and no Windows operation is added.


### Batch 06AN result: RATS source-audit tool

The Fedora 44 Workstation x86_64 VM passed the 06AN package-only lifecycle on
2026-11-01. Candidate refusal created no journal. Apply installed only the
signed `rats` 2.4-31.fc44 RPM; there were no dependencies, scriptlets, systemd
units, or file capabilities. The executable and bundled C, OpenSSL, Perl, PHP,
Python, and Ruby XML databases were present. Signature and `rpm -V` passed;
repeat, restore, explicit install/remove, and exact inventory recovery passed.
No source scan was run. The upstream remains an old export; H065 tracks a
maintained multi-language alternative. Forty-one opt-in profiles now map 135
of 137 group members; two remain unmapped. See the
[06AN acceptance report](../acceptance/security-lab-rats.md).

### Batch 06AO result: Tripwire package presence

The next unmapped member selected is `tripwire`. Fedora 44 ships Open Source
Tripwire 2.4.3.7-21.fc44, GPL-2.0-or-later. Upstream's latest tagged source is
old, while Fedora continues to ship a signed package. Tripwire's value depends
on securely generated keys, a reviewed policy, and a clean initial baseline;
the RPM also provides a daily check script. v3.0 will expose package presence
only as an opt-in candidate and will not initialize or use those assets.
[Fedora Tripwire package](https://packages.fedoraproject.org/pkgs/tripwire/tripwire/)
[Tripwire upstream](https://github.com/Tripwire/tripwire-open-source/)
[Tripwire releases](https://github.com/Tripwire/tripwire-open-source/releases)

Completion checks before implementation: map only `tripwire` to an isolated
Fedora 44 Workstation x86_64 candidate profile. In the pinned disposable VM,
verify refusal, plan, apply, Fedora signature, `rpm -V`, executable and default
configuration presence, absence of generated private keys and an initialized
integrity database, status, unchanged repeat, restore, explicit remove, and
exact package inventory recovery. Inspect scriptlets, file capabilities,
cron/systemd activation, and generated files. Do not generate keys, sign or
initialize policy, build a baseline, execute the daily check, scan the
filesystem, or create reports. The first pilot stopped at `rpm -V`; Fedora's
RPM database confirms its post-install script intentionally substitutes the
system hostname for `localhost` in `twpol.txt`. The installed RPM contained no
key files or `.twd` baseline. Acceptance now checks this exact expected config
change. The corrected full lifecycle then passed on Fedora 44 Workstation
x86_64. The signed RPM transaction installed only Tripwire, refusal/plan,
repeat, restore, explicit install/remove, and exact RPM inventory recovery
passed. The RPM had no file capabilities or systemd units. Its daily script
does not scan without an initialized host database; no keys, `.twd` baseline,
or reports were created. RPM removal deliberately preserves the hostname-
specific sample policy as `/etc/tripwire/twpol.txt.rpmsave`; acceptance checks
that it contains only the expected hostname and remains unowned. This
documented config residue is part of the opt-in candidate's recovery contract.
H066 tracks key/policy ownership, clean baseline generation, scheduled scan
scope, and database/report recovery for v3.1.

Evidence: Fedora 44 Workstation x86_64, 2026-11-01, apply
`20261101T130008Z-2567-28474`, repeat `20261101T130021Z-3740-30519`, restore
`20261101T130022Z-4178-21261`, explicit install
`20261101T130026Z-5014-31011`, and remove `20261101T130029Z-5291-17346`.
Transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06ao-verified/fedora-44-workstation-x86_64/20261101T125939Z-test-package-apply-repeat-status-restore-and-remove-69bfa7b3/transcript.jsonl`
(SHA-256 `432eb5613b45126f39716642445080c0302140c9884c39dd0fd47064cbd7eccb`).
Forty-two opt-in profiles map 136 of 137 observed Security Lab group members;
one remains unmapped.

### Batch 06AP preflight: USB capture and replay tools

The last unmapped Fedora Security Lab member is `usbsniff`. Fedora 44 ships
`0-26.20170624gitb4ba3c8.fc44` from the GPL-3.0-or-later upstream
[vdudouyt/usbsniff](https://github.com/vdudouyt/usbsniff); Fedora describes it
as USB traffic capture and replay tooling
([Fedora package](https://packages.fedoraproject.org/pkgs/usbsniff/usbsniff/)).
The source is old but the package is still present in the Fedora 44 release.
Its `usb_replay` detaches the kernel driver and may interrupt the attached
device until it is reconnected. v3.0 will expose only opt-in RPM presence;
capture, replay, detach, reset, and USB hardware behavior stay outside the
operation and profile.

Completion checks defined before implementation: map only `usbsniff` to one isolated
Fedora 44 Workstation x86_64 candidate profile. In the pinned disposable VM,
verify candidate refusal, plan, signed Fedora RPM apply, `rpm -V`, presence of
the four packaged commands, status, unchanged repeat, restore, explicit
install/remove, and exact RPM inventory recovery. Inspect scriptlets, file
capabilities, units, package dependencies, and residual files. Do not connect
or operate USB hardware, invoke capture/replay/detach/reset, load `usbmon`, or
read host USB data. Then update the Security Lab inventory, progress report,
burndown, generated operation docs, and Windows alignment. There is no
shared Windows USB capture contract; record the Linux-only package boundary.

### Batch 06AP result: USB capture/replay package presence

The pinned Fedora 44 Workstation x86_64 lifecycle passed on 2026-11-01.
Candidate refusal did not create a run journal. Apply installed only the
signed `usbsniff` RPM (`0-26.20170624gitb4ba3c8.fc44`); all four executables
were present and `rpm -V` passed. The RPM had no scriptlets, file capabilities,
or systemd units. Repeat was unchanged; restore and explicit remove both
returned the exact RPM inventory to baseline. No USB device was connected or
operated, and none of the four commands was invoked. The operation remains an
opt-in candidate because the package is old and device-level capture/replay
behavior was intentionally outside this migration acceptance.

Evidence: apply `20261101T140757Z-2572-11324`, repeat
`20261101T140809Z-3593-18052`, restore `20261101T140810Z-4029-10309`, explicit
install `20261101T140813Z-4633-13494`, and remove
`20261101T140816Z-4904-21166`. Transcript:
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06ap/fedora-44-workstation-x86_64/20261101T140728Z-test-package-apply-repeat-status-restore-and-remove-9c5a8607/transcript.jsonl`
(SHA-256 `ce15cc22cf106e858768b21f0a70aa8b0edb5695af93c57f7c4e8221262a5e47`).
The Security Lab group now has all 137 members mapped across 43 opt-in
profiles.

Windows alignment for 06AO: no shared lifecycle, catalog, or package contract
changes. The Fedora RPM and filesystem integrity policy are platform-specific;
revisit only if shared integrity-policy semantics are proposed.

Windows alignment for 06AP: no shared package or lifecycle contract changed.
USB capture and replay remain a Fedora-specific opt-in RPM package; no Windows
USB behavior or device-operation contract is inferred. Revisit if cross-
platform capture/replay management is proposed.
