# GNOME idle and lock timing acceptance

Target: Fedora 44 Workstation x86_64 disposable VM. Operation:
`setting.gnome-lock-timing`.

Status: PASS.

- Seeded four non-default GNOME user values before testing.
- Applied the 10-minute idle / 5-minute lock profile and the 15-minute idle /
  5-minute lock profile. Both set the expected idle delay, idle activation,
  automatic lock, and 300-second post-activation lock delay.
- `status setting.gnome-lock-timing` recognized the selected state without a
  profile value. Reapplying each profile reported unchanged.
- `restore` after each profile returned the exact four seeded values.
- Automated failure injection confirms a mid-transaction write failure rolls
  back all four settings; malformed saved state is rejected.
- Transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-desktop-user-11-status-fix/fedora-44-workstation-x86_64/20261102T000307Z-test-vm-shortcut-and-favorite-profiles-exactly-restore-e84d31b5/transcript.jsonl`
- Transcript SHA-256: `9e5cc87a450ff3a372dd350e7c8ab14c053258f2d3a887c7bf1a8fd564098a22`
- Base image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`

The VM check did not wait for the configured idle period. H092 tracks a brief
visible confirmation of screen blanking and automatic lock behavior.

The v2 `EnableScreenSaver` and `DisableScreensaver` states also passed their
separate Fedora 44 Workstation lifecycle on 2026-11-02. The test applied each
opt-in profile, verified effective GNOME values and unchanged `lock-delay`,
confirmed repeat and status, and restored the exact seeded values.

- Test: `tests/acceptance/test_screensaver_states.py`
- Result: 1 passed in 462.56 seconds
- Transcript: `.acceptance-runs/fedora-44-workstation-x86_64/20261102T140149Z-test-legacy-screensaver-states-preserve-lock-delay-and-restore-52fc6028/transcript.jsonl`
- Transcript SHA-256: `63455a3037b1d8f1fd49074f6c3e38223e371c9ff3ca232380b72a609599ea16`
- Overlay SHA-256: `a2c6e793d7758ae0f9bce74e2f46b98e51acf9ba2eafb12dc34654923b665cf0`
- Source bundle SHA-256: `6968bd25c83157bf566d002cc44a970dccb471df4d5a527d09fb98efbc4b9553`
- Base image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`

These states are operable on the declared Workstation target. H092 retains
the brief visible confirmation because headless VM evidence does not establish
the user-visible blanking and locking experience.
