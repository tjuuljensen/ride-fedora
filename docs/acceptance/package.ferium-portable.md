# `package.ferium-portable` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Server x86_64.
Run: 2026-11-02, QEMU TCG, 7m10s. Reviewer: Codex.

The operation installs Ferium v4.7.1 to an owned user-local directory and
creates an owned `~/.local/bin/ferium` link. It is available only through the
opt-in `fedora-server-ferium` profile. It does not manage Ferium configuration,
profiles, mod lists, or Minecraft output.

The upstream Linux release does not publish an archive checksum. v3.0 fetches
the fixed official release URL over HTTPS, checks the executable version, and
records the archive and binary digests for later integrity checks. This does
not independently authenticate the archive contents. H096 tracks stronger
publisher provenance if upstream publishes a Linux checksum or signature.

The disposable Fedora 44 Server x86_64 scenario used the pinned image
SHA-256 `efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`
and a fresh QEMU overlay. It seeded Ferium configuration and a mod file, then
checked candidate gating, apply, repeat, status, remove, and preservation of
both seeded files. All assertions passed. The test used TCG because this host
does not expose `/dev/kvm`; the VM overlay was discarded after the run.

Run artifacts are retained under
[`generic-server-19-ferium`](../../.acceptance-runs/generic-server-19-ferium/):
`metadata.json` records the target, image digest, source bundle, and catalog;
`transcript.jsonl` records the guest commands; and `serial.log` and `qemu.log`
record the guest and hypervisor output. The initial run exited before tests
started because one 10-second SSH probe timed out under TCG. The VM harness now
continues polling through that timeout; its focused unit test passes.

To repeat from the repository root with the prepared environment:

```sh
python3 -m pytest tests/acceptance/test_ferium.py \
  --vm-target fedora-44-server-x86_64 \
  --vm-image /path/to/fedora-44-server.qcow2 \
  --vm-accel tcg \
  --vm-output /tmp/ride-vm-acceptance
```

The operation remains opt-in and requires `--allow-candidate`; H096 tracks
independent publisher checksum or signature verification if Ferium adds it.
