# Keyfile mount removal acceptance

`setting.keyfile-mounts` passed as a candidate on Fedora 44 Workstation
x86_64, 2026-11-03. The scenario used a disposable second QEMU disk containing
a synthetic LUKS2 volume and a random synthetic keyfile. It did not use or
modify the guest's root/system volume.

## Completion checks

The implementation is deliberately limited to one explicitly named mapper
with one root-owned `/root/keyfile_*` keyfile and one `/dev/mapper/<name>`
fstab source. The helper refuses malformed or duplicate rows, unsafe
permissions, an active mapper, a mounted target, changed keyfile metadata, and
configuration changed since removal. It snapshots configuration bytes and
metadata privately and never stores key material.

The seven focused helper tests cover exact restoration and unrelated-row
preservation, active or mounted refusal, malformed and duplicate records,
unsafe keyfile permissions and mapper names, concurrent configuration edits,
keyfile changes, and rollback after an fstab update failure.

The VM scenario created a LUKS2 data volume and sentinel, then checked plan,
apply, repeat, status, run restore, and reboot behavior. After removal, the
guest rebooted with the mapper and mount absent while the keyfile and raw
encrypted volume hashes remained unchanged. After exact restoration, the
guest rebooted, automatically opened and mounted the same volume, and read the
same sentinel. Full `/etc/crypttab` and `/etc/fstab` hashes matched their
pre-operation values after restore.

Deep-safety evidence is recorded with the required domain checks:

- `exact-configuration-recovery`: both full configuration file hashes matched
  after run restore.
- `unrelated-entry-preservation`: the full files, including pre-existing
  entries, were byte-for-byte restored.
- `active-or-mounted-refusal`: the focused tests refused an active mapper and
  a mounted target without editing either configuration file.
- `keyfile-preservation`: the random keyfile hash was unchanged across removal,
  reboot, and restore.
- `encrypted-data-preservation`: the encrypted volume stayed byte-identical
  during the absent-state reboot and the sentinel hash matched after restore.
- `boot-recovery`: the absent state remained closed after reboot; restored
  crypttab/fstab opened and mounted the same data volume after reboot.

## Target and evidence

- Target: Fedora 44 Workstation x86_64.
- Base image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
- VM acceleration: KVM.
- Command: `/tmp/ride-acceptance-venv/bin/python -m pytest -q tests/acceptance/test_keyfile_mounts.py --vm-target fedora-44-workstation-x86_64 --vm-pilot setting.keyfile-mounts --vm-image .acceptance-runs/workstation-image-build/workstation.qcow2 --vm-output .acceptance-runs/keyfile-mounts-final`.
- Result: 1 passed in 95.67 seconds.
- Apply run ID: `20261102T233502Z-4015-3476`; repeat run ID: `20261102T233503Z-4319-13659`; restore run ID: `20261102T233526Z-1813-859`.
- Run directory: `.acceptance-runs/keyfile-mounts-final/fedora-44-workstation-x86_64/20261102T233413Z-test-selected-keyfile-mount-remove-restore-and-boot-recovery-0b328787/`.
- Transcript SHA-256: `f1e21552392a526dc4f51c6fc29fd6e7afa6e1c33eb0e3a03e341b2f3f7152b0`.
- VM metadata SHA-256: `26424e9da7ac306ad8395514e11d18c2bab185d9dea271cfbceb94a41ad69325`.
- Fedora image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
- Guest OS overlay SHA-256: `21633fdb713a58c6258ee5dbb19a3054bee1bc33ca2131745c7980c1e9b1a7a3`.
- Synthetic encrypted data disk SHA-256: `a0b299ff368b1dee9b1dc138197c0a02b783aa91d23b87324b9012abbaeeca61`.
- The run directory contains the transcript, QEMU logs, verified image metadata, source bundle digest, and disposable overlays. It is ignored by Git.

The catalog remains an opt-in candidate requiring `--allow-candidate`. Other
Linux editions, mapper/keyfile formats outside the stated contract, additional
volume discovery, encryption management, and Windows support are not covered.
