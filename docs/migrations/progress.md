# V2 to v3 migration progress

Generated from `migration/outcomes.json`; run `python3 tools/migration_progress.py --summary` for a current CLI view.
Source outcomes are counted separately from catalog operations. A disposition is not a working install.

**8/180 complete (4.4%)**: 6 supported, 0 opt-in candidate, 2 retired, 0 private, 0 unsupported; 172 unresolved.

Replacements with an operable v3 mapping: 0. Owner exclusions: 2 Citrix functions and 13 host-specific server functions, outside the 180 outcomes.

| Batch | Family | Risk | Complete | Evidence | Next action |
| --- | --- | --- | ---: | --- | --- |
| `native-rpm-01` | Fedora CLI packages: pwgen, htop, bat, ncdu, ripgrep, fd | low 6 | 6/6 | [native-rpm-01.md](../../docs/migrations/native-rpm-01.md) | Complete on Fedora 44 Workstation; start native-rpm-02 and recheck this batch if its target or package contract changes. |
| `native-rpm-02` | Native Rpm 02: LibEWF, Exif, Md5deep, Terminator, Alien, SmartMonTools | low 6 | 0/6 | — | Assess LibEWF, Exif, Md5deep, Terminator, Alien, SmartMonTools; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `native-rpm-03` | Native Rpm 03: Hexchat, SpeedtestCLI, Chromium, Cheat, NautilusHash, NautilusImageTools | low 6 | 0/6 | — | Assess Hexchat, SpeedtestCLI, Chromium, Cheat, NautilusHash, NautilusImageTools; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `native-rpm-04` | Native Rpm 04: BulkExtractor, SecurityLab, Dc3dd, Qbittorrent, Pidgin, Thunderbird | low 6 | 0/6 | — | Assess BulkExtractor, SecurityLab, Dc3dd, Qbittorrent, Pidgin, Thunderbird; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `native-rpm-05` | Native Rpm 05: Flameshot, Dia, Wine, VLCPlayer, GIMP, HandBrake | low 6 | 0/6 | — | Assess Flameshot, Dia, Wine, VLCPlayer, GIMP, HandBrake; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `native-rpm-06` | Native Rpm 06: Lynis, ClamAV, KeepassXC, Eza, Libpst | low 5 | 0/5 | — | Assess Lynis, ClamAV, KeepassXC, Eza, Libpst; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `provider-foundation-01` | Provider Foundation 01: Required, ShellTools | medium 2 | 0/2 | — | Assess Required, ShellTools; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `provider-foundation-02` | Provider Foundation 02: RPMfusionRepos | high 1 | 0/1 | — | Assess RPMfusionRepos; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `provider-foundation-03` | Provider Foundation 03: KernelTools, DNFutils, EzaGitHub, Flathub, PythonPip, PackagingTools | medium 6 | 0/6 | — | Assess KernelTools, DNFutils, EzaGitHub, Flathub, PythonPip, PackagingTools; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `provider-foundation-04` | Provider Foundation 04: BasicEditors, GnomeExtInstaller, GnomeTools, VersionLock, Flatpak, Snap | medium 6 | 0/6 | — | Assess BasicEditors, GnomeExtInstaller, GnomeTools, VersionLock, Flatpak, Snap; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `provider-foundation-05` | Provider Foundation 05: Codecs, GnomeRegion, CustomKbrdShortcut | medium 3 | 0/3 | — | Assess Codecs, GnomeRegion, CustomKbrdShortcut; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `forensic-isolated-01` | Forensic Isolated 01: VMFStools, ExifTool, ASN, UnfURL, CyberChef, Chepy | medium 6 | 0/6 | — | Assess VMFStools, ExifTool, ASN, UnfURL, CyberChef, Chepy; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `forensic-isolated-02` | Forensic Isolated 02: NetworkMiner, Plaso, Autopsy, Volatility, Volatility3, EmailHeaderAnlzr | medium 6 | 0/6 | — | Assess NetworkMiner, Plaso, Autopsy, Volatility, Volatility3, EmailHeaderAnlzr; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `forensic-isolated-03` | Forensic Isolated 03: Binwalk, Dumpzilla, PyhtonAutopep8, Macvendor | medium 4 | 0/4 | — | Assess Binwalk, Dumpzilla, PyhtonAutopep8, Macvendor; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-01` | Publisher Apps 01: AppImageLauncher | medium 1 | 0/1 | — | Assess AppImageLauncher; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-02` | Publisher Apps 02: VeraCrypt | high 1 | 0/1 | — | Assess VeraCrypt; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-03` | Publisher Apps 03: VisualStudioCode, Brave | medium 2 | 0/2 | — | Assess VisualStudioCode, Brave; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-04` | Publisher Apps 04: FirefoxAddons | high 1 | 0/1 | — | Assess FirefoxAddons; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-05` | Publisher Apps 05: YouTubeDownloader, SystemMonitor, GnomeExtensions | medium 3 | 0/3 | — | Assess YouTubeDownloader, SystemMonitor, GnomeExtensions; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-06` | Publisher Apps 06: BitwardenAppImage | high 1 | 0/1 | — | Assess BitwardenAppImage; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-07` | Publisher Apps 07: UnifyingOnLaptop, VMtoolsOnVM | medium 2 | 0/2 | — | Assess UnifyingOnLaptop, VMtoolsOnVM; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-08` | Publisher Apps 08: YubikeyManager | high 1 | 0/1 | — | Assess YubikeyManager; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-09` | Publisher Apps 09: SonosPlayer, CommanderFileMgrs, PowerShell, MicrosoftTeams, WoeUSB, BalenaEtcher | medium 6 | 0/6 | — | Assess SonosPlayer, CommanderFileMgrs, PowerShell, MicrosoftTeams, WoeUSB, BalenaEtcher; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-10` | Publisher Apps 10: ArduinoIDE, AtomEditor, AtomPlugins, Discord, Joplin, Vivaldi | medium 6 | 0/6 | — | Assess ArduinoIDE, AtomEditor, AtomPlugins, Discord, Joplin, Vivaldi; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-11` | Publisher Apps 11: Chrome, Opera, Edge, SpotifyClient, ClementinePlayer, PulseAudioEq | medium 6 | 0/6 | — | Assess Chrome, Opera, Edge, SpotifyClient, ClementinePlayer, PulseAudioEq; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-12` | Publisher Apps 12: Bitwarden | high 1 | 0/1 | — | Assess Bitwarden; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-13` | Publisher Apps 13: Projecteur | medium 1 | 0/1 | — | Assess Projecteur; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-14` | Publisher Apps 14: YubikeyPersTool | high 1 | 0/1 | — | Assess YubikeyPersTool; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `publisher-apps-15` | Publisher Apps 15: Xmind | medium 1 | 0/1 | — | Assess Xmind; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `desktop-user-01` | Desktop and user state 01: SetupUserDefaultDirs, FirefoxPreferences | high 2 | 0/2 | — | Assess SetupUserDefaultDirs, FirefoxPreferences; record user-owned data, exact prior state, inverse, and VM criteria. |
| `desktop-user-02` | Desktop and user state 02: DateInTaskbar, WeekNumbersInTaskbar, WindowCtlMinMaxClose, MiddleButtonPaste, GnomeRegionDaDK, ScreensaverSlp10Lgn5 | medium 6 | 0/6 | — | Assess DateInTaskbar, WeekNumbersInTaskbar, WindowCtlMinMaxClose, MiddleButtonPaste, GnomeRegionDaDK, ScreensaverSlp10Lgn5; record user-owned data, exact prior state, inverse, and VM criteria. |
| `desktop-user-03` | Desktop and user state 03: CustomKeyboardShortcut, GnomeCustomFavorites | high 2 | 0/2 | — | Assess CustomKeyboardShortcut, GnomeCustomFavorites; record user-owned data, exact prior state, inverse, and VM criteria. |
| `desktop-user-04` | Desktop and user state 04: GnmLocationServiceOff, GnmAutoProblemRptOff, PowerPercentageLow15 | medium 3 | 0/3 | — | Assess GnmLocationServiceOff, GnmAutoProblemRptOff, PowerPercentageLow15; record user-owned data, exact prior state, inverse, and VM criteria. |
| `desktop-user-05` | Desktop and user state 05: BashAliases, AliasLsEza, AliasWanIP, ChromePreferences, AliasRideLog, CheckFirefoxAddons | high 6 | 0/6 | — | Assess BashAliases, AliasLsEza, AliasWanIP, ChromePreferences, AliasRideLog, CheckFirefoxAddons; record user-owned data, exact prior state, inverse, and VM criteria. |
| `desktop-user-06` | Desktop and user state 06: FinalizeFirefoxAddonRemoval | high 1 | 0/1 | — | Assess FinalizeFirefoxAddonRemoval; record user-owned data, exact prior state, inverse, and VM criteria. |
| `desktop-user-07` | Desktop and user state 07: WindowCtlAppmenuClose, WindowCtlLeftClsMinMax, ScreensaverSlp15Lgn5 | medium 3 | 0/3 | — | Assess WindowCtlAppmenuClose, WindowCtlLeftClsMinMax, ScreensaverSlp15Lgn5; record user-owned data, exact prior state, inverse, and VM criteria. |
| `desktop-user-08` | Desktop and user state 08: VMKeyboardShortcut, GnomeDefaultFavorites, GnomeMinimalFavorites | high 3 | 0/3 | — | Assess VMKeyboardShortcut, GnomeDefaultFavorites, GnomeMinimalFavorites; record user-owned data, exact prior state, inverse, and VM criteria. |
| `desktop-user-09` | Desktop and user state 09: GnmLocationServiceOn, GnmAutoProblemRptOn, PowerPercentageLow20 | medium 3 | 0/3 | — | Assess GnmLocationServiceOn, GnmAutoProblemRptOn, PowerPercentageLow20; record user-owned data, exact prior state, inverse, and VM criteria. |
| `system-security-01` | System Security 01: Hostname, FastDNF | medium 2 | 0/2 | — | Assess Hostname, FastDNF; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-02` | System Security 02: UpdateFedora | high 1 | 0/1 | — | Assess UpdateFedora; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-03` | System Security 03: Docker | high 1 | 0/1 | — | Assess Docker; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-04` | System Security 04: NetworkTools, NetCommsTools | medium 2 | 0/2 | — | Assess NetworkTools, NetCommsTools; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-05` | System Security 05: NetMgrLibreswan | high 1 | 0/1 | — | Assess NetMgrLibreswan; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-06` | System Security 06: MulticastDNS | medium 1 | 0/1 | — | Assess MulticastDNS; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-07` | System Security 07: NetMgrL2TP | high 1 | 0/1 | — | Assess NetMgrL2TP; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-08` | System Security 08: OpenconnectVPN | high 1 | 0/1 | — | Assess OpenconnectVPN; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-09` | System Security 09: ImportOpenVPNProfiles | high 1 | 0/1 | — | Assess ImportOpenVPNProfiles; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-10` | System Security 10: ExpressVPN | high 1 | 0/1 | — | Assess ExpressVPN; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-11` | System Security 11: StartExpressVPNafterBoot | high 1 | 0/1 | — | Assess StartExpressVPNafterBoot; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-12` | System Security 12: CreateExpVPNrandomizer | high 1 | 0/1 | — | Assess CreateExpVPNrandomizer; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-13` | System Security 13: VMwareWorkstation | high 1 | 0/1 | — | Assess VMwareWorkstation; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-14` | System Security 14: PatchVMwareModules | high 1 | 0/1 | — | Assess PatchVMwareModules; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-15` | System Security 15: AddExtraLUKSpasswords | high 1 | 0/1 | — | Assess AddExtraLUKSpasswords; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-16` | System Security 16: EncryptUnpartitionedDisks | high 1 | 0/1 | — | Assess EncryptUnpartitionedDisks; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-17` | System Security 17: ReclaimEncryptDWUnmntPrt | high 1 | 0/1 | — | Assess ReclaimEncryptDWUnmntPrt; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-18` | System Security 18: SSHreboot | high 1 | 0/1 | — | Assess SSHreboot; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-19` | System Security 19: Wireguard | high 1 | 0/1 | — | Assess Wireguard; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-20` | System Security 20: VPNProfiles | high 1 | 0/1 | — | Assess VPNProfiles; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-21` | System Security 21: ExpressVPNProfiles | high 1 | 0/1 | — | Assess ExpressVPNProfiles; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-22` | System Security 22: ExpressVPNafterBoot | high 1 | 0/1 | — | Assess ExpressVPNafterBoot; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-23` | System Security 23: ScheduleRandomExpVPNChange | high 1 | 0/1 | — | Assess ScheduleRandomExpVPNChange; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-24` | System Security 24: ScheduleExpVPNChange | high 1 | 0/1 | — | Assess ScheduleExpVPNChange; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `system-security-25` | System Security 25: KeyfileMounts | high 1 | 0/1 | — | Assess KeyfileMounts; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-01` | Generic Server 01: UpdateFedora | high 1 | 0/1 | — | Assess UpdateFedora; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-02` | Generic Server 02: Required | medium 1 | 0/1 | — | Assess Required; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-03` | Generic Server 03: AutoUpdate | high 1 | 0/1 | — | Assess AutoUpdate; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-04` | Generic Server 04: ViewIPaddress | medium 1 | 1/1 | [resolution-decisions.md](../../docs/migrations/resolution-decisions.md) | Closed as information-only behavior; reopen only if a v3 IP discovery view is requested. |
| `generic-server-05` | Generic Server 05: Hostname | high 1 | 0/1 | — | Assess Hostname; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-06` | Generic Server 06: Docker | high 1 | 0/1 | — | Assess Docker; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-07` | Generic Server 07: Glances | medium 1 | 0/1 | — | Assess Glances; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-08` | Generic Server 08: NoRootLogin | high 1 | 0/1 | — | Assess NoRootLogin; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-09` | Generic Server 09: ExpressVPN | high 1 | 0/1 | — | Assess ExpressVPN; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-10` | Generic Server 10: CreateVPNrandomizer | high 1 | 0/1 | — | Assess CreateVPNrandomizer; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-11` | Generic Server 11: VPNRandomizerPersistent | high 1 | 0/1 | — | Assess VPNRandomizerPersistent; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-12` | Generic Server 12: PythonPip, Selenium | medium 2 | 0/2 | — | Assess PythonPip, Selenium; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-13` | Generic Server 13: GenerateSSHkeysRSA | high 1 | 0/1 | — | Assess GenerateSSHkeysRSA; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `generic-server-14` | Generic Server 14: Tailscale | high 1 | 0/1 | — | Assess Tailscale; record v2 behavior, current source, inverse, and risk-based completion criteria. |
| `resolution-review-01` | Resolution Review 01: TecmintMonitorSh, ScreenSaver, Screensaver, Galleta, Xplico, AtomTelemetry | medium 6 | 1/6 | [resolution-decisions.md](../../docs/migrations/resolution-decisions.md) | Review the remaining stub and conflicting setting outcomes; TecmintMonitorSh is retired. |

## v3.1 hardening queue

These items do not replace v3.0 safety checks for data, storage, encryption, or security behavior.

| ID | Item | Trigger | Status |
| --- | --- | --- | --- |
| `H001` | Broader Fedora target coverage | After v3.0 target matrix is accepted | queued |
| `H002` | Extended failure and recovery matrix for opt-in candidate applications | After each candidate has its v3.0 happy-path evidence | queued |
| `H003` | Desktop visual and accessibility review | After desktop operations are operable in disposable Workstation VMs | queued |
| `H004` | Retained artifact offline installation and provider fallback | After artifact provenance and dependency behavior are designed | queued |
