# System and security package-only acceptance

Status: **PASS; package-only support** on Fedora 44 x86_64 Workstation,
2026-10-30.
The package-only operations are `package.networkmanager-libreswan`,
`package.networkmanager-libreswan-gnome`, `package.networkmanager-l2tp`,
`package.networkmanager-l2tp-gnome`, and `package.keepassxc`.

See the [predefined completion checks](../migrations/system-security-packages.md).

The pinned Workstation image SHA-256 was
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
The three source outcomes passed a disposable VM lifecycle in overlay
`20261030T140321Z-test-package-only-security-lifecycles-ea7c45b7`
using candidate catalog SHA-256
`34563bd251abb7f7db5d4e1bdc5ace5294ff7600ce52a7b8a249f72d561cbd0e`.
Each opt-in profile passed absent plan, candidate-gate refusal, signed RPM
apply and verification, repeat, status, restore preview and execution,
explicit remove, and return to the exact prepared RPM baseline. Existing
NetworkManager connection UUIDs and active connections, relevant service
enable/active states, and a seeded vault-file checksum stayed unchanged
during apply and after recovery. The test completed in 128.62 seconds.

The targeted failure probe in a separate disposable VM inserted a missing
RPM after `package.networkmanager-libreswan`. The journal recorded the first
package as changed and the second as failed. Restore removed the first
package and returned RPM inventory, connection state, relevant services,
and the seeded vault checksum to baseline. It passed in 47.31 seconds. The
unchanged DNF handler's general mocked failure tests are also reused.

The vault sentinel checks file preservation; it is not a real KeePass
database. The package operations do not open a vault, create or connect a
VPN profile, or claim protocol or GUI behavior. H020 and H021 retain those
separate v3.1 reviews.

After promotion to `supported`, one focused profile smoke ran in overlay
`20261030T140802Z-test-supported-package-only-profiles-7aadac51`
with catalog SHA-256
`65d8d097d935c28a51d7464eca5de181f97e6d589fb4403766bd053b8a1c4e8b`.
All three opt-in profiles planned as supported, applied without
`--allow-candidate`, repeated unchanged, and restored the exact prepared
RPM, connection, service, and vault-sentinel state. It passed in 69.38
seconds. The supported metadata changed the gate and acceptance links;
the Fedora RPM handler and package mappings remained the same as in the
earlier lifecycle and failure runs.

The current supported catalog then passed the full signed-package and
seeded-state lifecycle again in overlay
`20261030T141205Z-test-package-only-security-lifecycles-3d7aa7d1`, with
catalog SHA-256
`6376ff7e42f262e5b07c34e8760d71497a566889a6a2dfe24a7be54482099976`.
The following partial-failure VM setup exhausted `/tmp` quota before its
scenario ran. After confirming no guest was active, completed overlay disks
were deleted while retaining metadata and transcripts. The focused
partial-failure test then passed on the same supported catalog in overlay
`20261030T141450Z-test-vpn-plugin-partial-failure-preserves-seeded-state-ae869451`
in 45.47 seconds. No unchanged scenario was retried before investigating
the infrastructure failure.
