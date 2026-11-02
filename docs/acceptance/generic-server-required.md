# Generic Server `InstallRequired` acceptance

Status: **PASS; operable opt-in candidates on Fedora 44 Server x86_64**. The
completion criteria were recorded before the catalog and profile changes in
[`generic-server-required.md`](../migrations/generic-server-required.md).

The opt-in `server-required-tools` profile contains ten one-way installed-state
operations. `firewalld` is isolated in `server-firewall-package`. Both profiles
stay separate from `server-base`; candidate operations require
`--allow-candidate`.

| v2 RPM | v3 operation | Profile |
| --- | --- | --- |
| `open-vm-tools` | `package.open-vm-tools` | `server-required-tools` |
| `nano` | `package.server-nano` | `server-required-tools` |
| `wget` | `package.wget` (`wget2-wget`) | `server-required-tools` |
| `firewalld` | `package.firewalld` | `server-firewall-package` |
| `unzip` | `package.unzip` | `server-required-tools` |
| `git` | `package.git` | `server-required-tools` |
| `cifs-utils` | `package.cifs-utils` | `server-required-tools` |
| `samba-client` | `package.samba-client` | `server-required-tools` |
| `samba-common` | `package.samba-common` | `server-required-tools` |
| `cronie` | `package.cronie` | `server-required-tools` |
| `screen` | `package.screen` | `server-required-tools` |

The focused disposable Fedora 44 Server x86_64 run passed plan, candidate gate,
apply, repeat, status, signed RPM and `rpm -V` checks, executable probes,
one-way profile removal, and the isolated firewall profile. The pinned image
SHA-256 is
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`.

The image began with 707 RPM identities. DNF installed 82 additional RPMs and
upgraded six existing identities without losing any original name/architecture
pair: `expat` 2.7.3-2 to 2.9.0-1, `fuse3-libs` 3.18.2-1 to 3.18.3-1,
`libldb` and `libwbclient` 4.24.0-6 to 4.24.7-1, and `ngtcp2` plus
`ngtcp2-crypto-ossl` 1.21.0-1 to 1.22.1-1. All ten requested package RPMs
had valid Fedora signatures and passed `rpm -V`; the package command probes
passed. Applying the profile again was unchanged. Removing it retained all ten
packages and left the post-install inventory unchanged.

The Server image already had `nano`, Wget, `unzip`, `cifs-utils`, `cronie`,
and `firewalld`. It also began with `firewalld` active and enabled. The isolated
firewall operation planned `installed` and completed unchanged; the daemon
remained active/enabled and the `/etc/firewalld` file hash remained
`47adeb7e1115ba736852e5889f0da00d64d7eb058f5758bb870d75a947bda602`. This
target run therefore verifies its existing state but does not exercise a new
firewalld RPM installation. H036 queues that deeper absent-package security
check before claiming the install transition.

Installing `open-vm-tools` enabled `vmtoolsd.service` and `vgauthd.service` by
RPM preset, while both remained inactive under the KVM test hypervisor. Cronie
remained active/enabled; firewalld's service state did not change. The
VMware-specific service behavior remains an opt-in package effect and is not
claimed as tested on VMware hardware.

Acceptance transcript:
`/tmp/ride-fedora-server-required-09/fedora-44-server-x86_64/20261031T094039Z-test-server-required-tools-and-firewall-installation-are-opt-in-and-bounded-14edadbb/transcript.jsonl`
(SHA-256 `e00ca2cd834823de09f782d3585a355a1bb1135fb9b750531de9789fcc2a9eb2`). Run IDs: apply
`20261031T094105Z-2977-15606`, repeat `20261031T094333Z-7985-31842`, remove
`20261031T094334Z-9186-7872`, and firewall profile
`20261031T094337Z-10278-3903`. The DNF transaction upgrade review is tracked
in H035.
