# Discord RPM acceptance

Target: Fedora 44 Workstation x86_64 disposable VM. This candidate uses the
official stable Discord RPM pinned to version 1.0.168 and SHA-256
`ade5550aa86cb4562116d5f5731d5af6110c7865d0712da5b25cdaf9d4137b61`.
Discord does not publish a verifiable RPM signature for this direct download;
the evidence is the HTTPS publisher download, observed digest, and RPM name,
version, and architecture metadata check performed before DNF installation.

The acceptance test refuses apply without `--allow-candidate`, then checks
plan, apply, installed RPM identity, status, repeat, and remove. A sentinel in
`~/.config/discord` confirms the package lifecycle preserves user profile data.
The test does not launch Discord or validate login, voice, or screen sharing;
those checks remain in the v3.1 hardening queue.

Completion evidence: `test_pinned_publisher_rpm_lifecycle` passed on
2026-11-01 against Fedora 44 Workstation x86_64 using TCG and image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Transcript:
`.tmp-vm-acceptance-publisher-apps-10-discord-final/fedora-44-workstation-x86_64/20261101T190131Z-test-pinned-publisher-rpm-lifecycle-fedora-discord-package-discord-discord-none-f2ff995b/transcript.jsonl`
(SHA-256 `9c4796d486cdd0d414a083843f9eea16f4d26df7f7404baa666b63d78ae8c0bd`).
The checked catalog SHA-256 was
`87b9894d56f5661e589b24cf97b6bdbc80496602076cf5dbdddf015a374fbd83`.

The covered catalog ID is `package.discord`.

Run with the shared Fedora 44 acceptance harness:

```bash
python3 -m pytest tests/acceptance/test_publisher_pinned_rpms.py -k discord \
  --vm-target fedora-44-workstation-x86_64 \
  --vm-image /path/to/workstation.qcow2
```
