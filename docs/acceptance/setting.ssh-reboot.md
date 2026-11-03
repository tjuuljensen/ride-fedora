# `setting.ssh-reboot` sudo policy acceptance

Status: **passed as an opt-in candidate**, 2026-11-02.

The disposable Fedora 44 Workstation x86_64 lifecycle used a test-only local
principal, `ride-ssh-target`. RIDE wrote a root-owned mode-0440 rule granting
only `(root) NOPASSWD: /usr/bin/systemctl reboot`. `sudo -l -U ride-ssh-target`
listed that exact rule; the account was not granted `NOPASSWD: ALL` or other
`systemctl` commands. The allowed command was invoked over SSH without a TTY;
the guest boot ID changed and both the test principal and harness account
reconnected.

The run checked plan, apply, repeat, privileged and unprivileged status, a
seeded unrelated sudoers file, conflict refusal, non-TTY reboot, SSH
reconnection, restore, and `visudo -c` before and after recovery. The unrelated
policy stayed byte-identical through reboot and restore. RIDE refused a seeded
principal-specific file without changing its hash, then removed only its own
unchanged rule on restore. Unprivileged status returned `requires-root`
without attempting escalation.

Deep security review checks:

- `scoped-privilege`: sudo lists only the named account's reboot command.
- `conflict-refusal`: a pre-existing principal-specific file is unchanged.
- `real-action`: the allowed system reboot actually occurs.
- `reconnect`: SSH returns for both the principal and harness account.
- `exact-recovery`: RIDE removes only its unchanged owned rule.
- `unrelated-policy-preservation`: the seeded rule remains byte-identical.

- Mocked lifecycle and CLI tests: `python3 -m unittest tests.test_v3_ssh_reboot -v` (7 passed)
- Bash completion tests: `python3 -m unittest tests.test_v3_cache_completion -v` (9 passed)
- Fedora VM test: `tests/acceptance/test_ssh_reboot.py`, 1 passed in 313.31 seconds
- Target: Fedora 44 Workstation x86_64, image SHA-256 `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`
- Acceleration: TCG
- Transcript: `.acceptance-runs/ssh-reboot-reconnect/fedora-44-workstation-x86_64/20261102T152200Z-test-named-user-reboot-rule-is-scoped-and-exactly-restored-e0a92264/transcript.jsonl`
- Transcript SHA-256: `5692f35ec5b0183b6248e0bf05854de261539ad31957c6425de073baf75c830f`
- Overlay SHA-256: `0c5f95ee7fed75b886f904f6004e4c1e2e0b204e32acbac1111044c2da1db7d5`
- Metadata SHA-256: `57f554f8ece55d108502bd662699be7dd266004c486dd05b57dbfe5791702dd4`

The high-risk sudo-policy boundary is covered for install, command scope,
conflict refusal, actual reboot, SSH reconnection, and exact restore. The
operation remains an explicit opt-in candidate. H112 tracks broader sshd
`Match` and multi-account policy coverage before expanding its supported use.
