# GNOME favorites and shortcut acceptance

Target: Fedora 44 Workstation x86_64 disposable VM. The test seeds user-owned
keybindings and a GNOME favorite list, then applies the VM shortcut, default
favorites, and minimal favorites profiles.

Status: PASS, Fedora 44 Workstation x86_64 disposable VM.

Operations: `setting.gnome-custom-shortcuts` and
`setting.gnome-favorite-apps`.

- The shortcut profile added only two RIDE-owned entries, repeated as unchanged,
  and restored the seeded user list, global binding, and custom shortcut.
- Both favorite profiles applied their declared desktop-ID lists, repeated as
  unchanged, and `restore` returned the exact seeded favorites list.
- The test exercised the explicit opt-in candidate gate.
- Transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-desktop-user-08-pass/fedora-44-workstation-x86_64/20261101T234141Z-test-vm-shortcut-and-favorite-profiles-exactly-restore-4a860915/transcript.jsonl`
- Transcript SHA-256: `f51485174018f26ea4793e0a2a8338433bcc65e27fca3c0ee1753da0f4ae6ea3`
- Base image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`

H085 and H089 retain short visual reviews of app availability and shortcut
dispatch.
