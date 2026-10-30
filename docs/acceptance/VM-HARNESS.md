# Disposable Linux VM acceptance

Run these commands from the repository root on a Linux x86_64 host. KVM is the
default and requires accessible `/dev/kvm`; use explicit `--vm-accel tcg` for
slower software emulation when KVM is unavailable. The host needs Python 3,
`qemu-system-x86_64`, `qemu-img`, `genisoimage`, `ssh`, `scp`, and `ssh-keygen`.
The target matrix includes Fedora
44 Cloud Base, a [locally built Workstation image](fedora-44-workstation-image.md),
and a [locally built Server image](fedora-44-server-image.md), all x86_64.
The runner accepts only the selected pinned qcow2 SHA256 digest and
checks the guest's actual distro, release, and architecture before testing.
It also checks `/etc/os-release` `VARIANT_ID` against the pinned edition, so
Cloud Base evidence cannot be mislabeled as Workstation or Server evidence.
It launches QEMU directly; libvirt is not required on the test host.
For Cloud Base, obtain the qcow2 file and signed checksum from the
[Fedora Cloud download page](https://fedoraproject.org/cloud/download/);
verify the Fedora signature and checksum according to that page. The
Workstation and Server image builds and verification are recorded in their linked recipes.
The target digests are recorded in
[`targets.json`](../../tests/acceptance/targets.json). Do not use an image of a
different release under the same target ID.

Create a host-only test environment, then run the suite with an absolute local
image path:

```bash
python3 -m venv /tmp/ride-acceptance-venv
/tmp/ride-acceptance-venv/bin/python -m pip install -r tests/acceptance/requirements.txt
mkdir -p /tmp/ride-acceptance-runs
/tmp/ride-acceptance-venv/bin/python -m pytest tests/acceptance -v \
  -p no:cacheprovider --rootdir=. \
  --vm-target fedora-44-cloud-x86_64 \
  --vm-image /absolute/path/to/Fedora-Cloud-Base-Generic-44-1.7.x86_64.qcow2 \
  --vm-output /tmp/ride-acceptance-runs \
  --junitxml=/tmp/ride-acceptance-runs/fedora-44-cloud-results.xml
```

The command boots one fresh VM per test from a read-only base and a new qcow2
overlay with the base image's virtual size. cloud-init creates or configures
the `ride-test` account, adds its disposable SSH key, and grants passwordless
sudo inside the guest. On Cloud Base it installs `jq` and `sudo`; the
Workstation and Server builds already include them and skip that repository refresh. The runner
copies only the current RIDE client, catalog, profiles, handlers, requirements,
and acceptance evidence directory. It never applies operations to the host.
Guest package installation uses Fedora repositories through QEMU user-mode
networking. The only incoming guest port is SSH forwarded to a host loopback
port.

The `tcg` option keeps the same digest, guest edition, architecture, overlay,
and host-only SSH checks. It is slower, so the harness allows a longer guest
boot and cloud-init wait. Record the acceleration mode from `metadata.json`
with the acceptance evidence; a timeout or failed test still requires
investigation before retrying.

Each scenario writes its overlay, seed, serial log, QEMU log, target metadata,
and `transcript.jsonl` under `--vm-output`. This directory can be large and
contains a temporary SSH private key and command output; review it before sharing.
The VM process is stopped
after the scenario. Its overlay is retained for investigation. Delete the
output directory when evidence is no longer needed; this does not affect the
verified base image. A failed test must stay failed in the JUnit result and
must not be treated as accepted behavior.

For reversible package operations, the suite checks `package.exfatprogs` from an absent state:
read-only plan, apply, repeated apply, status, RPM signature and file
verification, restore, explicit remove, and partial-failure journaling. A
test-only missing package is added to a temporary guest catalog for failure
injection; it is never added to the published catalog. The three accepted
base package operations run on their declared editions without the candidate
override; all other candidates still require `--allow-candidate`.
The suite also compares installed package inventories before and after
recovery, including versions, so leftover dependencies or changed packages
fail acceptance. If the pinned base has the pilot package installed, the suite
records the original read-only plan and removes that package only in its
disposable overlay before exercising the install path. The Workstation target
also declares `package.less` as a selectable pilot. Use `--vm-pilot package.less`
with that target and `-k test_package_apply_repeat_status_restore_and_remove`
for its focused lifecycle check.

Use `--vm-pilot package.openssh-clients` on the Workstation target for its
installed-only contract. The suite selects scenarios from the catalog's
`recovery` value before booting a VM. It checks an unchanged apply on the
intact image and a repair from an artificially absent client in a separate
disposable overlay. The latter uses `rpm -e --nodeps` only to create a test
fixture, then checks DNF dependency health and refusal of unsupported restore
and remove. Do not use that removal command on a persistent system.
On the Server target, the default pilot is `package.less` and
`--vm-pilot package.openssh-clients` selects the client. The profile smoke
scenarios select their own matching target before starting a VM.

The Cloud image is appropriate for the generic package pilot. It is not a
Fedora Workstation or Fedora Server image. Before changing a catalog row to
`supported`, record the required edition-specific tests and review the result
under `docs/acceptance/<operation-id>.md` as described in this directory's
README. Later Debian and Ubuntu entries can reuse the same VM and CLI contract
once apt/dpkg providers exist; each new target needs its own verified image,
guest setup, package observations, and VM result. Desktop, graphical, and
hardware-dependent operations need separate VM or physical test lanes.
