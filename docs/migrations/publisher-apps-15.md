# Xmind desktop outcome

The owner kept Xmind for v3.0. The v2 functions `InstallXmind` and
`RemoveXmind` scrape an old `/zen/download/linux_rpm/` endpoint, pass extracted
links to DNF, then remove `xmind-vana` by name. The publisher currently lists
Linux RPM and Flathub options. The initial v3.0 path is a Flathub Flatpak
candidate for the publisher's current proprietary Xmind app. This gives a
signed Flathub acquisition and an owned app ID while the legacy RPM scrape is
retired. The Flathub manifest grants broad home-directory and network access,
so the app is not confined to its private data directory. At review time, the
Flathub version is 26.03.04129 and the publisher download page offers RPM
26.05.01107. A separate publisher RPM operation remains addable after its
source, package identity, and coexistence/recovery behavior are verified.

## Completion criteria defined before implementation

- Pin the current Flathub application ID and verify the GPG-checked system
  remote on Fedora 44 Workstation x86_64. Keep it opt-in and outside base
  profiles.
- Verify plan, apply, repeat, status, and remove while preserving a seeded
  file under the app's data directory. Do not alter Xmind documents outside
  the managed application package.
- Keep GUI launch, existing document open/save/export, and account/sync
  behavior in H081. Investigate a failed VM run before retrying.

`package.xmind` uses `net.xmind.XMind`, the publisher's proprietary Linux
application packaged for Flathub. See the [operation acceptance record](../acceptance/package.xmind.md)
and the curated [Xmind profile](../../profiles/fedora-xmind.json). The shared
browser/media Flatpak acceptance covers its candidate gate, source origin,
repeat, inverse, and app-data preservation.

Sources: [Xmind Linux downloads](https://xmind.com/download),
[Flathub application](https://flathub.org/en/apps/net.xmind.XMind),
[Flathub manifest](https://github.com/flathub/net.xmind.XMind).
