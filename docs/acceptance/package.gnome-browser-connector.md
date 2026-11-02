# `package.gnome-browser-connector` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

The Fedora 44 package installs a native messaging host that connects a browser
extension to GNOME Shell and `extensions.gnome.org`. The browser add-on and
extension choices remain user-driven; this operation does not install,
enable, update, or remove any user extension. Fedora publishes
`gnome-browser-connector` 42.1-14.fc44 under GPL-3.0-or-later. GNOME documents
the rename from `chrome-gnome-shell` and the browser store installation path.

The opt-in profile passed candidate refusal, plan, signed Fedora RPM and
`rpm -V` verification, native connector binary and host manifest checks,
repeat, status, restore, explicit install/remove, and package inventory
recovery. A seeded pre-existing user extension directory retained its file
hash. No browser was launched and no extension was installed or changed.

VM evidence: Fedora 44 Workstation x86_64; pinned image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`;
overlay `20261101T143807Z-test-package-apply-repeat-status-restore-and-remove-9723361e`;
catalog SHA-256
`d0c504e3c5643413ddd85ea3cfd67f5947415378b53c7e5cb334487b3ee9409f`;
transcript [transcript.jsonl](../../.tmp-vm-acceptance-provider-10-gnome-connector-complete/fedora-44-workstation-x86_64/20261101T143807Z-test-package-apply-repeat-status-restore-and-remove-9723361e/transcript.jsonl)
SHA-256 `b4ecb3ac6117a95f05b072e43e635f493523061344ffab0a9bfbb0e49ce8affb`.
Run IDs: apply `20261101T143839Z-3061-11252`, repeat
`20261101T143852Z-3973-7678`, restore `20261101T143853Z-4407-15789`,
explicit install `20261101T143856Z-5074-14313`, explicit remove
`20261101T143858Z-5349-27867`.
