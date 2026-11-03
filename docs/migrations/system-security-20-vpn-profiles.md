# System and security batch 20: owned VPN profiles

Status: **complete as supported on Fedora 44 Workstation x86_64**,
2026-11-02. The owner kept `VPNProfiles` for migration. The v2
`RemoveVPNProfiles` function deletes every NetworkManager VPN connection,
including profiles it does not own. The v3 setting requires an explicit UUID
list and snapshots selected keyfiles before removal. The separate v2
`ImportOpenVPNProfiles` action remains outside this batch.

## Completion checks defined before implementation

- Preserve the cleanup capability as an opt-in setting; keep base profiles
  unchanged.
- Accept only one to 32 syntactically valid UUIDs supplied by the operator.
  Never discover targets by type, name substring, working directory, or
  repository contents.
- Require every selected UUID to resolve to a VPN keyfile in NetworkManager's
  system keyfile store. Refuse missing, duplicate, unsupported, or active
  profiles.
- Before each deletion, recheck the selected keyfile against the private
  snapshot and recheck that the connection is inactive.
- Snapshot each selected keyfile, including ownership, mode, modification
  time, and extended attributes, into root-owned mode-0600 files under a
  mode-0700 state directory. Keep credentials out of journals and logs.
- On any partial deletion, reload, or observed-state failure, restore all
  selected keyfiles and verify them before deleting recovery state.
- Explicit restore must refuse UUID or filename collisions and changed
  snapshots. It must preserve unrelated profiles and restore exact metadata.
- Mock tests cover apply/restore, repeat/status, selected active refusal,
  activation after snapshot, changed live profiles, partial deletion failure,
  reload failure, malformed and duplicate values, and unrelated-profile
  preservation.
- A Fedora 44 Workstation x86_64 disposable-VM happy path must prove plan,
  apply, repeat, status, journal secret exclusion, and exact restore before
  changing the catalog from blocked to supported. A mocked pass alone is
  insufficient. **Passed** on the pinned target; see the acceptance record.

## Source and method review

The v2 inverse deletes all connections with type `vpn`. The v3 implementation
uses `nmcli` only for the explicitly selected UUIDs and supports keyfiles in
`/etc/NetworkManager/system-connections`; other storage backends and user
connections are refused. Fedora's keyfile store requires root access because
it can contain credentials.

- [Fedora 44 NetworkManager OpenVPN package](https://packages.fedoraproject.org/pkgs/NetworkManager-openvpn/NetworkManager-openvpn/fedora-44.html)
- [Fedora 44 OpenVPN GNOME package](https://packages.fedoraproject.org/pkgs/NetworkManager-openvpn/NetworkManager-openvpn-gnome/)
- [NetworkManager `nmcli` reference](https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nmcli.html)
- [NetworkManager keyfile format and permissions](https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nm-settings-keyfile.html)

## Implementation and evidence

- Catalog ID: `setting.networkmanager-vpn-profiles`, supported only on Fedora
  44 Workstation x86_64; system scope; exact-state recovery.
- Handler: `lib/v3/networkmanager-vpn-profiles.sh`.
- Private state and keyfile recovery: `tools/networkmanager-vpn-state.py`.
- Mocked lifecycle: `tests/test_networkmanager_vpn_profiles.py`.
- Disposable-VM scenario: `tests/acceptance/test_networkmanager_vpn_profiles.py`.
- Acceptance report: `docs/acceptance/setting.networkmanager-vpn-profiles.md`.

The focused mocked tests pass (9 tests), and the declared disposable-VM
lifecycle passes as a supported operation without `--allow-candidate`. It
preserves exact selected keyfiles and every unrelated seeded profile. Do not
extend support beyond the accepted target or add activation and routing
behavior without a separate migration review.

The owner-kept `RemoveExpressVPNProfiles` outcome reuses this same operation:
the operator supplies the exact UUIDs of ExpressVPN profiles to remove.
Automatic name-substring discovery remains intentionally absent. The existing
mocked and Fedora 44 Workstation evidence applies unchanged because this is the
same handler and keyfile lifecycle.
