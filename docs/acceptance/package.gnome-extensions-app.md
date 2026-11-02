# GNOME Extensions manager acceptance

`package.gnome-extensions-app` is an opt-in Fedora 44 Workstation x86_64 RPM
candidate. Fedora packages GNOME's Extensions app for managing updates,
preferences, enable/disable, and removal. The paired profile also selects the
separately owned `package.gnome-browser-connector` for the official
extensions.gnome.org handoff. This is a manual user-managed path; it does not
install or enable the nine legacy v2 extension IDs.

The Fedora 44 Workstation x86_64 TCG run passed candidate gating,
plan/apply/repeat/status/remove, RPM signature and file verification, and
preserved a seeded extension directory. The run did not install, enable, or
launch extension code.

- Transcript: `.tmp-vm-acceptance-publisher-apps-17-gnome-manager/fedora-44-workstation-x86_64/20261101T193636Z-test-gnome-extensions-manager-profile-lifecycle-bed080ce/transcript.jsonl`
- Transcript SHA-256: `742b81bda1f656e7fe16321bacbe405c12c089a674d3c0c21bff4ab3fc44f937`
- VM image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`
- Catalog SHA-256: `b90108df3c503ed45b361babb87dff0267fe4620864090a76e649dbff187e126`

Sources: <https://packages.fedoraproject.org/pkgs/gnome-extensions-app/gnome-extensions-app/>,
<https://apps.gnome.org/Extensions/>,
<https://packages.fedoraproject.org/pkgs/gnome-browser-connector/gnome-browser-connector/>.
