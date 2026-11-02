# NetworkMiner deployment path review

Status: **kept for v3.0; Fedora Linux acquisition is identified, but the fixed artifact digest still needs verification.**

Netresec documents a Linux path using Fedora `mono-devel` and optional `gtk2`,
then extracts NetworkMiner under `/opt` and runs `NetworkMiner.exe` with Mono.
The current product page advertises the free edition and says NetworkMiner runs
on Linux; the official source page states GPLv2. It is a real current path,
not the older 2.x-only installation path. See the [Linux install guide](https://www.netresec.com/?month=2025-04&page=Blog&post=How-to-Install-NetworkMiner-in-Linux),
[product/download page](https://www.netresec.com/?page=NetworkMiner), and
[license page](https://www.netresec.com/?page=NetworkMinerSourceCode).

The official guide links a fixed NetworkMiner 3.2 ZIP at
`https://download.netresec.com/networkminer/NetworkMiner_3-2.zip`. The
product page's displayed digest is `daceec649fb4fe59b11e4a9e4ecd5f51c1dd37824280dfbeac67bec27b6b6d60`,
while the vendor's linked current hash endpoint returned
`782e3d4d0b917a5aadf59966ab7d21ab30dbd593eff14e426f2b580a2e3f89e1` during
this review. The download host was not reachable from this environment, so the
version and artifact digest could not be reconciled against the fixed ZIP.
Do not pin either value to the fixed-version artifact until verified.

The product extracts files, credentials, and certificates from PCAPs and can
listen for PCAP-over-IP; its output is local. RIDE's package lifecycle must not
open captures, start live receiving, or choose output directories. A future
v3.0 operation can install a verified user-local ZIP and Fedora's Mono runtime
as an explicit opt-in; H110 holds fixture-based output, capture authorization,
and user-data review.

## Completion checks before operable status

- Verify the fixed 3.2 archive digest and confirm its file list has no path
  traversal or symlink entries.
- Use Fedora's signed Mono runtime; leave GTK optional unless GUI evidence
  shows it is required.
- Install only under the invoking user's RIDE-owned directory and refuse
  changed or unowned files on remove.
- On Fedora 44 Workstation, verify plan, candidate gating, apply, repeat,
  status, executable/runtime presence, remove, restore, and seeded user-file
  preservation. Do not launch live capture or open PCAP input as part of the
  package lifecycle.

The release remains non-runnable until the fixed artifact and owned lifecycle
are verified. Any user-requested capture or PCAP analysis is a separate
high-risk scope decision.
