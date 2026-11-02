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
- Repeat apply and inspect status. Restore the run and confirm the owned file
  is gone, `sshd -t` still passes, the original effective root-login value is
  restored, sshd remains active, and a fresh non-root SSH channel still works.
- Refuse a conflicting or modified RIDE drop-in and roll back the staged file
  if the effective-policy check or reload fails.

## Fedora 44 Server evidence

The disposable VM run **PASS**ed plan, apply, syntax validation, effective
policy, a new non-root SSH channel after reload, repeat, status, restore, and
the prior `prohibit-password` policy check. The transcript is preserved in
`.acceptance-runs/generic-server-08-no-root-login/`; the checked-in scenario is
`tests/acceptance/test_sshd_root_login.py` and mocked ownership/failure tests
are in `tests/test_v3_sshd_root_login.py`.

The current OpenSSH server manual documents `PermitRootLogin` and `Include`
configuration. H103 tracks additional `Match` contexts and include-order
coverage before broader configuration claims. See the [sshd_config manual](https://man.openbsd.org/sshd_config.5).
