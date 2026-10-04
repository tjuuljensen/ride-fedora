# bootstrap installation
Bootstrap installation of fedora system.  
Can be initated using these commands:
```
$ wget https://tjuuljensen.github.io/ride-fedora/ -O bootstrap.sh
$ chmod +x bootstrap.sh
$ ./bootstrap.sh --default
```
...or just use the one-liner:  
```
$ wget https://tjuuljensen.github.io/ride-fedora/ -O bootstrap.sh && chmod +x bootstrap.sh && ./bootstrap.sh  --default
```

This way the one-liner will allow you to customize your install by *editing* the preset file before installing:  
```
$ wget https://tjuuljensen.github.io/ride-fedora/ -O bootstrap.sh && chmod +x bootstrap.sh && ./bootstrap.sh --edit
```

You can also *halt the installation* process when the source has been downloaded.
The source will be left in a subdirectory to current directory:
```
$ wget https://tjuuljensen.github.io/ride-fedora/ -O bootstrap.sh && chmod +x bootstrap.sh && ./bootstrap.sh --stop
```

The bootstrap installer also accepts the full input for the ride.sh script.
Everything after --ride will be parsed to the ride installer.
```
$ ./bootstrap.sh --ride --help
```

### Optional loading of variables
usage: `bootstrap.sh --ride --include lib-fedora.sh --include serialnumbers.config --preset default.preset actionFunction1 actionFunction2`

### Firefox extensions

Firefox extensions are managed through Firefox's native system policy rather
than by modifying a user profile. The desired extension IDs and Mozilla
Add-ons slugs are stored in `policies/firefox-extensions.json`.

Validate the manifest, current AMO metadata, download hashes, and XPI files:

```bash
./ride.sh --include lib-fedora.sh CheckFirefoxAddons
```

`InstallFirefoxAddons` performs the same online validation before atomically
merging RIDE-owned entries into `/etc/firefox/policies/policies.json`. It
preserves unrelated Firefox policies, refuses conflicting unmanaged extension
entries, and backs up an existing policy before changing it. Firefox applies
the extension policy on its next start.

```bash
sudo ./ride.sh --include lib-fedora.sh InstallFirefoxAddons
```

Removal is deliberately a two-step operation. The first action changes only
the RIDE-owned entries to `blocked`; Firefox then uninstalls those extensions
the next time it starts. After verifying the removal in Firefox, the finalize
action removes the temporary policy tombstones and RIDE state:

```bash
sudo ./ride.sh --include lib-fedora.sh RemoveFirefoxAddons
# Restart Firefox and verify that the extensions are gone.
sudo ./ride.sh --include lib-fedora.sh FinalizeFirefoxAddonRemoval
```

Ownership state is stored in
`/var/lib/ride-fedora/firefox-extensions.json`. Firefox will identify itself as
managed while system policy is present. The legacy `ubuntu-scripts` profile
installer and the obsolete, disabled Thunderbird extension list are no longer
used.

### FAQ
**Q:** What is an action?  
**A:** An action is a name of one of the functions referenced in either one of the included file  

**Q:** The preset function could easily have been included the same way as the function libraries. Why not source everything?  
**A:** For readability purposes, I have chosen this solution because it is easy to see which functions are mutually connected.  

**Q:** Are there dependencies between actions?  
**A:** I have strived to keep each action atomic, having no dependencies to other actions. A few exclusions apply though; 1) rpmfusion repos are required for a lot of the installations 2) CERT Forensic repo is required for all functions in that section.
