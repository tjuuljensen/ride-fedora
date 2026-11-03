# Firefox managed add-ons acceptance

Status: **opt-in candidate; full Fedora 44 Workstation x86_64 lifecycle passed**
on 2026-11-02. Mozilla's global XPI directory is the selected deployment path;
the prior ExtensionSettings route did not install add-ons and is no longer used
by this operation.

## Completion checks

- Plan is read-only and the blocked operation requires explicit candidate
  evidence before mutation.
- Apply downloads each public AMO XPI, verifies the current AMO SHA-256 and
  embedded add-on ID, and installs only into
  `/usr/lib64/mozilla/extensions/{ec8030f7-c20a-464f-9b0e-13a3a9e97384}`.
- Existing files for a managed ID and ExtensionSettings entries for a managed
  ID are treated as conflicts. Unrelated administrator policy is unchanged.
- Repeat is unchanged and status reports `configured`.
- Firefox startup installs all 16 managed extensions in a seeded profile.
- Removal stores exact root-only recovery copies, removes only owned global
  XPI files, and reports `removal-pending` until Firefox restarts and the
  managed IDs leave the profile.
- Restore from `removal-pending` restores the exact XPI bytes. A second removal
  and restart removes managed extensions, then finalization clears only RIDE's
  recovery state and its directory if RIDE created it.
- Seeded unrelated profile data and administrator policy remain unchanged.

## Fedora 44 Workstation x86_64 evidence

The earlier ExtensionSettings path failed: Firefox loaded the 16 policy
entries but installed none. A focused disposable-VM probe then verified a
current uBlock Origin XPI against AMO metadata, SHA-256, and the embedded ID.
Firefox 150 installed it from the global
`/usr/lib64/mozilla/extensions/{application-id}` directory and removed it from
the seeded profile after the source file was removed and Firefox restarted.
The probe also confirmed that the other tested distribution directory did not
install it. Seeded profile data survived. This proves the deployment mechanism
for one add-on; it does not establish the RIDE lifecycle or all 16 add-ons.

Mozilla documents global Linux extension paths in its [Firefox support
article](https://support.mozilla.org/en-US/kb/cannot-uninstall-add-on-extension-or-theme)
and [add-on sideloading reference](https://devdoc.net/web/developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Alternative_distribution_options/Sideloading_add-ons.html).
The probe transcript and VM overlay are retained here:

- [VM transcript](../../.acceptance-runs/firefox-global-xpi-probe/fedora-44-workstation-x86_64/20261102T185722Z-test-firefox-global-xpi-install-and-removal-probe-76dd035d/transcript.jsonl)
- [VM metadata](../../.acceptance-runs/firefox-global-xpi-probe/fedora-44-workstation-x86_64/20261102T185722Z-test-firefox-global-xpi-install-and-removal-probe-76dd035d/metadata.json)
- VM overlay: `.acceptance-runs/firefox-global-xpi-probe/fedora-44-workstation-x86_64/20261102T185722Z-test-firefox-global-xpi-install-and-removal-probe-76dd035d/overlay.qcow2`

The complete candidate-gated `setting.firefox-addons` lifecycle passed on
Fedora 44 Workstation x86_64 with Firefox 150.0. RIDE verified all 16 current
AMO XPI digests and embedded IDs, applied and repeated the opt-in profile,
observed every managed extension in the seeded profile, staged exact recovery
copies, restored the pending removal, and then removed all 16 extensions after
a second browser restart. The test confirmed the unrelated policy and seeded
profile file were preserved throughout. The repository catalog is an opt-in
candidate and refuses apply unless the caller explicitly passes
`--allow-candidate`.

- [`test_firefox_addons.py`](../../tests/acceptance/test_firefox_addons.py)
- [VM transcript](../../.acceptance-runs/firefox-addons/fedora-44-workstation-x86_64/20261102T191938Z-test-firefox-global-xpi-lifecycle-and-restart-recovery-f4281180/transcript.jsonl)
- [VM metadata](../../.acceptance-runs/firefox-addons/fedora-44-workstation-x86_64/20261102T191938Z-test-firefox-global-xpi-lifecycle-and-restart-recovery-f4281180/metadata.json)
- VM overlay: `.acceptance-runs/firefox-addons/fedora-44-workstation-x86_64/20261102T191938Z-test-firefox-global-xpi-lifecycle-and-restart-recovery-f4281180/overlay.qcow2`

The security checks are recorded as passed: `scoped-privilege` is limited to
the root-owned global XPI directory and RIDE state; `conflict-refusal` covers
unowned files, policy conflicts, and tampered XPI refusal; `real-action` is
verified by all 16 IDs in Firefox; `reconnect` is verified by browser restarts;
`exact-recovery` compares restored XPI bytes with their recorded hashes; and
`unrelated-policy-preservation` compares the complete seeded policy after
apply, restart, removal, and finalization. Focused mock results are in
[`test_manage_firefox_global_xpis.py`](../../tests/test_manage_firefox_global_xpis.py).

H115 tracks v3.1 review of AMO licensing metadata and version/update behavior
for the 16 publishers, plus profile migration effects when a global add-on is
updated or replaced.
