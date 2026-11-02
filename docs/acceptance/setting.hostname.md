# Static hostname acceptance

Status: **PASS on Fedora 44 Workstation and Server x86_64**.

- Workstation image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
- Workstation transcript: `.tmp-vm-acceptance-system-security-01-hostname-workstation-fixed/fedora-44-workstation-x86_64/20261102T003348Z-test-workstation-private-hostname-value-restores-exactly-d5927d6f/transcript.jsonl` (SHA-256 `10ffeeb45ee8df53035e2a2bf3486eea3e0b0c26de6ca66795533f8c627e4259`).
- Server image SHA-256: `efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`.
- Server transcript: `.tmp-vm-acceptance-system-security-01-hostname-server/fedora-44-server-x86_64/20261102T003632Z-test-server-private-hostname-value-restores-exactly-7a298bcc/transcript.jsonl` (SHA-256 `ec31c64dfbceb55f1b152baaa15e7e55800ba072089775f13ee29271ef58d186`).

## Declared behavior

- Operation: `setting.hostname`.
- Targets: Fedora 44 Workstation and Server x86_64.
- Input: a validated DNS hostname passed with `--value`; the value stays out of tracked profiles.
- Apply: `hostnamectl set-hostname --static` changes only the static hostname.
- Recovery: the run journal records the prior static hostname and restores that exact name.
- Refusal: invalid desired names, unset prior static names, and invalid current static names fail before mutation.

## Automated evidence

`tests/test_v3_system_hostname.py` covers value validation, state observation, and exact prior-name restoration. `tests/acceptance/test_system_hostname.py` checks apply, status, repeat, and exact restore on both declared VM targets. Both runs passed.
