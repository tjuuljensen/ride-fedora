# Google Chrome Flatpak acceptance

`package.chrome` is an opt-in Fedora 44 Workstation x86_64 candidate for the
community-packaged Google Chrome Flatpak. Flathub describes it as an
unverified, community-provided package that Google does not support. Flatpak
verifies the configured Flathub remote with system GPG; the separate publisher
RPM method can be added as an independently selectable deployment.

The disposable VM lifecycle checks remote trust, candidate gating, plan,
apply, application ID and origin, status, repeat, remove, and preservation of a
seeded profile file under `~/.var/app/com.google.Chrome`. It does not launch
Chrome or test sign-in, sync, or browsing behavior; those remain v3.1 checks.

Flathub entry: <https://flathub.org/en/apps/com.google.Chrome>.

## Fedora 44 VM result

The signed-Flathub-remote candidate lifecycle passed on Fedora 44 Workstation
x86_64 in a disposable TCG overlay. It checked plan, default candidate refusal,
explicit `--allow-candidate` apply, application ID and Flathub origin, status,
repeat, remove, and preservation of a seeded app data file. This establishes
package lifecycle only; GUI sign-in and product behavior remain in the named
v3.1 work. The shared transcript is [`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-publisher-apps-11-flatpaks/fedora-44-workstation-x86_64/20261101T191731Z-test-browser-and-spotify-flatpak-lifecycles-preserve-user-state-767cc3d8/transcript.jsonl`](../../.acceptance-runs/legacy-vm/.tmp-vm-acceptance-publisher-apps-11-flatpaks/fedora-44-workstation-x86_64/20261101T191731Z-test-browser-and-spotify-flatpak-lifecycles-preserve-user-state-767cc3d8/transcript.jsonl); SHA-256
`300eb000edf07b7b177b59a17be5b4f3728cdda4ac4bac956e101297bbb79633`. Base image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`. Catalog SHA-256 used by the VM: `4290274513c38a3375e1e93a2349a692bb69eaf174316792e7d6b1d4d393d76f`.
