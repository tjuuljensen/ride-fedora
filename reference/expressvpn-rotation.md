# ExpressVPN location rotation tool

`tools/expressvpn-rotate.sh` replaces the v2 randomizer's legacy
`expressvpn refresh` / `disconnect` / `list all` sequence with the current
`expressvpnctl connect "LOCATION"` interface and a user-owned location list.
It does not install ExpressVPN, activate an account, schedule itself, or manage
server presets.

## Configure and preview

Run as the desktop user, from the repository root:

```bash
install -d -m 700 "$HOME/.config/ride"
cat > "$HOME/.config/ride/expressvpn-rotate.conf" <<'EOF'
# Use exact names accepted by expressvpnctl.
Germany - Frankfurt - 1
Netherlands - Amsterdam - 1
EOF
tools/expressvpn-rotate.sh --dry-run
```

Dry run chooses a configured location but makes no VPN request. It excludes the
last location whose request returned success when another choice is available.
That small state file is stored under
`~/.local/state/ride/expressvpn-rotate/last-location` (or under
`$XDG_STATE_HOME`). The stored value tracks the last successful CLI request; it
does not prove which location is currently connected.

## Request a rotation

After confirming the preview, run:

```bash
tools/expressvpn-rotate.sh --rotate
```

The user must already be logged into ExpressVPN. Its GUI must be running or
background mode must already be enabled. The tool invokes `expressvpnctl
connect "LOCATION"` directly, never disconnects first, and updates its
last-request state only if the command exits successfully. The command's exit
status is not proof that the VPN tunnel, route, DNS, or kill switch recovered.
If it fails, investigate the client and network state before retrying.

## Current evidence and limits

ExpressVPN's [Linux CLI guide](https://www.expressvpn.com/support/vpn-setup/app-for-linux-cli/)
documents `expressvpnctl get regions`, `expressvpnctl connect`, the exact
location argument, and the GUI/background-mode prerequisite. It does not
document a stable current-location query or guarantee an atomic location
handoff. Therefore the tool does not claim to preserve the active route during
a failed switch and is not yet evidence for enabling unattended rotation.

The workstation and generic-server v2 scheduling outcomes remain separate
migration items. This utility does not install a timer or rewrite crontabs. In
particular, it must not be used to replace the server-side
`VPNRandomizerPersistent` schedule until the `network-devices` owner confirms
the deployed consumers, executor identity, deployment path, and rollback.
