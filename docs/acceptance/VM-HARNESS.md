# Disposable Linux VM acceptance

Run these commands from the repository root on a Linux host with accessible
`/dev/kvm`. The host needs Python 3, `qemu-system-x86_64`, `qemu-img`,
`genisoimage`, `ssh`, `scp`, and `ssh-keygen`. The first target is Fedora 44
Cloud Base x86_64. The runner accepts only its pinned qcow2 SHA256 digest and
checks the guest's actual distro, release, and architecture before testing.
It launches QEMU directly; libvirt is not required on the test host.
Obtain the qcow2 file and signed checksum from the [Fedora Cloud download
page](https://fedoraproject.org/cloud/download/); verify the Fedora signature
and checksum according to that page. The target digest is recorded in
[`targets.json`](../../tests/acceptance/targets.json). Do not use an image of a
different release under the same target ID.

Create a host-only test environment, then run the suite with an absolute local
image path:

```bash
python3 -m venv /tmp/ride-acceptance-venv
/tmp/ride-acceptance-venv/bin/python -m pip install -r tests/acceptance/requirements.txt
mkdir -p /tmp/ride-acceptance-runs
/tmp/ride-acceptance-venv/bin/python -m pytest tests/acceptance -v \
  --vm-target fedora-44-cloud-x86_64 \
  --vm-image /absolute/path/to/Fedora-Cloud-Base-Generic-44-1.7.x86_64.qcow2 \
  --vm-output /tmp/ride-acceptance-runs \
  --junitxml=/tmp/ride-acceptance-runs/fedora-44-cloud-results.xml
```

The command boots one fresh VM per test from a read-only base and a new qcow2
overlay. cloud-init creates the `ride-test` account, adds its disposable SSH
key, grants passwordless sudo inside the guest, and installs `jq` and `sudo`. The runner
copies only the current RIDE client, catalog, profiles, handlers, requirements,
and acceptance evidence directory. It never applies operations to the host.
Guest package installation uses Fedora repositories through QEMU user-mode
networking. The only incoming guest port is SSH forwarded to a host loopback
port.

Each scenario writes its overlay, seed, serial log, QEMU log, target metadata,
and `transcript.jsonl` under `--vm-output`. This directory can be large and
contains a temporary SSH private key and command output; review it before sharing.
The VM process is stopped
after the scenario. Its overlay is retained for investigation. Delete the
output directory when evidence is no longer needed; this does not affect the
verified base image. A failed test must stay failed in the JUnit result and
must not be treated as accepted behavior.

The current suite checks `package.exfatprogs` from an initially absent state:
read-only plan, apply, repeated apply, status, RPM signature and file
verification, restore, explicit remove, and partial-failure journaling. A
test-only missing package is added to a temporary guest catalog for failure
injection; it is never added to the published catalog. Package changes remain
behind the existing candidate gate in the normal client.
The suite also compares installed package inventories before and after
recovery, including versions, so leftover dependencies or changed packages
fail acceptance.

This Cloud image is appropriate for the generic package pilot. It is not a
Fedora Workstation or Fedora Server image. Before changing a catalog row to
`supported`, record the required edition-specific tests and review the result
under `docs/acceptance/<operation-id>.md` as described in this directory's
README. Later Debian and Ubuntu entries can reuse the same VM and CLI contract
once apt/dpkg providers exist; each new target needs its own verified image,
guest setup, package observations, and VM result. Desktop, graphical, and
hardware-dependent operations need separate VM or physical test lanes.
