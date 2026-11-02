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
- Transcript: `.tmp-vm-acceptance-desktop-user-11-status-fix/fedora-44-workstation-x86_64/20261102T000307Z-test-vm-shortcut-and-favorite-profiles-exactly-restore-e84d31b5/transcript.jsonl`
- Transcript SHA-256: `9e5cc87a450ff3a372dd350e7c8ab14c053258f2d3a887c7bf1a8fd564098a22`
- Base image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`

The VM check did not wait for the configured idle period. H092 tracks a brief
visible confirmation of screen blanking and automatic lock behavior.
