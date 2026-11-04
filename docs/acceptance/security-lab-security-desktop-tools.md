# Security Lab menu and SETools GUI acceptance

Batch 06AG adds two opt-in candidate RPM operations for Fedora 44 Workstation
x86_64: `security-menus` 38-8.fc44 and `setools-gui` 4.6.0-6.fc44. Both are
GPL-2.0-only and acquired from Fedora's signed RPM repository. The menu package
adds a Security Lab XDG category and launchers across the full tool collection;
SETools provides `apol`, a graphical SELinux policy analysis application. The
Fedora-listed Pagure source for `security-menus` is a read-only archive, while
Fedora still ships the package. SETools remains active upstream. See the
[menu package report](package.security-menus.md) and
[SETools package report](package.setools-gui.md).

## Completion checks

- Confirm the exact two unmapped inventory entries and isolated profile.
- Candidate refusal creates no journal.
- On the pinned Fedora 44 Workstation x86_64 VM, plan, apply, verify RPM
  signatures and root-run `rpm -V`, query status, repeat, restore, and compare
  package inventory.
- Inspect dependency changes, changes to existing RPMs, capabilities,
  scriptlets, menu/desktop files, and service-unit ownership.
- Do not launch menu items or Apol, or read/change host SELinux policy data.

## VM evidence

Passed on 2026-11-01 on `fedora-44-workstation-x86_64`, Fedora 44 Workstation,
x86_64, KVM. The verified base-image SHA-256 was
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Candidate refusal created no journal. The exact profile planned both RPMs as
absent candidates. Apply completed; signatures and root-run `rpm -V` passed;
status reported both installed; repeated apply reported unchanged; restore
completed, returning both requested RPMs to absent. No new RPM remained after
restore.

DNF installed 8 packages in the menu transaction and 29 in the SETools
transaction. Eleven already-installed Qt and GStreamer RPMs were upgraded to
resolve the SETools transaction. The final package inventory had the original
number of RPMs, with those 11 versions updated; restore does not reverse such
updates. H059 records the effect for promotion review. The menu package owned
`/etc/xdg/menus/applications-merged/security-lab.menu`, category directories,
and desktop launchers for the broader Security Lab collection, including
applications absent from this profile. SETools owned `/usr/bin/apol`. Neither
package had file capabilities, RPM scriptlets, or systemd units. No GUI was
opened, no launcher was run, and no SELinux policy was inspected or changed.

Pytest reported `1 passed, 73 deselected`.

Run IDs: apply `20261101T121855Z-2547-1510`, repeat
`20261101T121927Z-3938-7124`, restore `20261101T121927Z-4317-28113`. Transcript:
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06ag/fedora-44-workstation-x86_64/20261101T121826Z-test-fedora-security-lab-security-desktop-tools-batch-and-profile-8e32bd08/transcript.jsonl`
(SHA-256 `1c049961ccd818573189be71ed4b65b5538d5e7e201131a971f4ee34b1d109af`).
H059 holds menu visibility, uninstalled-launcher behavior, Apol fixture tests,
and package-update recovery review for v3.1.
