# Chrome preferences migration

## Completion checks

- Map each v2 `master_preferences` entry to a current Chrome policy or record
  its deployment-specific replacement. Never edit a Chrome profile database.
- Use only Google's recommended-policy directory so users can change the
  defaults. Write one RIDE-owned JSON file and a protected hash manifest;
  refuse pre-existing, symlinked, or modified files and remove only the exact
  unchanged file.
- Fixed policy identifiers only; no policy names or JSON accepted as shell.
- Mocked tests cover all selected values, repeat, unowned-file refusal,
  modified-file refusal, and exact removal.
- A Fedora 44 Workstation x86_64 disposable VM installs Chrome through the
  existing Flathub candidate, checks `chrome://policy` through the actual
  wrapper, verifies repeat/status, and removes the policy and application
  while preserving seeded app data. Do not sign in or access personal data.

## Legacy mapping

The current Flathub `com.google.Chrome` wrapper imports host policy files from
`/etc/opt/chrome/policies/{managed,recommended,enrollment}`. Google documents
the Linux policy directories and exposes a recommended-policy channel for
user-changeable settings. Sources: [Flathub wrapper](https://github.com/flathub/com.google.Chrome/blob/master/chrome.sh),
[Google Linux policy setup](https://support.google.com/chrome/a/answer/9025927?hl=en),
and [Chrome Enterprise policies](https://chromeenterprise.google/policies/).

| v2 `master_preferences` value | v3 treatment |
| --- | --- |
| `homepage=https://www.google.com` | `HomepageLocation` recommended policy |
| `homepage_is_newtabpage=false` | `HomepageIsNewTabPage` recommended policy |
| `browser.show_home_button=true` | `ShowHomeButton` recommended policy |
| `browser.check_default_browser=false` | `DefaultBrowserSettingEnabled=false`; recommended default remains user-changeable |
| `safebrowsing.enabled=false` | `SafeBrowsingEnabled=false` retained as an explicit candidate selection. Google marks this policy deprecated and recommends `SafeBrowsingProtectionLevel`; the v2 disabled value reduces browser protection, so the opt-in profile calls it out and must not enter base profiles. |
| `safebrowsing.reporting_enabled=false` | `SafeBrowsingExtendedReportingEnabled=false` retained alongside the legacy setting; verify policy status on the pinned Chrome build. The deprecated/overlapping policy behavior is a hardening item. |
| `net.network_prediction_options=2` and DNS prefetch disabled | `NetworkPredictionOptions=2` recommended policy; the value covers DNS, connection prediction, and prerendering. |
| `bookmark_bar.show_on_all_tabs=true` | `BookmarkBarEnabled=true` recommended policy |
| Import bookmarks/history/home page/search engine disabled | Replaced by profile-safe behavior: RIDE neither launches Chrome for import nor reads, writes, or migrates profile data. The Flatpak preserves app data on package removal. |
| Suppress first-run bubble/default-browser prompt; `first_run_tabs` | No stable user preference equivalent is applied. The RIDE profile does not launch or suppress onboarding; Chrome owns its first-run UI. The default-browser policy controls only the prompt preference. |
| No desktop/quick-launch/taskbar shortcuts | Flatpak owns its desktop launcher lifecycle; no Windows-only taskbar value is emitted. |
| Do not launch Chrome | Preserved: RIDE only writes policy and never launches the browser during apply. |
| Do not register update launch; MSI/system-level/require-EULA/verbose logging | Obsolete or inapplicable RPM/MSI installer directives. The selected Flatpak deployment owns updates and system scope; no update policy or logging override is added. |

The operation owns only `/etc/opt/chrome/policies/recommended/ride-fedora.json`
and `/var/lib/ride-fedora/owned-chrome/setting.chrome-preferences.json`. Its
fixed `--value` IDs allow profiles to select a subset; values are rendered from
trusted handler code. The [opt-in profile](../../profiles/fedora-chrome-preferences.json)
selects all retained browser defaults and explicitly warns that Safe Browsing
is disabled. Chrome and policy remain out of the base profiles.

Google's current policy reference marks `SafeBrowsingEnabled` deprecated in
Chrome 83 and points to `SafeBrowsingProtectionLevel`. H091 tracks current
behavior and policy deprecation, including whether the reporting value remains
recognized on the pinned Flathub build. Review before broadening or changing
the opt-in profile.

## Fedora 44 Workstation evidence

Acceptance: pending.
