# Unsupported outcome triage and retirement approval

Status: **proposal only**, 2026-10-30. The authoritative ledger still has 99
`unsupported` source outcomes. This review assigns each of those 99 outcomes
exactly one decision batch. It does not change a ledger disposition, add an
operation, delete v2 code, or run a state-changing test. The [migration ledger](../../migration/outcomes.json)
and [progress report](progress.md) remain authoritative until an approval is
applied. The 15 Citrix and host-specific exclusions are outside this review.

| Decision lane | Outcomes | What happens next |
| --- | ---: | --- |
| Retirement proposals, R1-R2 | 11 | Owner can approve the two larger batches independently. |
| Keep-or-drop choices, U1a-U3b | 38 | Decide each feature or value individually before migration work. |
| Migration design, D1a-D5a | 50 | Decide the exact owner, source, state, and recovery for each outcome. |

Approving both retirement batches changes only their 11 ledger rows from
`unsupported` to `retire` with a documented reason and review trigger.
The v3.0 total stays 180/180 and the runnable count stays 54; the category
counts become 88 unsupported and 25 retired. Legacy functions and any
existing v2 machine state remain untouched. Future behavior may return as
a separately reviewed v3 operation with its own evidence. These review
batches do not override the small implementation batches in the migration plan.

## R1: obsolete or mismatched integrations (4)

| Source outcome | Current coverage | Why retirement is proposed | Reopen only if |
| --- | --- | --- | --- |
| `workstation:package.NautilusHash` | Commented | v2 uses `gtkhash-nautilus`; its own source notes the GNOME 43 break. The [current Fedora GtkHash source](https://packages.fedoraproject.org/pkgs/gtkhash/) lists Caja, Nemo, and Thunar extensions, with no Nautilus subpackage. | A maintained GNOME Files hash integration for the declared target is requested and tested. |
| `workstation:package.NautilusImageTools` | Commented | v2 calls `nautilus-image-converter`; its [Fedora package record](https://packages.fedoraproject.org/pkgs/nautilus-image-converter/nautilus-image-converter/) lists only EPEL 7. Retiring that extension does not reject image resizing; Fedora has a separate [imgp](https://packages.fedoraproject.org/pkgs/imgp/imgp/) CLI. | A current GNOME Files resize integration is requested with compatible package and recovery evidence. |
| `workstation:package.GnomeExtInstaller` | Active | v2 clones the [archived upstream script](https://github.com/brunelli/gnome-shell-extension-installer) and overwrites a system symlink. This retires that helper, while `workstation:package.GnomeExtensions` remains a separate migration decision. | A maintained installer for the declared GNOME target has pinned acquisition and owned rollback. |
| `workstation:package.BitwardenAppImage` | Active | The function labeled AppImage actually downloads an RPM into `~/Applications`; its inverse removes only `Bitwarden*.AppImage`. The separate `workstation:package.Bitwarden` product outcome remains in the keep-or-drop queue. | A real portable Bitwarden artifact and vault-safe lifecycle are requested and verified. |

## R2: unsafe standalone cleanup functions (7)

Each row is a library-only remove path. Retirement removes it from the v3
migration queue as a standalone action. It does not authorize running it on
an existing v2 machine. Historical v2 recovery remains a separate operator
concern; a future v3 inverse must act only on journaled, RIDE-owned state.

| Source outcome | What its v2 function removes or changes | Reopen only if |
| --- | --- | --- |
| `workstation:package.GnomeRegion` | `RemoveGnomeRegion` writes an empty region, not the user's prior value. | It is the exact inverse of an owned GNOME region operation. |
| `workstation:package.CustomKbrdShortcut` | `RemoveCustomKbrdShortcut` clears the complete custom shortcut list and fixed slots, including unowned entries. | It is scoped to shortcuts created and journaled by v3. |
| `workstation:package.VPNProfiles` | `RemoveVPNProfiles` deletes every NetworkManager VPN connection. | It deletes only recorded RIDE-owned UUIDs and preserves unrelated connections. |
| `workstation:package.ExpressVPNProfiles` | `RemoveExpressVPNProfiles` deletes name-matched connections without proving ownership. | It is tied to an accepted client and exact owned UUIDs. |
| `workstation:package.ExpressVPNafterBoot` | `RemoveExpressVPNafterBoot` filters the user crontab by matching text. | An owned timer or schedule has an exact inverse. |
| `workstation:package.ScheduleExpVPNChange` | `RemoveScheduleExpVPNChange` similarly filters matching crontab lines without origin proof. | A future owned randomizer schedule records and restores prior state. |
| `workstation:package.KeyfileMounts` | `RemoveKeyfileMounts` broadly deletes matching crypttab/fstab lines while encrypted volumes remain. | Each encrypted mapping has a named owner, backup, and tested mount/boot recovery. |

## Later individual decisions: keep or drop (38)

These are not proposed for batch retirement. Some v2 installers are obsolete,
but the product or desired behavior may still be useful. Ask whether each
feature is still wanted, which edition or variant, and whether it belongs
in a public opt-in profile or a private workflow. If the answer is no,
prepare an individual retirement reason and review trigger.

### U1a: Optional desktop and portable applications (6)

Choose each product and deployment form before source or handler work.

- `workstation:package.AppImageLauncher` (active; medium risk): v2 selects a mutable beta publisher RPM and creates a user Applications directory without owned AppImage integration or safe inverse.
- `workstation:package.BalenaEtcher` (commented; medium risk): The v2 latest-release scrape is mutable and v3 has no pinned external-RPM acquisition, detection, or inverse handler, despite a current publisher RPM.
- `workstation:package.ArduinoIDE` (commented; medium risk): The v2 latest AppImage scrape and filename-glob inverse lack owned destination and collision handling; no v3 portable handler exists.
- `workstation:package.Discord` (commented; medium risk): The publisher offers a Linux RPM, but v2 has no declared Fedora 44 source and v3 lacks a pinned publisher-RPM or owned Flathub handler.
- `workstation:package.Joplin` (commented; medium risk): The v2 moving AppImage and glob inverse lack file ownership; the publisher script cannot be executed by a default v3 profile, and notebooks belong to the user.
- `workstation:package.Xmind` (commented; medium risk): The v2 old Zen RPM scrape does not identify the current publisher edition or package; its xmind-vana inverse lacks ownership and user-document recovery.

### U1b: Optional browsers, media, and HandBrake (6)

Choose which products and channels are still wanted; no old repository or user profile is silently reused.

- `workstation:package.Vivaldi` (commented; medium risk): Vivaldi supports Fedora 43+, but the v2 scraped RPM and publisher-managed repository/key lack an owned inverse in v3.
- `workstation:package.Chrome` (commented; medium risk): The v2 HTTP Google repository file and name-based inverse have no owned source/key collision contract; v3 has no publisher RPM/repository handler.
- `workstation:package.Opera` (commented; medium risk): The v2 external repository and fixed-key-ID removal can erase pre-existing Opera trust; stable versus developer channel is not selected in v3.
- `workstation:package.Edge` (commented; medium risk): The v2 mutable developer-channel repository and fixed repo-file inverse do not own the Microsoft key or preserve other Microsoft packages.
- `workstation:package.SpotifyClient` (commented; medium risk): The v2 lpf-spotify-client request declares no source; LPF is interactive and a third-party Fedora repackaging is a distinct source with separate terms.
- `workstation:package.HandBrake` (commented; medium risk): The v2 DNF install relies on unaccepted RPM Fusion repository trust; the CLI and GUI RPMs are distinct and no exact-target package happy path was run.

### U1c: Optional development, messaging, vault, and VMware applications (6)

Decide individual demand and edition; a current product does not validate the old installer.

- `workstation:package.PowerShell` (commented; medium risk): The v2 function imports a system Microsoft key and a RHEL 7 repository; current Microsoft RPM guidance does not establish Fedora 44 support or an owned inverse.
- `workstation:package.WoeUSB` (commented; medium risk): Fedora WoeUSB is orphaned and has no Fedora 44 package; the v2 DNF name cannot install on the declared target.
- `workstation:package.Pidgin` (commented; high risk): v2 installs Pidgin and OTR but has no account, key, plugin activation, encrypted-message, or user-data recovery contract.
- `workstation:package.Bitwarden` (commented; high risk): The v2 latest RPM scrape lacks pinned publisher verification and a vault-preserving inverse; no v3 external-RPM handler satisfies the deeper credential/data gate.
- `workstation:package.VMwareWorkstation` (commented; high risk): v2 follows a moving publisher installer redirect and uses host-specific serial data without pinned provenance or full recovery.
- `workstation:action.PatchVMwareModules` (commented; high risk): v2 pulls moving third-party kernel module source, stops service, and lacks module rollback.

### U2a: Forensic tools and the broad Security Lab bundle (5)

Choose a concrete case workflow or bounded tool set before implementation.

- `workstation:package.Plaso` (commented; medium risk): The v2 pair only prints a URL; current Plaso has a broad Python dependency set and no pinned isolated Fedora 44 handler or lifecycle acceptance.
- `workstation:package.Autopsy` (commented; medium risk): The v2 pair only prints a URL; publisher Linux ZIP and Java/Sleuth Kit requirements lack a Linux v3 portable handler and case-data-preserving inverse.
- `workstation:package.BulkExtractor` (commented; high risk): The v2 moving-branch source build writes untracked files to /usr/local, removes shared dependencies, and has no owned inverse or seeded forensic-output recovery evidence.
- `workstation:package.EmailHeaderAnlzr` (commented; high risk): The v2 clone and global pip steps create an unpinned persistent Flask service; service identity, bind scope, unit ownership, and Python/data inverse are unproven.
- `workstation:package.SecurityLab` (commented; medium risk): The Fedora 44 security-lab group has 137 default packages and group state outside the per-package v3 journal; no safe group ownership or inverse is established.

### U2b: Optional Snap, Tailscale, and Selenium roles (3)

Choose a concrete app, tailnet role, or browser automation target before migration.

- `workstation:package.Snap` (commented; high risk): The v2 RPM-only pair does not establish usable Snapd, service/confined operation, or preservation of pre-existing snap apps and data; no high-risk recovery evidence exists.
- `server:package.Tailscale` (library-only; high risk): v2 executes an unpinned remote shell installer without trust, node identity, or inverse.
- `server:package.Selenium` (commented; medium risk): Global unpinned pip install has no isolated environment, browser/driver target, or inverse.

### U3a: Active tuning, profile, codec, and environment choices (6)

Confirm the desired behavior or target first; the v2 implementation is not an accepted v3 method.

- `workstation:setting.FastDNF` (active; medium risk): v2 rewrites administrator DNF config; DNF5 defaults do not reproduce its 15-download tuning and inverse loses prior values.
- `workstation:setting.ChromePreferences` (commented; high risk): v2 overwrites legacy master_preferences and has a broken inverse; Chrome deployment itself remains unowned.
- `workstation:package.Codecs` (commented; high risk): The legacy wildcard installs and optional Multimedia group upgrade have a changing package set and no complete owned inverse; RPM Fusion source trust is also unresolved.
- `workstation:setting.GnomeCustomFavorites` (active; high risk): v2 replaces all user favorites and includes retired Atom desktop ID.
- `workstation:setting.AliasWanIP` (active; high risk): v2 appends three external-DNS aliases and inverse uses a broad line deletion.
- `workstation:package.VMtoolsOnVM` (active; medium risk): The v2 hypervisor branches use inconsistent DMI checks and have no QEMU inverse; the pinned KVM image preinstalls all three guest-tool RPMs, so it cannot establish a RIDE-owned install.

### U3b: Alternate desktop setting variants (6)

Select one desired value or retire the unused variant after checking user intent.

- `workstation:setting.WindowCtlAppmenuClose` (library-only; medium risk): v2 writes one GNOME button-layout string without preserving the arbitrary prior user value.
- `workstation:setting.WindowCtlLeftClsMinMax` (library-only; medium risk): v2 writes another value to the same GNOME button-layout key without conflict or inverse handling.
- `workstation:setting.ScreensaverSlp15Lgn5` (library-only; high risk): v2 library-only lock variant conflicts with the 10-minute choice and has no exact inverse.
- `workstation:setting.VMKeyboardShortcut` (library-only; high risk): v2 VM variant reuses fixed custom-keybinding slots and can overwrite user or workstation bindings.
- `workstation:setting.GnomeMinimalFavorites` (library-only; high risk): v2 replaces the full user favorites list without snapshot or inverse.
- `workstation:setting.PowerPercentageLow20` (library-only; medium risk): The v2 PowerPercentageLow20 behavior lacks owned, exact prior-state recovery required for a runnable setting; see the batch review.

## Later individual decisions: migration design (50)

These source outcomes express behavior that may be retained, but the v2
method cannot be carried forward. The next decision for each is the exact
v3 owner, source or provider, target, state boundary, and recovery. High-risk
storage, encryption, network, and security work stays isolated; grouping
here is for review, not a shared installer or shared safety gate.

### D1a: Trusted repositories and desktop integrations (5)

If retained, choose a verified provider, owned key/repository or extension state, and exact inverse.

- `workstation:package.RPMfusionRepos` (active; high risk): The v2 free/nonfree release-RPM install changes host package trust and its wildcard inverse deletes unowned repositories; v3 has no authenticated ownership-aware repository handler or safety/recovery evidence.
- `workstation:package.Flathub` (active; medium risk): The active v2 remote-add has no owned remote journal and its inverse is not remote-delete; v3 lacks a scoped Flatpak remote handler and app-preserving inverse.
- `workstation:package.VisualStudioCode` (active; medium risk): The official Fedora code RPM requires an owned external repository and signing-key lifecycle; v3 has no handler or exact-target VM recovery, and v2 removes a hard-coded potentially shared key.
- `workstation:package.Brave` (active; medium risk): The official Fedora Brave RPM requires an owned external repository/key lifecycle; v3 has no handler or exact-target VM recovery, and v2 leaves its repository on removal.
- `workstation:package.GnomeExtensions` (active; high risk): The v2 bundle downloads user extensions through a mutable script and removes named user directories without ownership; native management RPMs alone do not reproduce the outcome.

### D1b: Active forensic acquisition and isolation (5)

If retained, choose pinned artifacts or isolated environments and preserve analysis output.

- `workstation:package.ASN` (active; medium risk): The v2 installer fetches an unpinned MIT-licensed script into /usr/bin and removes shared RPM dependencies; v3 has no pinned owned-script handler or safe inverse.
- `workstation:package.UnfURL` (active; medium risk): The v2 installer mutates the user global Python environment with unpinned pip dependencies; v3 has no isolated pinned dfir-unfurl environment or VM happy path.
- `workstation:package.CyberChef` (active; medium risk): The v2 installer selects a mutable GitHub ZIP, extracts into a system path, and writes a desktop launcher without an owned artifact/notice/recovery contract; Linux v3 has no portable handler.
- `workstation:package.Chepy` (active; medium risk): The v2 installer clones an unpinned Git branch, globally installs Python packages and PyInstaller, and copies a built binary into /usr/bin without owned recovery.
- `workstation:package.NetworkMiner` (active; high risk): The active v2 mutable ZIP installer makes captures world writable and its inverse deletes the entire capture/output tree; no Linux owned portable handler or seeded-capture recovery exists.

### D2a: Desktop ownership and policy (6)

Define user or administrator ownership, detection, previous state, and exact recovery.

- `workstation:action.SetupUserDefaultDirs` (active; high risk): v2 chowns pre-existing ~/git and ~/bin and has no ownership-aware inverse.
- `workstation:package.Terminator` (active; high risk): v2 combines a Fedora RPM with a user iBus hotkey; inverse hard-codes a default instead of restoring the prior hotkey.
- `workstation:setting.FirefoxPreferences` (active; high risk): v2 overwrites three Firefox installation files with security and startup preferences and blindly deletes them on inverse.
- `workstation:setting.ScreenSaver` (active; medium risk): v2 sets three lock/idle values without an exact inverse or rollback for partial failure.
- `workstation:setting.WindowCtlMinMaxClose` (active; medium risk): The v2 WindowCtlMinMaxClose behavior lacks owned, exact prior-state recovery required for a runnable setting; see the batch review.
- `workstation:setting.GnomeRegionDaDK` (active; medium risk): The v2 GnomeRegionDaDK behavior lacks owned, exact prior-state recovery required for a runnable setting; see the batch review.

### D2b: Lock, shortcuts, power, and shell settings (5)

Define conflict-safe settings and seeded user-state recovery before a runnable handler.

- `workstation:setting.ScreensaverSlp10Lgn5` (active; high risk): v2 writes four lock and idle GNOME keys without prior values, atomicity, or inverse.
- `workstation:setting.CustomKeyboardShortcut` (active; high risk): v2 replaces the entire GNOME custom-keybindings list and fixed slots, potentially hiding user shortcuts.
- `workstation:setting.PowerPercentageLow15` (active; medium risk): The v2 PowerPercentageLow15 behavior lacks owned, exact prior-state recovery required for a runnable setting; see the batch review.
- `workstation:setting.BashAliases` (active; high risk): v2 appends to .bashrc and inverse deletes all .bash_aliases lines, including user content.
- `workstation:setting.AliasLsEza` (active; high risk): v2 appends ls=eza to .bash_aliases but inverse removes ride-log lines instead.

### D3a: Workstation system lifecycle (5)

Define bounded machine state and inverse; keep service, network, and Docker data safe.

- `workstation:setting.Hostname` (active; medium risk): Interactive v2 hostname has no declared profile value or exact prior-name restore.
- `workstation:action.UpdateFedora` (active; high risk): v2 runs an unbounded system update with no repeat-state observation, transaction inventory, or recovery.
- `workstation:package.Docker` (active; high risk): v2 adds an external repo, installs packages, and starts a service; removal does not preserve repo ownership or container volumes.
- `workstation:package.SmartMonTools` (active; high risk): Fedora RPM installation enabled smartd.service in the disposable VM; the generic package handler cannot recover prior service state.
- `workstation:setting.MulticastDNS` (commented; medium risk): v2 rewrites nsswitch hosts lines without an owned inverse.

### D3b: Server baseline, updates, and host identity (4)

Split broad server behavior by role and maintain the network-devices ownership boundary.

- `server:action.UpdateFedora` (active; high risk): v2 performs a broad DNF update without a bounded planned transaction or rollback.
- `server:package.Required` (active; medium risk): The 11-package v2 bundle mixes VM tools, firewall, Samba, cron, and editors without role ownership or inverse.
- `server:package.AutoUpdate` (active; high risk): v2 enables an update timer and edits administrator DNF config without journaling prior state; its timer edit does not persist.
- `server:setting.Hostname` (active; high risk): Interactive host identity has no declared private value or prior-name recovery.

### D3c: Security and server services (4)

Require service, signature, firewall, SSH, or data recovery before execution.

- `workstation:package.ClamAV` (commented; high risk): v2 runs freshclam after RPM installation; signature database ownership, freshness, failure, and recovery are undefined.
- `server:package.Docker` (active; high risk): External repository, docker group, daemon, images, and volumes have no owned inverse in v2.
- `server:package.Glances` (active; high risk): v2 overwrites /opt/glances and a systemd unit, opens a firewall port, starts a web service, and defines no inverse.
- `server:setting.NoRootLogin` (active; high risk): v2 edits administrator sshd_config in place without backup, syntax check, or inverse.

### D4a: VPN packages, profiles, and credentials (4)

Separate signed packages from private keys, profiles, activation, and unowned connections.

- `workstation:package.Wireguard` (library-only; high risk): v2 creates private keys and inverse recursively deletes /etc/wireguard, including unowned secrets.
- `workstation:package.OpenconnectVPN` (commented; high risk): v2 builds moving Git source into /usr with no provenance or inverse.
- `workstation:action.ImportOpenVPNProfiles` (commented; high risk): v2 imports implicit local .ovpn files and credentials into NetworkManager without owned UUIDs.
- `workstation:package.ExpressVPN` (commented; high risk): v2 scrapes a moving RPM and prompts for activation while inverse leaves account and connection state.

### D4b: Workstation ExpressVPN scheduling (3)

Decide whether scheduling is wanted only after the VPN client and owned script are accepted.

- `workstation:action.StartExpressVPNafterBoot` (commented; high risk): v2 appends an unowned crontab reboot job.
- `workstation:action.CreateExpVPNrandomizer` (commented; high risk): v2 appends executable script text without provenance, idempotence, or inverse.
- `workstation:action.ScheduleRandomExpVPNChange` (library-only; high risk): v2 inserts an unowned recurring crontab job.

### D4c: Privileged policy and Server VPN (5)

Keep principals and secrets private; require owned sudo, key, service, route, and timer recovery.

- `workstation:setting.SSHreboot` (commented; high risk): v2 writes user-specific passwordless sudoers and deletes it without validation or prior ownership.
- `server:action.GenerateSSHkeysRSA` (commented; high risk): v2 interactively generates private keys in user home with weak .ssh directory mode and no existing-key recovery.
- `server:package.ExpressVPN` (active; high risk): Moving publisher RPM URL and activation prompt have no credential, profile, or service inverse.
- `server:action.CreateVPNrandomizer` (active; high risk): v2 appends unverified shell text to /usr/sbin with no bounded selection or inverse.
- `server:setting.VPNRandomizerPersistent` (active; high risk): v2 rewrites crontab with VPN jobs without owned schedule or unrelated-job recovery.

### D5a: Encrypted volumes and destructive disk actions (4)

Review each source outcome individually and implement only in isolated disposable-disk batches with backup and recovery.

- `workstation:package.VeraCrypt` (active; high risk): v2 silently runs a scraped setup script; v3 has no verified publisher-RPM trust handler or seeded encrypted-volume recovery.
- `workstation:action.AddExtraLUKSpasswords` (commented; high risk): v2 adds keys to all detected LUKS devices without explicit target or key-slot journal.
- `workstation:action.EncryptUnpartitionedDisks` (commented; high risk): v2 heuristic disk scan can erase and encrypt a disk without an exact device plan or rollback.
- `workstation:action.ReclaimEncryptDWUnmntPrt` (commented; high risk): v2 heuristic unmounted-partition scan can reclaim data and alter mount/encryption state without inverse.

## Evidence and next action

The source-level reasons and review triggers above are taken from the
checked-in ledger and its linked batch records. The archived GNOME helper
and absent Fedora 44 Nautilus subpackages support R1. An obsolete v2
acquisition method alone is insufficient to retire PowerShell,
[WoeUSB-ng](https://github.com/WoeUSB/WoeUSB-ng),
[AppImageLauncher](https://github.com/TheAssassin/AppImageLauncher), or
another product. No VM session is needed to
approve a non-runnable ledger disposition. After an R1 or R2 approval, update
only the approved rows, regenerate the progress report and burndown, run
ledger/CI checks, and record the approved batch in the migration plan.
Then review the remaining outcomes individually, starting with active v2
selectors and the owner choices in U1-U3.
