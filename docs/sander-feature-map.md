# Sander feature map

Source: [sanderu/bootstrap `ride-functions.sh` at 3831965](https://github.com/sanderu/bootstrap/blob/383196551bc24ee89d869d3698ee43adfd5d1f07/ride-functions.sh). This inventory records 185 function definitions. The author has communicated MIT intent; no source code is copied here. An exact legacy name is only a search lead, not a claim of equivalent behavior.

Status is a v3 disposition: **implemented candidate** means cataloged but not VM-certified; **deferred** means no executable v3 operation; **not ported** means the original behavior should not be copied; **out of scope** means the owner excluded the product. The 25 active Sander preset entries are marked `yes`.

| Section | Sander function | Active | Existing exact name | v3 target / disposition |
| --- | --- | --- | --- | --- |
| Generic Debian | `UpdateDebian` | yes | none | deferred: legacy UpdateFedora; future apt adapter |
| Generic Debian | `InstallRequired` | yes | Fedora legacy | deferred: compare legacy behavior before migration |
| Generic Debian | `InstallChipDependant` | yes | none | not ported: Fedora-native policy or unsafe CPU inference |
| Generic Debian | `InstallShellTools` | yes | Fedora legacy | deferred: compare legacy behavior before migration |
| Generic Debian | `RemoveShellTools` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Generic Debian | `InstallKernelTools` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Generic Debian | `RemoveKernelTools` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Generic Debian | `InstallXserver` | yes | none | deferred: outside focused v3 scope |
| Generic Debian | `RemoveXserver` | no | none | deferred: outside focused v3 scope |
| Generic Debian | `InstallXscreensaver` | yes | none | deferred: outside focused v3 scope |
| Generic Debian | `RemoveXscreensaver` | no | none | deferred: outside focused v3 scope |
| Generic Debian | `InstallAwesome` | yes | none | deferred: outside focused v3 scope |
| Generic Debian | `RemoveAwesome` | no | none | deferred: outside focused v3 scope |
| Generic Debian | `InstallI3` | no | none | deferred: outside focused v3 scope |
| Generic Debian | `RemoveI3` | no | none | deferred: outside focused v3 scope |
| Basic Tools and support | `InstallExfatSupport` | yes | none | implemented candidate: package.exfatprogs |
| Basic Tools and support | `RemoveExfatSupport` | no | none | implemented candidate: package.exfatprogs |
| Basic Tools and support | `InstallPackagingTools` | yes | Fedora legacy | deferred: compare legacy behavior before migration |
| Basic Tools and support | `RemovePackagingTools` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Basic Tools and support | `InstallBasicEditor` | yes | none | deferred: legacy InstallBasicEditors |
| Basic Tools and support | `RemoveBasicEditor` | no | none | deferred: legacy RemoveBasicEditors |
| Basic Tools and support | `InstallPythonTools` | yes | none | deferred: legacy InstallPythonPip; replace global pip |
| Basic Tools and support | `RemovePythonTools` | no | none | deferred: legacy RemovePythonPip |
| Basic Tools and support | `InstallTerminator` | yes | Fedora legacy | deferred: compare legacy behavior before migration |
| Basic Tools and support | `RemoveTerminator` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Basic Tools and support | `InstallLess` | yes | none | implemented candidate: package.less |
| Basic Tools and support | `RemoveLess` | no | none | implemented candidate: package.less |
| Basic Tools and support | `InstallHexEditor` | no | none | deferred: outside focused v3 scope |
| Basic Tools and support | `RemoveHexEditor` | no | none | deferred: outside focused v3 scope |
| Basic Tools and support | `InstallHexwalk` | yes | none | deferred: outside focused v3 scope |
| Basic Tools and support | `RemoveHexwalk` | no | none | deferred: outside focused v3 scope |
| Basic Tools and support | `InstallImHex` | yes | none | implemented candidate: package.imhex |
| Basic Tools and support | `RemoveImHex` | no | none | implemented candidate: package.imhex |
| Database | `InstallPostgreSQLServer` | no | none | deferred: outside focused v3 scope |
| Database | `RemovePostgreSQLServer` | no | none | deferred: outside focused v3 scope |
| Database | `InstallPostgreSQLClient` | no | none | deferred: outside focused v3 scope |
| Database | `RemovePostgreSQLClient` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `InstallForensicImageTools` | no | none | implemented candidate: package.ewftools + package.sleuthkit |
| Forensic tools | `RemoveForensicImageTools` | no | none | implemented candidate: package.ewftools + package.sleuthkit |
| Forensic tools | `InstallImagingTools` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `RemoveImagingTools` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `InstallExifTool` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Forensic tools | `RemoveExifTool` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Forensic tools | `InstallRecoverTools` | no | none | implemented candidate: package.testdisk |
| Forensic tools | `RemoveRecoverTools` | no | none | implemented candidate: package.testdisk |
| Forensic tools | `InstallYara` | no | none | implemented candidate: package.yara |
| Forensic tools | `RemoveYara` | no | none | implemented candidate: package.yara |
| Forensic tools | `InstallPlaso` | no | Fedora legacy | deferred candidate: Plaso |
| Forensic tools | `RemovePlaso` | no | Fedora legacy | deferred candidate: Plaso |
| Forensic tools | `InstallAutopsy` | no | Fedora legacy | deferred candidate: Autopsy |
| Forensic tools | `RemoveAutopsy` | no | Fedora legacy | deferred candidate: Autopsy |
| Forensic tools | `InstallWindowsForensicTools` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `RemoveWindowsForensicTools` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `InstallBMCTools` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `RemoveBMCTools` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `InstallVolatility3` | no | Fedora legacy | implemented candidate: isolated package.volatility3 core |
| Forensic tools | `RemoveVolatility3` | no | Fedora legacy | implemented candidate: package.volatility3 owned environment removal; legacy removal targeted unrelated file |
| Forensic tools | `InstallUAC` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `RemoveUAC` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `InstallRegistrySpy` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `RemoveRegistrySpy` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `InstallAuroraIR` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `RemoveAuroraIR` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `InstallKanvasIR` | no | none | deferred: outside focused v3 scope |
| Forensic tools | `RemoveKanvasIR` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `InstallGhidra` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Reverse Engineering tools | `RemoveGhidra` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Reverse Engineering tools | `InstallCutter` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `RemoveCutter` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `InstallMalcat` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `RemoveMalcat` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `InstallRadare2` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `RemoveRadare2` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `InstallIaito` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `RemoveIaito` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `InstallEDBDebugger` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `RemoveEDBDebugger` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `InstallCapa` | no | none | partial candidate: artifact.capa-linux downloads verified archive only; installation deferred |
| Reverse Engineering tools | `RemoveCapa` | no | none | deferred: download-only artifact has no installed state to remove |
| Reverse Engineering tools | `InstallFLOSS` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `RemoveFLOSS` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `InstallDIE` | no | none | deferred: outside focused v3 scope |
| Reverse Engineering tools | `RemoveDIE` | no | none | deferred: outside focused v3 scope |
| CTF / Pentest tools | `InstallBurp` | no | none | deferred: outside focused v3 scope |
| CTF / Pentest tools | `RemoveBurp` | no | none | deferred: outside focused v3 scope |
| CTF / Pentest tools | `InstallStegSeek` | no | none | deferred: outside focused v3 scope |
| CTF / Pentest tools | `RemoveStegSeek` | no | none | deferred: outside focused v3 scope |
| Programming Tools | `InstallVisualStudioCode` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Programming Tools | `RemoveVisualStudioCode` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Communication | `InstallChatProgs` | no | none | deferred: outside focused v3 scope |
| Communication | `RemoveChatProgs` | no | none | deferred: outside focused v3 scope |
| Communication | `InstallSignal` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Communication | `RemoveSignal` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Communication | `InstallSlack` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Communication | `RemoveSlack` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Communication | `InstallDiscord` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Communication | `RemoveDiscord` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Communication | `InstallEmailProgs` | no | none | deferred: outside focused v3 scope |
| Communication | `RemoveEmailProgs` | no | none | deferred: outside focused v3 scope |
| NetworkConfiguration | `EnableMulticastDNS` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| NetworkConfiguration | `DisableMulticastDNS` | yes | Fedora legacy | deferred: compare legacy behavior before migration |
| NetworkConfiguration | `InstallNetworkTools` | yes | Fedora legacy | deferred: compare legacy behavior before migration |
| NetworkConfiguration | `RemoveNetworkTools` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| NetworkConfiguration | `InstallNetCommsTools` | yes | Fedora legacy | deferred: compare legacy behavior before migration |
| NetworkConfiguration | `RemoveNetCommsTools` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| NetworkConfiguration | `InstallWindowsNetCommsTools` | no | none | deferred: outside focused v3 scope |
| NetworkConfiguration | `RemoveWindowsNetCommsTools` | no | none | deferred: outside focused v3 scope |
| NetworkConfiguration | `InstallOpenconnectVPN` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| NetworkConfiguration | `RemoveOpenconnectVPN` | no | none | deferred: outside focused v3 scope |
| NetworkConfiguration | `InstallSSHserver` | no | none | deferred: outside focused v3 scope |
| NetworkConfiguration | `RemoveSSHserver` | no | none | deferred: outside focused v3 scope |
| NetworkConfiguration | `InstallSSHclient` | yes | none | implemented candidate: package.openssh-clients |
| NetworkConfiguration | `RemoveSSHclient` | no | none | implemented candidate: package.openssh-clients |
| NetworkConfiguration | `InstallOpenVPN` | no | none | deferred: outside focused v3 scope |
| NetworkConfiguration | `RemoveOpenVPN` | no | none | deferred: outside focused v3 scope |
| NetworkConfiguration | `InstallWireGuard` | no | none | deferred: outside focused v3 scope |
| NetworkConfiguration | `RemoveWireGuard` | no | none | deferred: outside focused v3 scope |
| Productivity Tools | `InstallDia` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Productivity Tools | `RemoveDia` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Productivity Tools | `InstallWine` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Productivity Tools | `RemoveWine` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Productivity Tools | `InstallLibreOffice` | no | none | deferred: outside focused v3 scope |
| Productivity Tools | `RemoveLibreOffice` | no | none | deferred: outside focused v3 scope |
| Productivity Tools | `InstallJupyter` | no | none | deferred: outside focused v3 scope |
| Productivity Tools | `RemoveJupyter` | no | none | deferred: outside focused v3 scope |
| Productivity Tools | `InstallObsidian` | no | none | deferred: outside focused v3 scope |
| Productivity Tools | `RemoveObsidian` | no | none | deferred: outside focused v3 scope |
| Supporting scripts | `InstallTecmintMonitorSh` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `RemoveTecmintMonitorSh` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `InstallMozExtensionMgr` | yes | none | deferred: existing Firefox policy helper |
| Supporting scripts | `RemoveMozExtensionMgr` | no | none | deferred: existing Firefox policy helper |
| Supporting scripts | `InstallChromium` | yes | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `RemoveChromium` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `InstallFirefoxESR` | yes | none | deferred: outside focused v3 scope |
| Supporting scripts | `RemoveFirefoxESR` | no | none | deferred: outside focused v3 scope |
| Supporting scripts | `SetFirefoxESRPreferences` | yes | none | deferred: legacy SetFirefoxPreferences (not equivalent) |
| Supporting scripts | `UnsetFirefoxESRPreferences` | no | none | deferred: legacy UnsetFirefoxPreferences (not equivalent) |
| Supporting scripts | `InstallFirefoxLatest` | no | none | deferred: outside focused v3 scope |
| Supporting scripts | `RemoveFirefoxLatest` | no | none | deferred: outside focused v3 scope |
| Supporting scripts | `InstallOpera` | no | Fedora legacy | out of scope: owner-excluded Opera |
| Supporting scripts | `RemoveOpera` | no | Fedora legacy | out of scope: owner-excluded Opera |
| Supporting scripts | `InstallVivaldi` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `RemoveVivaldi` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `InstallSpotifyClient` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `RemoveSpotifyClient` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `InstallVLCPlayer` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `RemoveVLCPlayer` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `InstallAudaciousPlayer` | no | none | deferred: outside focused v3 scope |
| Supporting scripts | `RemoveAudaciousPlayer` | no | none | deferred: outside focused v3 scope |
| Supporting scripts | `InstallAudacity` | no | none | deferred: outside focused v3 scope |
| Supporting scripts | `RemoveAudacity` | no | none | deferred: outside focused v3 scope |
| Supporting scripts | `InstallClementinePlayer` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `RemoveClementinePlayer` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `InstallPulseAudioEq` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `RemovePulseAudioEq` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `InstallYouTubeDownloader` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `RemoveYouTubeDownloader` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `InstallGIMP` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `RemoveGIMP` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `InstallHandBrake` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Supporting scripts | `RemoveHandBrake` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Miscellaneous tweaks and installs | `InstallQemuKVM` | no | none | deferred: outside focused v3 scope |
| Miscellaneous tweaks and installs | `RemoveQemuKVM` | no | none | deferred: outside focused v3 scope |
| Miscellaneous tweaks and installs | `InstallVMtoolsOnVM` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Miscellaneous tweaks and installs | `RemoveVMtoolsOnVM` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| 3rd party applications | `InstallPowerShell` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| 3rd party applications | `RemovePowerShell` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Security related | `InstallKeepassXC` | yes | Fedora legacy | deferred: compare legacy behavior before migration |
| Security related | `RemoveKeepassXC` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Security related | `InstallAIDE` | no | none | deferred: outside focused v3 scope |
| Security related | `RemoveAIDE` | no | none | deferred: outside focused v3 scope |
| Security related | `InstallClamAV` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Security related | `RemoveClamAV` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Security related | `InstallRootkitCheckers` | no | none | deferred: outside focused v3 scope |
| Security related | `RemoveRootkitCheckers` | no | none | deferred: outside focused v3 scope |
| Security related | `InstallLynis` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Security related | `RemoveLynis` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Security related | `InstallAuditd` | yes | none | implemented candidate: package.audit + setting.auditd-enabled |
| Security related | `RemoveAuditd` | no | none | implemented candidate: package.audit + setting.auditd-enabled |
| Security related | `InstallSELinux` | no | none | not ported: Fedora-native policy or unsafe CPU inference |
| Security related | `RemoveSELinux` | no | none | not ported: Fedora-native policy or unsafe CPU inference |
| Encryption Functions | `AddExtraLUKSpasswords` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Encryption Functions | `EncryptUnpartitionedDisks` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Encryption Functions | `ReclaimEncryptDWUnmntPrt` | no | Fedora legacy | deferred: compare legacy behavior before migration |
| Encryption Functions | `RemoveKeyfileMounts` | no | Fedora legacy | deferred: compare legacy behavior before migration |

## Review priorities

1. Complete repository-backed DFIR packages and the isolated Volatility3 handler before promoting the forensics profile.
2. Evaluate Plaso's opt-in GIFT COPR and Autopsy's upstream Linux setup in disposable Fedora VMs; otherwise retain non-executable candidates.
3. Review optional reverse-engineering, VPN, database, KVM and alternative desktop families after the core lifecycle is accepted.
4. Keep Firefox ESR and X11/Awesome choices out of Fedora's default profile. Review named overlaps such as ExifTool and Ghidra for source and behavior differences.
