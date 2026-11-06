# SSH root-login policy acceptance

Status: **PASS — operable opt-in Fedora 44 Server x86_64 candidate**.

`setting.ssh-root-login` maps v2 `SetNoRootLogin` to an owned OpenSSH server
drop-in, `/etc/ssh/sshd_config.d/00-ride-root-login.conf`. It sets
`PermitRootLogin no` without editing the administrator's main configuration.
The handler verifies the file contents and effective root policy, validates
the complete config with `sshd -t`, then reloads `sshd.service`. It does not
restart the daemon or change an existing SSH session. Restore removes only the
RIDE-owned file and reloads the prior policy.

Select it only in the opt-in `fedora-server-no-root-login` profile. Candidate
operations require the explicit `--allow-candidate` flag. Keep at least one
working non-root administrator account before applying this policy.

## Completion checks

- Run in a disposable Fedora 44 Server x86_64 VM with an active sshd service.
- Record the effective `PermitRootLogin` value before apply for the root user
  in the tested hostname/address context.
- Apply the profile; require `sshd -t`, effective `PermitRootLogin no`, and an
  active `sshd.service`. Open a fresh non-root SSH channel after reload.
- Repeat apply and inspect status. Run `unset`; confirm the owned file is gone,
  `sshd -t` still passes, the original effective root-login value is restored,
  sshd remains active, and a fresh non-root SSH channel still works. Repeat
  unset, restore that run to configured, then restore the original apply run
  and confirm the prior policy and connection are recovered again.
- Refuse a conflicting or modified RIDE drop-in and roll back the staged file
  if the effective-policy check or reload fails.

## Fedora 44 Server evidence

The 2026-11-05 Fedora 44 Server x86_64 TCG run **PASS**ed plan, apply, syntax
validation, effective policy, a new non-root SSH channel after reload, repeat,
status, direct unset, repeat-unset, restore to configured, and restore of the
original apply run to absent with the prior effective root policy. Transcript:
`.acceptance-runs/align03-owned-unset/fedora-44-server-x86_64/20261105T151628Z-test-sshd-root-login-policy-reload-and-exact-restore-ee8ab295/transcript.jsonl`
(SHA-256 `3555e4b8388beee1185f19b85d1a237b9411b03d23fdc4056c202d5a3dcb3b61`);
the VM image SHA-256 is
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`. The
checked-in scenario is
`tests/acceptance/test_sshd_root_login.py` and mocked ownership/failure tests
are in `tests/test_v3_sshd_root_login.py`.

The current OpenSSH server manual documents `PermitRootLogin` and `Include`
configuration. H103 tracks additional `Match` contexts and include-order
coverage before broader configuration claims. See the [sshd_config manual](https://man.openbsd.org/sshd_config.5).
