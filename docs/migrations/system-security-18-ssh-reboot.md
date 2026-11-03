# System and security batch 18: SSH reboot sudo policy

Status: **operable opt-in candidate on Fedora 44 Workstation**, 2026-11-02. This
isolated high-risk batch migrates the kept `EnableSSHreboot` and
`DisableSSHreboot` v2 pair. The v2 function writes a user-specific sudoers file
with a passwordless `systemctl reboot` alias, but also grants password-prompted
access to the full `systemctl` binary. Its inverse deletes the file without
checking ownership or validating the policy.

## Completion checks defined before implementation

- Keep the v2 user-visible capability: a named non-root local account can run
  `sudo systemctl reboot` without a password. Scope the v3 rule to that exact
  command; do not carry over the unrelated permission to run any `systemctl`
  command as root.
- Require the caller to supply the principal explicitly as a validated Linux
  username. Do not put host-specific usernames in the public profiles or
  catalog. Refuse missing users and `root`.
- Use a per-user RIDE-owned file under `/etc/sudoers.d`. Refuse pre-existing
  files, symlinks, modified owned files, and unsupported ownership or mode.
  Write atomically without replacing existing state.
- Validate the temporary rule and complete sudoers configuration with
  `visudo`; apply only if both validations pass. Do not restart SSH or reboot.
- Observe `configured` only when the exact RIDE file is root-owned, mode 0440,
  syntactically valid, and the required command rule is present. Restore removes
  only that unchanged owned file. A seeded unrelated sudoers file must remain
  byte-identical across apply and restore. Unprivileged status must report the
  root requirement without attempting elevation or reading protected policy.
- Mock principal validation, path conflicts, invalid syntax, interrupted
  writes, exact repeat, external modification refusal, and restore. On a
  disposable Fedora 44 Workstation VM, verify plan, apply, repeat, `sudo -l`
  command scope, status, exact restore, and full `visudo -c`. Invoke the
  permitted reboot over non-TTY SSH, then verify the guest and named principal
  reconnect and seeded policy remains intact.
- Keep the operation opt-in and candidate; broader `sshd Match` and
  multi-account policy coverage remains in H112.

The public ID is `setting.ssh-reboot`, with a required per-invocation
`--value <linux-user>`; no profile is added because its principal is
host-specific. The focused mocked lifecycle and Fedora 44 Workstation
acceptance passed, including an automated non-TTY SSH reboot and reconnect.
The candidate stays opt-in. See [acceptance evidence](../acceptance/setting.ssh-reboot.md).
