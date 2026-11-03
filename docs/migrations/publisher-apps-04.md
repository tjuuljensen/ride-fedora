# Publisher Apps 04: Firefox managed add-ons

Status: **opt-in v3 candidate; full Fedora 44 lifecycle passed**, 2026-11-02.
The owner kept this active-preset outcome. The v3 operation wraps the exact
16-item `policies/firefox-extensions.json` list and remains outside base
profiles.

The v2 helper used Firefox `ExtensionSettings`. Fedora 44 Firefox 150 loaded
that policy but did not install any of its add-ons, even after the AMO install
URL was corrected to use extension IDs. The chosen v3 path downloads each
current public AMO XPI, verifies publisher metadata, SHA-256, and embedded ID,
then installs owned XPI files in Firefox's global Linux extensions directory.
Mozilla recognizes that directory for all Firefox profiles. RIDE keeps exact
recovery copies while removal is pending a Firefox restart and removes only
its own files and state.

## Batch completion checks

- Keep the 16 add-ons and their stable IDs from the v2 manifest.
- Refuse any pre-existing target file, conflicting managed ExtensionSettings
  entry, tampered owned XPI, unsafe symlink, or incomplete recovery copy.
- Check, configure, observe, repeat, remove, restore, and finalize behavior
  uses the explicit `configured`, `removal-pending`, and `absent` states.
- Prove all configured add-ons install into a seeded Fedora 44 Firefox profile
  and disappear after the owned source files are removed and Firefox restarts.
- Preserve unrelated ExtensionSettings policy and seeded profile data.
- Keep the operation opt-in. The complete disposable-VM lifecycle passed, so
  candidate status is appropriate; broader add-on UI and update behavior
  remain separate hardening.

## Evidence and next action

A disposable Fedora 44 Workstation probe proved the global-directory mechanism
for uBlock Origin: the current AMO artifact's SHA-256 and embedded ID matched,
Firefox installed it into a seeded profile, and removing the source removed
the profile add-on on restart. Seeded user data remained intact. A separate
distribution-directory attempt did not install it. This is evidence for the
mechanism only, not for the RIDE state machine or the full bundle.

Five focused mock tests cover idempotent install, exact ownership,
conflict/tamper refusal, removal recovery, and restart-aware finalization. The
full 16-add-on target lifecycle passed in
[`setting.firefox-addons.md`](../acceptance/setting.firefox-addons.md) and
[`test_firefox_addons.py`](../../tests/acceptance/test_firefox_addons.py).
The one-add-on mechanism probe was used only to select the deployment path;
the full RIDE test independently verified the complete list and lifecycle.
H115 tracks current AMO license metadata, version/update behavior, and profile
migration as v3.1 hardening.
