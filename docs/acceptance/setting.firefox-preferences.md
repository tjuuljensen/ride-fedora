# Firefox preferences acceptance

`setting.firefox-preferences` is an opt-in Fedora 44 Workstation x86_64
candidate. It uses Firefox's documented AutoConfig mechanism to apply the
values kept from v2. RIDE writes three known files only when all are absent,
records their hashes, and removes them only when all still match. It refuses
pre-existing or modified files. This prevents replacing an administrator's
Firefox configuration or deleting later changes.

The mocked lifecycle tests cover first apply, repeat, exact removal, refusal of
an unowned file, and preservation when an owned file is edited. Fedora 44
Workstation x86_64 TCG acceptance passed candidate gating, apply/repeat/status,
Firefox startup with AutoConfig active, and removal of all three files. Firefox
is a persistent GUI process, so the headless smoke test confirmed it stayed
alive for 25 seconds and then stopped it with the declared timeout. H083 tracks
review of values that may be obsolete or undesirable in current Firefox,
including WebRTC, Sync, the old new-tab URL, and the Linux-irrelevant Windows
preference.

- Transcript: `.tmp-vm-acceptance-desktop-user-01-firefox-final/fedora-44-workstation-x86_64/20261101T195916Z-test-firefox-preferences-lifecycle-and-startup-441e0a71/transcript.jsonl`
- Transcript SHA-256: `86499dd9878d7d5d8a1c36a03de585293ac953d17982366c322d9ac1cc7bff85`
- VM image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`
- Catalog SHA-256: `b082751c382af1d02f53ae2bb319bb77b0e2e22e2fb4d56976f3fca0680dce6e`

Mozilla currently documents AutoConfig as the mechanism for preferences that
are not covered by `policies.json`; its setup requires a startup preference
file and a JavaScript configuration file. Fedora 44 RPM targets are limited to
the `/usr/lib64/firefox` paths declared by this operation.

Sources: [Mozilla AutoConfig guide](https://support.mozilla.org/en-US/kb/customizing-firefox-using-autoconfig),
[Firefox policy templates](https://mozilla.github.io/policy-templates/),
[Fedora Firefox package](https://packages.fedoraproject.org/pkgs/firefox/firefox/).
