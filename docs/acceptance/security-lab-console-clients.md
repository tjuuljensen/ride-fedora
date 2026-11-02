# Security Lab console client package acceptance

Batch 06Y covers `mcabber`, `mutt`, `screen`, and `telnet` as Fedora 44
Workstation x86_64 opt-in candidate RPM operations. RIDE manages package
presence only; acceptance does not launch a client, connect to a server, or
read/write user mail, chat, or session data.

## Completion checks

- Verify exact source group membership and profile mapping.
- Verify candidate refusal creates no run journal.
- On the disposable Fedora 44 Workstation target, plan, apply, check RPM
  signatures and root-run `rpm -V`, query status, repeat apply, and restore.
- Inspect RPM scripts, file capabilities, dependencies, and changes to
  pre-existing RPMs.
- Preserve packages present before apply and restore all package identities
  to the expected post-DNF state.
- For `package.screen`, reuse the existing Server install/restore evidence and
  verify its newly declared Workstation target and absent state.

## VM evidence

Passed on 2026-10-31 with the pinned disposable target
`fedora-44-workstation-x86_64` (Fedora 44 Workstation, x86_64). Candidate
refusal, plan, apply, RPM signatures, root-run file checks, status, repeat,
restore, and package identity recovery passed. Run IDs were
`20261031T150009Z-2789-561` (apply), `20261031T150034Z-5023-29580`
(repeat), and `20261031T150035Z-5626-18179` (restore). All four RPMs were
initially absent. Mcabber added `enchant`, `libidn`, `libotr`, and `loudmouth`;
Mutt added `perl-File-Copy`, `tokyocabinet`, and `urlview`. Restore removed all
seven dependencies. No pre-existing RPM changed, and none of the four packages
declared scriptlets or file capabilities. No client was launched, and no
network connection or user data was accessed.

The retained command transcript is
`.tmp-vm-acceptance-security-06y/fedora-44-workstation-x86_64/20261031T145939Z-test-fedora-security-lab-console-clients-batch-and-profile-28349d55/transcript.jsonl`
(SHA-256 `2ada5bd4bcd10840109dc45cbd7e2a10e7e3c163edacd36cabc28d8f91964015`);
pytest reported `1 passed`. The new Workstation install/remove path for
`package.screen` passed. Its unchanged Server install/restore behavior is
covered by the [generic Server Required report](generic-server-required.md).
H050 tracks account, protocol, and user-data review; Telnet's archived
upstream and cleartext protocol remain explicit v3.1 hardening concerns.
Catalog operation IDs in this accepted profile: `package.mcabber`, `package.mutt`, `package.screen`, `package.telnet`.
