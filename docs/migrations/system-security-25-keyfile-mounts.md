# System Security 25: owned keyfile mount removal

Status: **operable opt-in candidate on Fedora 44 Workstation x86_64**,
2026-11-03. The owner kept the v2 `RemoveKeyfileMounts` capability for v3.0.
Its old behavior deletes every matching crypttab row and related fstab rows,
without ownership proof, while leaving encrypted volumes and keyfiles in
place. v3 will keep this capability as an explicit, reversible removal of one
selected mapper configuration. It will not create encrypted volumes or keys.

## Completion checks defined before implementation

- Add a system-scope `setting.keyfile-mounts` operation with `configured` and
  `absent` states. Require `--value` to name exactly one crypttab mapper. Do
  not enumerate devices or infer selections from `/root/keyfile_*` names.
- Before removal, require exactly one selected crypttab record whose key path
  is a regular root-owned keyfile under `/root/keyfile_`; require exactly one
  related fstab record using `/dev/mapper/<mapper>`. Reject duplicate,
  malformed, symlinked, or ambiguous records and unsafe file ownership/modes.
- Refuse an active crypt mapping or mounted target. Do not unlock, unmount,
  change LUKS headers/key slots, modify the keyfile, or touch encrypted data.
- Save exact prior crypttab/fstab bytes and metadata in a private root-owned
  recovery directory before changing either file. Store configuration only,
  never key material. Remove just the selected records with atomic writes;
  roll back the first file if the second-file update fails.
- Restore only when both files are safe and the selected records have no
  conflicting edits. Reinsert the exact original records while preserving
  unrelated changes, or refuse with recovery data retained if a safe merge is
  not possible. Keep the recovery data until exact restoration succeeds.
- Focused mocked tests cover selector validation, ownership/mode refusal,
  duplicate and malformed records, active-mount refusal, staged-write failure,
  concurrent edits, exact restore, and preservation of unrelated entries.
- On a disposable Fedora 44 Workstation x86_64 VM, create a separate
  synthetic LUKS-backed data volume with a known sentinel. Exercise plan,
  apply, repeat, status, and exact run restore. Verify absent state survives a
  reboot, restored state opens the same volume at boot, the keyfile and
  sentinel hashes remain unchanged, and the system/root volume is untouched.
  Record the VM target, image digest, transcript, and recovery hashes.
- Keep this system operation out of base profiles. It remains a
  `--allow-candidate` operation because its contract is system-wide and
  intentionally narrow. Keep broader volume creation, key generation, device
  discovery, and arbitrary mount editing outside this operation.

## Implementation and acceptance result

`setting.keyfile-mounts` is implemented with a fixed mapper-name value and
`configured`/`absent` states. Seven focused tests pass for exact restoration,
active or mounted refusal, malformed and duplicate rows, unsafe keyfiles,
external edits, keyfile changes, and rollback after a second-file write
failure.

The exact Fedora 44 Workstation x86_64 VM lifecycle also passed: plan, apply,
repeat, status, exact run restore, reboot with the encrypted volume closed,
then reboot with the same volume opened and mounted from restored
crypttab/fstab. Crypttab and fstab hashes, the keyfile hash, and a synthetic
encrypted-volume sentinel matched their expected values. The root/system
volume was not used as a test target. Detailed transcript and image evidence
are in the [acceptance record](../acceptance/setting.keyfile-mounts.md).

The operation remains candidate-gated with `--allow-candidate` and is not
selected by a base profile. Its value is an explicit mapper name; broad device
discovery, multiple-mapper selection, key creation, key-slot changes, and
volume-data changes remain outside v3.0.

## Windows alignment checkpoint

Compared Fedora schema 3/profile schema 1 and Windows
`codex/ride-v3-migration` at `1871f7bcf0a9374351ffda2f8fc443c4a68cdcf5`.
Windows catalog/profile schemas are clean at that commit and have no encrypted
mount operation. This is a Linux-specific system configuration with no shared
run-state or lifecycle contract change. Recompare schemas at release review.

## Legacy source

`RemoveKeyfileMounts` is in `lib-fedora.sh`. The v2 function matches
`root/keyfile` text globally in `/etc/crypttab`, then deletes related lines
from `/etc/fstab` by mapper name. It does not unmount active volumes or remove
keyfiles. That implementation is preserved only as migration evidence.
