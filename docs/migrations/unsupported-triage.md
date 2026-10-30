# Unsupported outcome triage and owner decisions

Status: **individual review in progress**, 2026-10-30. This review assigns
each of the original 99 `unsupported` source outcomes exactly one decision
batch. Three were approved for retirement, and one of those, Opera, was later
excluded from v3 scope. Teams desktop capability was also retired in the
fast-track review. The current ledger has 102 `unsupported` and 13 `retire`
outcomes. These decisions do not add an
operation, delete v2 code, or run a state-changing test. The
[migration ledger](../../migration/outcomes.json) and [progress report](progress.md)
are authoritative for current disposition. The eleven Citrix, Opera, and host-specific
exclusions are outside this review.

The [package path review](package-path-review.md) assesses the original
unsupported or retired `package.*` paths by product status, source, and
required v3 path. A v2 selector being active, commented, or absent does not
show whether that package was used on a machine. Selector coverage remains in
the ledger for traceability only and does not rank decisions or set a weaker
acceptance gate. Review all packages with the same source questions and the
appropriate risk-based recovery checks.

| Original decision lane | Outcomes | Owner decisions so far |
| --- | ---: | --- |
| Retirement proposals, R1-R2 | 10 | 2 retired, 6 retained for migration, 2 deferred. |
| Keep-or-drop choices, U1a-U3b | 38 | 11 retained, 1 later excluded, 3 deferred, 23 still to decide. |
| Migration design, D1a-D5a | 51 | Bitwarden AppImage retained; exact ownership, source, state, and recovery remain to design. |

At the initial triage point, 96 unsupported outcomes consisted of 68 migration-design outcomes
(51 original, six retained R2 inverses, and 11 retained U1 applications),
23 keep-or-drop choices, and five deferred owner decisions. The original
ledger total remained 180/180 after these decisions; six server package
additions and the later Opera exclusion make current progress 185/185
dispositioned. The runnable count is now 59. Retaining an outcome does not
make its unsafe v2 function runnable; a new owned implementation needs its
own evidence. Legacy functions and existing v2 machine state remain untouched.
These review groups do not override the small implementation batches in the
migration plan.
The later [v3.0 capability reassessment](v30-path-reassessment.md) requires
working paths or explicit owner-approved capability retirement for package and
setting behavior. Historical exact-method retirement and unsupported labels
alone do not establish v3.0 capability completion.

## R1: obsolete or mismatched integrations (3 original; 2 retired)

| Source outcome | Decision | Evidence and review trigger |
| --- | --- | --- |
| `workstation:package.NautilusHash` | **Full capability retired** by owner on 2026-10-30. | v2 uses `gtkhash-nautilus`; its own source notes the GNOME 43 break. The [Fedora GtkHash source](https://packages.fedoraproject.org/pkgs/gtkhash/) lists Caja, Nemo, and Thunar extensions, with no Nautilus subpackage. No v3.0 checksum context action is required. |
| `workstation:package.NautilusImageTools` | **Full capability retired** by owner on 2026-10-30. | v2 calls `nautilus-image-converter`; its [Fedora package record](https://packages.fedoraproject.org/pkgs/nautilus-image-converter/nautilus-image-converter/) lists only EPEL 7. No v3.0 image context action is required. |
| `workstation:package.GnomeExtInstaller` | **Decide later**, per owner on 2026-10-30; remains unsupported. | v2 clones the [archived upstream script](https://github.com/brunelli/gnome-shell-extension-installer) and overwrites a system symlink. `workstation:package.GnomeExtensions` remains a separate migration decision. A retained helper would need a maintained installer, pinned acquisition, and owned rollback. |

`workstation:package.BitwardenAppImage` moved to D1a during individual
review. Its v2 function downloads an RPM into `~/Applications`, but
[Bitwarden still publishes a Linux AppImage](https://bitwarden.com/help/desktop-app-feature-support/).
The owner chose to **keep the portable AppImage outcome** on 2026-10-30.
It needs a verified AppImage and vault-safe lifecycle before runnable status.

## R2: unsafe standalone cleanup functions (7 original; 6 retained)

Each row is a v2 remove-only path. The owner retained six desired inverse
outcomes for migration on 2026-10-30 and deferred GnomeRegion. This does not
authorize running a v2 removal on an existing machine. Historical v2 recovery
remains a separate operator concern; a future v3 inverse must act only on
journaled, RIDE-owned state.

| Source outcome | Owner decision | Unsafe v2 behavior | Migration requirement |
| --- | --- | --- | --- |
| `workstation:package.GnomeRegion` | **Decide later** | `RemoveGnomeRegion` writes an empty region, not the user's prior value. | Revisit after the owned GNOME region operation is designed. |
| `workstation:package.CustomKbrdShortcut` | **Keep for migration** | `RemoveCustomKbrdShortcut` clears the complete custom shortcut list and fixed slots, including unowned entries. | Scope the inverse to shortcuts created and journaled by v3. |
| `workstation:package.VPNProfiles` | **Keep for migration** | `RemoveVPNProfiles` deletes every NetworkManager VPN connection. | Delete only recorded RIDE-owned UUIDs and preserve unrelated connections. |
| `workstation:package.ExpressVPNProfiles` | **Keep for migration** | `RemoveExpressVPNProfiles` deletes name-matched connections without proving ownership. | Tie removal to an accepted private client deployment and exact owned UUIDs. |
| `workstation:package.ExpressVPNafterBoot` | **Keep for migration** | `RemoveExpressVPNafterBoot` filters the user crontab by matching text. | Give an owned boot timer or schedule an exact inverse. |
| `workstation:package.ScheduleExpVPNChange` | **Keep for migration** | `RemoveScheduleExpVPNChange` filters matching crontab lines without origin proof. | Record and restore an owned randomizer schedule without deleting unrelated jobs. |
| `workstation:package.KeyfileMounts` | **Keep for migration** | `RemoveKeyfileMounts` broadly deletes matching crypttab/fstab lines while encrypted volumes remain. | Name each owned mapping and prove backup, boot recovery, and unrelated-mount preservation. |

## Later individual product and behavior decisions (38 original)

These are not proposed for batch retirement. Some v2 installers are obsolete
while the product or desired behavior has a new path. Use the package path
review before asking for a product choice. Ask for an edition, variant,
private input, or retirement decision only where evidence cannot settle it.
Record a concrete reason and review trigger for any new retirement.

### U1a: Desktop and portable application sources (6)

Check each product's current source and choose its deployment form before
handler work.

- `workstation:package.AppImageLauncher` (medium risk; **decide later** on 2026-10-30): v2 selects a mutable beta publisher RPM and creates a user Applications directory without owned AppImage integration or safe inverse. Revisit after its source and recovery design is clearer.
- `workstation:package.BalenaEtcher` (medium risk; **keep for migration** on 2026-10-30): The v2 latest-release scrape is mutable and v3 has no pinned external-RPM acquisition, detection, or inverse handler, despite a current publisher RPM. Plan a pinned, owned application lifecycle.
- `workstation:package.ArduinoIDE` (medium risk; **keep for migration** on 2026-10-30): The v2 latest AppImage scrape and filename-glob inverse lack owned destination and collision handling; no v3 portable handler exists. Choose the deployment form and prove its owned inverse.
- `workstation:package.Discord` (medium risk; **keep for migration** on 2026-10-30): The publisher offers a Linux RPM, but v2 has no declared Fedora 44 source and v3 lacks a pinned publisher-RPM or owned Flathub handler. Choose an owned source and preserve the user profile.
- `workstation:package.Joplin` (medium risk; **keep for migration** on 2026-10-30): The v2 moving AppImage and glob inverse lack file ownership; the publisher script cannot be executed by a default v3 profile, and notebooks belong to the user. Pin an owned deployment and protect notebook data.
- `workstation:package.Xmind` (medium risk; **keep for migration** on 2026-10-30): The v2 old Zen RPM scrape does not identify the current publisher edition or package; its xmind-vana inverse lacks ownership and user-document recovery. Choose the edition and preserve documents.

### U1b: Browser, media, and HandBrake sources (6)

Verify the product source and channel; preserve any existing repository or
user profile unless the operation proves ownership.

- `workstation:package.Vivaldi` (medium risk; **decide later** on 2026-10-30): Vivaldi supports Fedora 43+, but the v2 scraped RPM and publisher-managed repository/key lack an owned inverse in v3. Revisit after source and browser-profile recovery design.
- `workstation:package.Chrome` (medium risk; **keep for migration** on 2026-10-30): The v2 HTTP Google repository file and name-based inverse have no owned source/key collision contract; v3 has no publisher RPM/repository handler. Design the official source and profile-safe recovery.
- `workstation:package.Opera` (medium risk; **out of scope** by owner on 2026-10-30): The v2 external repository and fixed-key-ID removal can erase pre-existing Opera trust. The owner subsequently excluded Opera from the v3 migration due to vendor ownership concerns; its source remains only as historical evidence.
- `workstation:package.Edge` (medium risk; **keep for migration** on 2026-10-30): The v2 mutable developer-channel repository and fixed repo-file inverse do not own the Microsoft key or preserve other Microsoft packages. Choose a channel and prove profile-safe recovery.
- `workstation:package.SpotifyClient` (medium risk; **keep for migration** on 2026-10-30): The v2 lpf-spotify-client request declares no source; LPF is interactive and a third-party Fedora repackaging is a distinct source with separate terms. Choose an acquisition provider and preserve user state.
- `workstation:package.HandBrake` (medium risk; **keep for migration** on 2026-10-30): The v2 DNF install relies on unaccepted RPM Fusion repository trust; the CLI and GUI RPMs are distinct and no exact-target package happy path was run. Accept source trust and choose CLI or GUI scope.

### U1c: Development, messaging, vault, and VMware sources (6)

Verify each edition and source; a current product does not validate the old installer.

- `workstation:package.PowerShell` (medium risk; **keep for migration** on 2026-10-30): The v2 function imports a system Microsoft key and a RHEL 7 repository; current Microsoft RPM guidance does not establish Fedora 44 support or an owned inverse. Review a current source and exact recovery.
- `workstation:package.WoeUSB` (medium risk; **keep for migration** on 2026-10-30): Fedora WoeUSB is orphaned and has no Fedora 44 package; the v2 DNF name cannot install on the declared target. Review a maintained WoeUSB-ng source and keep USB writing user-initiated.
- `workstation:package.Pidgin` (high risk; **decide later** on 2026-10-30): v2 installs Pidgin and OTR but has no account, key, plugin activation, encrypted-message, or user-data recovery contract. Revisit the combined outcome after compatibility and recovery review.
- `workstation:package.Bitwarden` (high risk): The v2 latest RPM scrape lacks pinned publisher verification and a vault-preserving inverse; no v3 external-RPM handler satisfies the deeper credential/data gate.
- `workstation:package.VMwareWorkstation` (high risk): v2 follows a moving publisher installer redirect and uses host-specific serial data without pinned provenance or full recovery.
- `workstation:action.PatchVMwareModules` (high risk): v2 pulls moving third-party kernel module source, stops service, and lacks module rollback.

### U2a: Forensic tools and the broad Security Lab bundle (5)

Choose a concrete case workflow or bounded tool set before implementation.

- `workstation:package.Plaso` (medium risk): The v2 pair only prints a URL; current Plaso has a broad Python dependency set and no pinned isolated Fedora 44 handler or lifecycle acceptance.
- `workstation:package.Autopsy` (medium risk): The v2 pair only prints a URL; publisher Linux ZIP and Java/Sleuth Kit requirements lack a Linux v3 portable handler and case-data-preserving inverse.
- `workstation:package.BulkExtractor` (high risk): The v2 moving-branch source build writes untracked files to /usr/local, removes shared dependencies, and has no owned inverse or seeded forensic-output recovery evidence.
- `workstation:package.EmailHeaderAnlzr` (high risk): The v2 clone and global pip steps create an unpinned persistent Flask service; service identity, bind scope, unit ownership, and Python/data inverse are unproven.
- `workstation:package.SecurityLab` (medium risk): The Fedora 44 security-lab group has 137 default packages and group state outside the per-package v3 journal; no safe group ownership or inverse is established.

### U2b: Snap, Tailscale, and Selenium roles (3)

Choose a concrete app, tailnet role, or browser automation target before migration.

- `workstation:package.Snap` (high risk): The v2 RPM-only pair does not establish usable Snapd, service/confined operation, or preservation of pre-existing snap apps and data; no high-risk recovery evidence exists.
- `server:package.Tailscale` (high risk): v2 executes an unpinned remote shell installer without trust, node identity, or inverse.
- `server:package.Selenium` (medium risk): Global unpinned pip install has no isolated environment, browser/driver target, or inverse.

### U3a: Tuning, profile, codec, and environment choices (6)

Confirm the desired behavior or target first; the v2 implementation is not an accepted v3 method.

- `workstation:setting.FastDNF` (medium risk): v2 rewrites administrator DNF config; DNF5 defaults do not reproduce its 15-download tuning and inverse loses prior values.
- `workstation:setting.ChromePreferences` (high risk): v2 overwrites legacy master_preferences and has a broken inverse; Chrome deployment itself remains unowned.
- `workstation:package.Codecs` (high risk): The legacy wildcard installs and optional Multimedia group upgrade have a changing package set and no complete owned inverse; RPM Fusion source trust is also unresolved.
- `workstation:setting.GnomeCustomFavorites` (high risk): v2 replaces all user favorites and includes retired Atom desktop ID.
- `workstation:setting.AliasWanIP` (high risk): v2 appends three external-DNS aliases and inverse uses a broad line deletion.
- `workstation:package.VMtoolsOnVM` (medium risk): The v2 hypervisor branches use inconsistent DMI checks and have no QEMU inverse; the pinned KVM image preinstalls all three guest-tool RPMs, so it cannot establish a RIDE-owned install.

### U3b: Alternate desktop setting variants (6)

Resolve conflicting values by owner choice and exact state recovery; selector
coverage cannot establish that a variant was unused.

- `workstation:setting.WindowCtlAppmenuClose` (medium risk): v2 writes one GNOME button-layout string without preserving the arbitrary prior user value.
- `workstation:setting.WindowCtlLeftClsMinMax` (medium risk): v2 writes another value to the same GNOME button-layout key without conflict or inverse handling.
- `workstation:setting.ScreensaverSlp15Lgn5` (high risk): The v2 lock variant conflicts with the 10-minute choice and has no exact inverse.
- `workstation:setting.VMKeyboardShortcut` (high risk): v2 VM variant reuses fixed custom-keybinding slots and can overwrite user or workstation bindings.
- `workstation:setting.GnomeMinimalFavorites` (high risk): v2 replaces the full user favorites list without snapshot or inverse.
- `workstation:setting.PowerPercentageLow20` (medium risk): The v2 PowerPercentageLow20 behavior lacks owned, exact prior-state recovery required for a runnable setting; see the batch review.

## Later individual decisions: migration design (51)

These source outcomes express behavior that may be retained, but the v2
method cannot be carried forward. The next decision for each is the exact
v3 owner, source or provider, target, state boundary, and recovery. High-risk
storage, encryption, network, and security work stays isolated; grouping
here is for review, not a shared installer or shared safety gate.

### D1a: Trusted sources and desktop integrations (6)

If retained, choose a verified provider, owned key/repository or extension state, and exact inverse.

- `workstation:package.RPMfusionRepos` (high risk): The v2 free/nonfree release-RPM install changes host package trust and its wildcard inverse deletes unowned repositories; v3 has no authenticated ownership-aware repository handler or safety/recovery evidence.
- `workstation:package.Flathub` (medium risk): The v2 remote-add has no owned remote journal and its inverse is not remote-delete; v3 lacks a scoped Flatpak remote handler and app-preserving inverse.
- `workstation:package.VisualStudioCode` (medium risk): The official Fedora code RPM requires an owned external repository and signing-key lifecycle; v3 has no handler or exact-target VM recovery, and v2 removes a hard-coded potentially shared key.
- `workstation:package.Brave` (medium risk): The official Fedora Brave RPM requires an owned external repository/key lifecycle; v3 has no handler or exact-target VM recovery, and v2 leaves its repository on removal.
- `workstation:package.GnomeExtensions` (high risk): The v2 bundle downloads user extensions through a mutable script and removes named user directories without ownership; native management RPMs alone do not reproduce the outcome.
- `workstation:package.BitwardenAppImage` (high risk): v2 downloads an RPM into `~/Applications` despite its AppImage name and cannot remove what it downloaded; the publisher offers a real Linux AppImage, which needs separate provenance and vault-safe recovery.

### D1b: Forensic acquisition and isolation (5)

If retained, choose pinned artifacts or isolated environments and preserve analysis output.

- `workstation:package.ASN` (medium risk): The v2 installer fetched an unpinned MIT script into `/usr/bin` and removed shared dependencies. The [v3 pinned user script and independent RPM path](../acceptance/package.asn.md) now pass a Fedora 44 opt-in lifecycle; live lookup and wider DNF transaction behavior remain H027/H008.
- `workstation:package.UnfURL` (medium risk): The v2 installer mutates the user global Python environment with unpinned pip dependencies. A [pinned opt-in user venv](../acceptance/package.dfir-unfurl.md) now has a Fedora 44 VM happy path; this original triage entry remains for decision history.
- `workstation:package.CyberChef` (medium risk): The v2 installer selected a mutable GitHub ZIP and wrote an unowned launcher. The [pinned v3 offline archive and owned desktop path](../acceptance/package.cyberchef.md) now pass a Fedora 44 opt-in lifecycle; browser interaction and updates remain H028.
- `workstation:package.Chepy` (medium risk): The v2 installer clones an unpinned Git branch, globally installs Python packages and PyInstaller, and copies a built binary into /usr/bin without owned recovery.
- `workstation:package.NetworkMiner` (high risk): The v2 mutable ZIP installer makes captures world writable and its inverse deletes the entire capture/output tree; no Linux owned portable handler or seeded-capture recovery exists.

### D2a: Desktop ownership and policy (6)

Define user or administrator ownership, detection, previous state, and exact recovery.

- `workstation:action.SetupUserDefaultDirs` (high risk): v2 chowns pre-existing ~/git and ~/bin and has no ownership-aware inverse.
- `workstation:package.Terminator` (high risk): v2 combines a Fedora RPM with a user iBus hotkey; inverse hard-codes a default instead of restoring the prior hotkey.
- `workstation:setting.FirefoxPreferences` (high risk): v2 overwrites three Firefox installation files with security and startup preferences and blindly deletes them on inverse.
- `workstation:setting.ScreenSaver` (medium risk): v2 sets three lock/idle values without an exact inverse or rollback for partial failure.
- `workstation:setting.WindowCtlMinMaxClose` (medium risk): The v2 WindowCtlMinMaxClose behavior lacks owned, exact prior-state recovery required for a runnable setting; see the batch review.
- `workstation:setting.GnomeRegionDaDK` (medium risk): The v2 GnomeRegionDaDK behavior lacks owned, exact prior-state recovery required for a runnable setting; see the batch review.

### D2b: Lock, shortcuts, power, and shell settings (5)

Define conflict-safe settings and seeded user-state recovery before a runnable handler.

- `workstation:setting.ScreensaverSlp10Lgn5` (high risk): v2 writes four lock and idle GNOME keys without prior values, atomicity, or inverse.
- `workstation:setting.CustomKeyboardShortcut` (high risk): v2 replaces the entire GNOME custom-keybindings list and fixed slots, potentially hiding user shortcuts.
- `workstation:setting.PowerPercentageLow15` (medium risk): The v2 PowerPercentageLow15 behavior lacks owned, exact prior-state recovery required for a runnable setting; see the batch review.
- `workstation:setting.BashAliases` (high risk): v2 appends to .bashrc and inverse deletes all .bash_aliases lines, including user content.
- `workstation:setting.AliasLsEza` (high risk): v2 appends ls=eza to .bash_aliases but inverse removes ride-log lines instead.

### D3a: Workstation system lifecycle (5)

Define bounded machine state and inverse; keep service, network, and Docker data safe.

- `workstation:setting.Hostname` (medium risk): Interactive v2 hostname has no declared profile value or exact prior-name restore.
- `workstation:action.UpdateFedora` (high risk): v2 runs an unbounded system update with no repeat-state observation, transaction inventory, or recovery.
- `workstation:package.Docker` (high risk): v2 adds an external repo, installs packages, and starts a service; removal does not preserve repo ownership or container volumes.
- `workstation:package.SmartMonTools` (high risk): Fedora RPM installation enabled smartd.service in the disposable VM; the generic package handler cannot recover prior service state.
- `workstation:setting.MulticastDNS` (medium risk): v2 rewrites nsswitch hosts lines without an owned inverse.

### D3b: Server baseline, updates, and host identity (4)

Split broad server behavior by role and maintain the network-devices ownership boundary.

- `server:action.UpdateFedora` (high risk): v2 performs a broad DNF update without a bounded planned transaction or rollback.
- `server:package.Required` (medium risk): The 11-package v2 bundle mixes VM tools, firewall, Samba, cron, and editors without role ownership or inverse.
- `server:package.AutoUpdate` (high risk): v2 enables an update timer and edits administrator DNF config without journaling prior state; its timer edit does not persist.
- `server:setting.Hostname` (high risk): Interactive host identity has no declared private value or prior-name recovery.

### D3c: Security and server services (4)

Require service, signature, firewall, SSH, or data recovery before execution.

- `workstation:package.ClamAV` (high risk): v2 runs freshclam after RPM installation; signature database ownership, freshness, failure, and recovery are undefined.
- `server:package.Docker` (high risk): External repository, docker group, daemon, images, and volumes have no owned inverse in v2.
- `server:package.Glances` (high risk): v2 overwrites /opt/glances and a systemd unit, opens a firewall port, starts a web service, and defines no inverse.
- `server:setting.NoRootLogin` (high risk): v2 edits administrator sshd_config in place without backup, syntax check, or inverse.

### D4a: VPN packages, profiles, and credentials (4)

Separate signed packages from private keys, profiles, activation, and unowned connections.

- `workstation:package.Wireguard` (high risk): v2 creates private keys and inverse recursively deletes /etc/wireguard, including unowned secrets.
- `workstation:package.OpenconnectVPN` (high risk): v2 builds moving Git source into /usr with no provenance or inverse.
- `workstation:action.ImportOpenVPNProfiles` (high risk): v2 imports implicit local .ovpn files and credentials into NetworkManager without owned UUIDs.
- `workstation:package.ExpressVPN` (high risk): v2 scrapes a moving RPM and prompts for activation while inverse leaves account and connection state.

### D4b: Workstation ExpressVPN scheduling (3)

Decide whether scheduling is wanted only after the VPN client and owned script are accepted.

- `workstation:action.StartExpressVPNafterBoot` (high risk): v2 appends an unowned crontab reboot job.
- `workstation:action.CreateExpVPNrandomizer` (high risk): v2 appends executable script text without provenance, idempotence, or inverse.
- `workstation:action.ScheduleRandomExpVPNChange` (high risk): v2 inserts an unowned recurring crontab job.

### D4c: Privileged policy and Server VPN (5)

Keep principals and secrets private; require owned sudo, key, service, route, and timer recovery.

- `workstation:setting.SSHreboot` (high risk): v2 writes user-specific passwordless sudoers and deletes it without validation or prior ownership.
- `server:action.GenerateSSHkeysRSA` (high risk): v2 interactively generates private keys in user home with weak .ssh directory mode and no existing-key recovery.
- `server:package.ExpressVPN` (high risk): Moving publisher RPM URL and activation prompt have no credential, profile, or service inverse.
- `server:action.CreateVPNrandomizer` (high risk): v2 appends unverified shell text to /usr/sbin with no bounded selection or inverse.
- `server:setting.VPNRandomizerPersistent` (high risk): v2 rewrites crontab with VPN jobs without owned schedule or unrelated-job recovery.

### D5a: Encrypted volumes and destructive disk actions (4)

Review each source outcome individually and implement only in isolated disposable-disk batches with backup and recovery.

- `workstation:package.VeraCrypt` (high risk): v2 silently runs a scraped setup script; v3 has no verified publisher-RPM trust handler or seeded encrypted-volume recovery.
- `workstation:action.AddExtraLUKSpasswords` (high risk): v2 adds keys to all detected LUKS devices without explicit target or key-slot journal.
- `workstation:action.EncryptUnpartitionedDisks` (high risk): v2 heuristic disk scan can erase and encrypt a disk without an exact device plan or rollback.
- `workstation:action.ReclaimEncryptDWUnmntPrt` (high risk): v2 heuristic unmounted-partition scan can reclaim data and alter mount/encryption state without inverse.

## Evidence and next action

The source-level reasons and review triggers above are taken from the
checked-in ledger and its linked batch records. The archived GNOME helper
and absent Fedora 44 Nautilus subpackages support R1. The Bitwarden
AppImage intent remains a migration decision even though its v2 method is
broken. An obsolete v2
acquisition method alone is insufficient to retire PowerShell,
[WoeUSB-ng](https://github.com/WoeUSB/WoeUSB-ng),
[AppImageLauncher](https://github.com/TheAssassin/AppImageLauncher), or
another product. No VM session is needed to record a non-runnable owner
decision. After an individual decision, update its ledger row and batch next
action, regenerate the progress report and burndown, run ledger/CI checks,
and record the decision in the migration plan. Review the remaining U1-U3
outcomes by source viability and risk. Revisit the five
deferred choices when their related design work makes the choice concrete.
