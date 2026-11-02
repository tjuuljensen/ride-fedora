# Vivaldi Flatpak acceptance

`package.vivaldi` is an opt-in Fedora 44 Workstation x86_64 candidate. Vivaldi
documents installation from Flathub and states that the package is maintained
by a Vivaldi team member but is not yet officially endorsed or supported by
Vivaldi Technologies. Flatpak verifies the configured Flathub system remote.
Removal leaves the profile under `~/.var/app/com.vivaldi.Vivaldi` intact.

The shared disposable VM lifecycle checks candidate gating, plan, apply,
application ID and origin, status, repeat, remove, and preservation of a
seeded profile file. It does not launch the browser or validate extensions,
native messaging, sign-in, sync, or browsing behavior; those remain v3.1 work.

Sources: <https://help.vivaldi.com/desktop/install-update/install-vivaldi-on-flatpak/>
and <https://flathub.org/en/apps/com.vivaldi.Vivaldi>.

## Fedora 44 VM result

Vivaldi passed the opt-in lifecycle in a disposable Fedora 44 Workstation
x86_64 TCG overlay. The test checked signed Flathub remote configuration,
default candidate refusal, explicit apply, app ID and origin, status, unchanged
repeat, remove, and preservation of a seeded file under
`~/.var/app/com.vivaldi.Vivaldi`. It did not launch the browser or test native
messaging, sign-in, sync, extensions, or browsing; H080 tracks those checks.
Transcript: [focused Vivaldi and Xmind run](../../.tmp-vm-acceptance-publisher-apps-10-11-selected-flatpaks/fedora-44-workstation-x86_64/20261101T192709Z-test-vivaldi-and-xmind-flatpak-lifecycles-preserve-user-state-7fc6cc72/transcript.jsonl),
SHA-256 `d40316d6f438f95de87001a80f22c1cfc4d9d93c9efe23f84aa58b743bea801d`.
Image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Catalog SHA-256: `f645bbad67c9788e47a619367b76375c3a468a8da68d89425c264915a0cdda97`.
