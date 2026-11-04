# Xmind Flathub acceptance

`package.xmind` is an opt-in Fedora 44 Workstation x86_64 candidate for
`net.xmind.XMind`. Xmind currently publishes Linux RPM and Flatpak options;
the selected Flatpak is packaged from the publisher's Linux build and verified
through the configured GPG-verified Flathub system remote. The Flatpak is
proprietary. Removal leaves its app data directory in place; documents outside
that directory are not touched by the package operation.

The shared disposable VM lifecycle checks candidate gating, plan, apply,
application ID and origin, status, repeat, remove, and preservation of a seeded
app data file. It does not launch Xmind or validate paid features, sync,
exports, or opening existing mind maps; those remain v3.1 checks.

Sources: <https://xmind.com/download>,
<https://flathub.org/en/apps/net.xmind.XMind>,
<https://github.com/flathub/net.xmind.XMind>.

The Flatpak manifest also requests broad access to the user's home directory
and network. This package is not confined to app-private data; the operation
only preserves the managed Flatpak data directory on removal and does not
claim that Xmind cannot access other files. At review time, Flathub lists
version 26.03.04129, while the publisher download page links a newer Linux RPM
(26.05.01107). The selected v3.0 path is the signed-remote Flatpak candidate;
H081 tracks a separately owned publisher RPM and version freshness review.

## Fedora 44 VM result

Xmind passed the opt-in lifecycle in a disposable Fedora 44 Workstation x86_64
TCG overlay. The test checked signed Flathub remote configuration, default
candidate refusal, explicit apply, app ID and origin, status, unchanged repeat,
remove, and preservation of a seeded file under
`~/.var/app/net.xmind.XMind`. It did not launch the app or test account, sync,
paid features, or document open/save/export behavior; H081 tracks those checks.
Transcript: [focused Vivaldi and Xmind run](../../.acceptance-runs/legacy-vm/.tmp-vm-acceptance-publisher-apps-10-11-selected-flatpaks/fedora-44-workstation-x86_64/20261101T192709Z-test-vivaldi-and-xmind-flatpak-lifecycles-preserve-user-state-7fc6cc72/transcript.jsonl),
SHA-256 `d40316d6f438f95de87001a80f22c1cfc4d9d93c9efe23f84aa58b743bea801d`.
Image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Catalog SHA-256: `f645bbad67c9788e47a619367b76375c3a468a8da68d89425c264915a0cdda97`.
