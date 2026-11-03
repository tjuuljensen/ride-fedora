# Experimental VMFS6 reader candidate

Status: **install path implemented; genuine VMFS6 behavior unverified**.

`package.vmfs6-reader` is an explicit Fedora 44 Workstation x86_64 candidate.
The `forensic-vmfs6-reader` profile installs Fedora-signed GCC, GNU Make, and
libuuid development headers, then downloads the pinned GPL-2.0-only upstream
source archive, verifies its SHA-256, builds only `debugvmfs6` without
`VMFS_WRITE`, and installs it in an owned user-local directory. It does not
open an image during installation.

The build path has mocked ownership, digest refusal, failure cleanup, and
removal checks. The earlier Fedora 44 VM probe built this pinned reader, but
its bundled image was VMFS3 and was rejected. No genuine VMFS6 fixture has
been read. This evidence authorizes the opt-in install candidate only; it does
not establish VMFS6 access or a supported reader.

From the repository root, apply the profile as the normal user. It installs
three Fedora RPM build prerequisites, which remain installed after profile
removal, and the user-local reader. The profile requires the explicit
candidate gate:

```bash
./ride.sh plan --profile forensic-vmfs6-reader --allow-candidate
./ride.sh apply --profile forensic-vmfs6-reader --allow-candidate
```

After applying this profile with the explicit candidate gate, the executable
is `~/.local/bin/debugvmfs6`. For manual testing, pass only an authorized,
disposable regular image file and follow the upstream command interface.
Do not use live datastore devices, block devices, or production VMFS data.
Record a fixture's source/license, SHA-256, known file manifest, reader output,
and before/after image hashes. RIDE does not inspect image content and removes
only unchanged files it owns.
