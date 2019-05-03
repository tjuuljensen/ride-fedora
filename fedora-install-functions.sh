#!/bin/sh
# script will automatically escalate to root privileges. Do not run as root
# last edited: April 16, 2019 11:32

MYUSER=$(logname)
DOWNLOADDIR=/home/$MYUSER/Downloads
FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number


################################################################
###### Require administrator privileges
################################################################

RequireAdmin(){
    # check if script is root and restart as root if not
    [ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"
}

################################################################
###### Auxiliary Functions  ###
################################################################

EnableScreenSaver(){
  # enable screensaver
  su $MYUSER -c "gsettings set org.gnome.desktop.screensaver idle-activation-enabled 'true'"
  su $MYUSER -c "gsettings set org.gnome.desktop.screensaver lock-enabled 'true'"
  su $MYUSER -c "gsettings set org.gnome.desktop.session idle-delay 300"
}

DisableScreensaver(){
  # disable screensaver
  su $MYUSER -c "gsettings set org.gnome.desktop.screensaver idle-activation-enabled 'false'"
  su $MYUSER -c "gsettings set org.gnome.desktop.screensaver lock-enabled 'false'"
  su $MYUSER -c "gsettings set org.gnome.desktop.session idle-delay 0"
}

Restart(){
  echo Rebooting now...
  reboot now
}

SetHostname(){
  # set hostname
  echo
  echo Current hostname is $HOSTNAME
  read -r -p "Enter NEW hostname (or <Enter> to continue unchanged): " NEWHOSTNAME
  if [ ! -z $NEWHOSTNAME ] ; then
    hostnamectl set-hostname --static "$NEWHOSTNAME"
  fi
}

################################################################
###### Generic Fedora ###
################################################################

UpdateFedora(){
  # update fedora
  dnf update -y
}

InstallRequired(){
  REQUIREDPACKAGES=("coreutils" "git" "gnupg" "python" "ssh" "tar" "wget" "gcc")
  for i in ${!REQUIREDPACKAGES[@]};
  do
    rpm -q --quiet ${REQUIREDPACKAGES[$i]}  || dnf install -y ${REQUIREDPACKAGES[$i]}
  done
}

InstallMiscTools(){
  dnf install -y pv
}

RemoveMiscTools(){
  dnf remove -y pv
}

InstallRPMfusionRepos(){
  FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number
  RPMFUSIONURL=http://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$FEDORARELEASE.noarch.rpm
  RPMFUSIONNONFREEURL=https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$FEDORARELEASE.noarch.rpm
  # install rpmfusion
  dnf install -y $RPMFUSIONURL
  dnf install -y $RPMFUSIONNONFREEURL
}

RemoveRPMfusionRepos(){
  # Remove rpmfusion
  # See more here (old article): https://www.if-not-true-then-false.com/2010/yum-remove-repo-repository-yum-disable-repo-repository/
  # Find repolist names: dnf repolist | grep rpmfusion | cut -d ' ' -f1 | sed 's/*//g'

  # Remove repo files
  find /etc/yum.repos.d/rpmfusion* -print -delete 2>/dev/null
  # RPM list
  rpm -qa | grep -i rpmfusion | xargs dnf remove -y
}

InstallKernelTools(){
  dnf install -y kernel-devel kernel-headers
}

RemoveKernelTools(){
  dnf remove -y kernel-devel kernel-headers
}

InstallFedy(){
  # Depends on rpmfusion
  # From https://www.folkswithhats.org/
  dnf install https://dl.folkswithhats.org/fedora/$(rpm -E %fedora)/RPMS/fedy-release.rpm
  dnf install $RPMFUSIONURL $RPMFUSIONNONFREEURL
  dnf install fedy
}

RemoveFedy(){
  # Installing fedy
  # From https://www.folkswithhats.org/

  # Remove repo
  REPONAME=$(dnf -q repolist | grep -i fedy | cut -d ' ' -f1 | sed 's/*//g' | awk 'NR==1' )
  rm  /etc/yum.repos.d/$REPONAME.repo

  # remove RPM
  dnf remove -y fedy-release
  dnf remove -y fedy
}


################################################################
###### Forensic Tools ###
################################################################

InstallForensicImageTools(){
  # install libewf - a library for access to EWF (Expert Witness Format)
  # See more at https://github.com/libyal/libewf
  # sleuthkit - https://www.sleuthkit.org/sleuthkit/
  dnf install -y libewf sleuthkit
}

RemoveForensicImageTools(){
  dnf remove -y libewf sleuthkit
}

InstallFTKImager(){
  FTKURL=https://ad-zip.s3.amazonaws.com/ftkimager.3.1.1_fedora64.tar.gz
  FTKPKG=${FTKURL##${FTKURL%/*}"/"}

  # download ftkimager from AccessSoftware and put it in /usr/bin
  wget $FTKURL
  tar xzvf $FTKPKG -C /usr/bin/
  chown $MYUSER:$MYUSER $FTKPKG
}

RemoveFTKImager(){
  rm /usr/bin/ftkimager
}

InstallExifTool(){
  # ExitTool - http://owl.phy.queensu.ca/~phil/exiftool/
  dnf install -y perl-Image-ExifTool
}

InstallExifTool(){
  # ExitTool - http://owl.phy.queensu.ca/~phil/exiftool/
  dnf remove -y perl-Image-ExifTool
}

################################################################
###### Basic Tools and Support ###
################################################################

InstallExfatSupport(){
  # install exfat utils (depends on RPMfusion)
  dnf install -y exfat-utils fuse-exfat
}

RemoveExfatSupport(){
  # install exfat utils (depends on RPMfusion)
  dnf remove -y exfat-utils fuse-exfat
}

InstallPackagingTools(){
  # install 7zip and dependencies
  dnf install -y p7zip unrar
}

RemovePackagingTools(){
  # install 7zip and dependencies
  dnf remove -y p7zip unrar
}

InstallAtomEditor(){
  #Install atom repo
  # See more here https://flight-manual.atom.io/getting-started/sections/installing-atom/#platform-linux
  #
  rpm --import https://packagecloud.io/AtomEditor/atom/gpgkey

  # Make repo file
  ATOMREPO=/etc/yum.repos.d/atom.repo
  echo -e '[Atom]
name=Atom Editor
baseurl=https://packagecloud.io/AtomEditor/atom/el/7/$basearch
enabled=1
gpgcheck=0
repo_gpgcheck=1
gpgkey=https://packagecloud.io/AtomEditor/atom/gpgkey' > $ATOMREPO

  dnf install -y atom
}

RemoveAtomEditor(){
  #Install atom repo
  # See more here https://flight-manual.atom.io/getting-started/sections/installing-atom/#platform-linux
  ### FIXME: ###
  #rpm --import https://packagecloud.io/AtomEditor/atom/gpgkey
  rm /etc/yum.repos.d/atom.repo
  dnf remove -y atom
}

InstallAtomPlugins(){
    if ( command -v atom > /dev/null 2>&1 ) ; then
      su $MYUSER -c "apm install minimap"
      su $MYUSER -c "apm install line-ending-converter"
      su $MYUSER -c "apm install git-plus"
      su $MYUSER -c "apm install atom-beautify"
      su $MYUSER -c "apm install autoclose-html"
      su $MYUSER -c "apm install ask-stack"
      su $MYUSER -c "apm install open-recent"
      su $MYUSER -c "apm install compare-files"
      su $MYUSER -c "apm install language-powershell"
    fi
}

RemoveAtomPlugins(){
    if ( command -v atom > /dev/null 2>&1 ) ; then
      su $MYUSER -c "apm uninstall minimap"
      su $MYUSER -c "apm uninstall line-ending-converter"
      su $MYUSER -c "apm uninstall git-plus"
      su $MYUSER -c "apm uninstall atom-beautify"
      su $MYUSER -c "apm uninstall autoclose-html"
      su $MYUSER -c "apm uninstall ask-stack"
      su $MYUSER -c "apm uninstall open-recent"
      su $MYUSER -c "apm uninstall compare-files"
      su $MYUSER -c "apm uninstall language-powershell"
    fi
}

InstallBasicEditors(){
  dnf install -y nano vim
}

RemoveBasicEditors(){
  dnf remove -y nano vim
}

InstallCommanderFileMgrs(){
  dnf install -y gnome-commander mc
}

RemoveCommanderFileMgrs(){
  dnf remove -y gnome-commander mc
}

InstallTerminator(){
  dnf install -y terminator
}

RemoveTerminator(){
  dnf remove -y terminator
}

InstallKeepassx(){
  dnf install -y keepassx
}

RemoveKeepassx(){
  dnf remove -y keepassx
}


################################################################
###### Communication ####
################################################################

InstallChatProgs(){
  dnf install -y hexchat pidgin pidgin-otr
}

RemoveChatProgs(){
  dnf install -y hexchat pidgin pidgin-otr
}

InstallThunderbird(){
  dnf install -y thunderbird
}

RemoveThunderbird(){
  dnf remove -y thunderbird
}


################################################################
###### NetworkConfiguration ####
################################################################

DisableMulticastDNS(){
  # change /etc/nsswitch.conf file to disable mulicast dns and use dns first
  # multicast dns has to be disabled to resolve .local dns names (like in Active Directory domains called eg. contoso.local)
  NSSWITCHFILE=/etc/nsswitch.conf
  DNSLINENO=$(cat $NSSWITCHFILE | grep -in ^hosts | cut -c1-2)
  NEWLINENO=$(($DNSLINENO)) #Why is it not +1 ???

  NEWDNSLINE=$(cat $NSSWITCHFILE | grep -i ^hosts | sed 's/dns //g' | sed 's/files/files dns/g')
  NOMULTIDNSLINE=$(cat $NSSWITCHFILE | grep -i ^hosts | sed 's/mdns4_minimal //g' | sed 's/dns //g' | sed 's/files/files dns/g')

  sed -i "s/^hosts/#hosts/g" $NSSWITCHFILE
  #sed -i "$NEWLINENO a $NEWDNSLINE" $NSSWITCHFILE #Keep Multicast DNS
  sed -i "$NEWLINENO a $NOMULTIDNSLINE" $NSSWITCHFILE # Discard Multicast DNS
}

InstallNetworkTools(){
  dnf install -y tcpdump wireshark-gnome tftp-server nmap macchanger flow-tools
}

RemoveNetworkTools(){
  dnf remove -y tcpdump wireshark-gnome tftp-server nmap macchanger flow-tools
}

InstallNetCommsTools(){
  dnf install -y minicom putty remmina
}

RemoveNetCommsTools(){
  dnf install -y minicom putty remmina
}

InstallNetMgrL2TP(){
  dnf install -y NetworkManager-l2tp NetworkManager-l2tp-gnome
}

RemoveNetMgrL2TP(){
  dnf remove -y NetworkManager-l2tp NetworkManager-l2tp-gnome
}

InstallOpenconnectVPN(){
  # OpenConnect for use with Juniper VPN
  dnf install -y automake libtool openssl-devel libxml2 libxml2-devel vpnc-script NetworkManager-openconnect-gnome
  su $MYUSER -c 'mkdir -p ~/git &>/dev/null'
  su $MYUSER -c 'cd ~/git ;  git clone git://git.infradead.org/users/dwmw2/openconnect.git ; cd openconnect/ ; ./autogen.sh ; ./configure --with-vpnc-script=/etc/vpnc/vpnc-script --without-openssl-version-check --prefix=/usr/ --disable-nls ; make'
  make install
}

################################################################
###### Productivity Tools ###
################################################################

InstallDia(){
  dnf install -y dia
}

RemoveDia(){
  dnf remove -y dia
}

InstallWine(){
  dnf install -y wine
}

RemoveWine(){
  dnf remove -y wine
}


################################################################
###### Supporting scripts ###
################################################################

InstallTecmintMonitorSh(){
  # A Shell Script to Monitor Network, Disk Usage, Uptime, Load Average and RAM Usage in Linux
  # https://www.tecmint.com/linux-server-health-monitoring-script/
  TECMINTMONSCRIPT=http://tecmint.com/wp-content/scripts/tecmint_monitor.sh
  wget -O /usr/local/bin/tecmint_monitor.sh $TECMINTMONSCRIPT
  chmod 755 /usr/local/bin/tecmint_monitor.sh
}

RemoveTecmintMonitorSh(){
  # Remove script
  rm /usr/local/bin/tecmint_monitor.sh
}

InstallGnomeExtInstaller(){
  # Script for searching and installing Gnome extensions
  # http://www.bernaerts-nicolas.fr/linux/76-gnome/345-gnome-shell-install-remove-extension-command-line-script

  su $MYUSER -c "mkdir -p ~/git &>/dev/null"
  su $MYUSER -c "cd ~/git ; git clone https://github.com/brunelli/gnome-shell-extension-installer"

  ln -fs "/home/$MYUSER/git/gnome-shell-extension-installer/gnome-shell-extension-installer" "/usr/local/bin/gnome-shell-extension-installer"
}

RemoveGnomeExtInstaller(){
  # Script for searching and installing Gnome extensions
  # http://www.bernaerts-nicolas.fr/linux/76-gnome/345-gnome-shell-install-remove-extension-command-line-script

  su $MYUSER -c "rm -rf ~/git/gnome-shell-extension-installer" # remove github repo clone
  rm "/usr/local/bin/gnome-shell-extension-installer" &>/dev/null # remove symlink
}


InstallMozExtensionMgr(){
  # Script for searching and installing Firefox extensions
  # http://www.bernaerts-nicolas.fr/linux/74-ubuntu/271-ubuntu-firefox-thunderbird-addon-commandline

  su $MYUSER -c "mkdir -p ~/git &>/dev/null"
  su $MYUSER -c "cd ~/git ; git clone https://github.com/NicolasBernaerts/ubuntu-scripts"

  # Fix missing executable flag when fetched from repo
  chmod 755 "/home/$MYUSER/git/ubuntu-scripts/mozilla/firefox-extension-manager"

  # create symlinks
  ln -fs "/home/$MYUSER/git/ubuntu-scripts/mozilla/firefox-extension-manager" "/usr/local/bin/firefox-extension-manager"
  ln -fs "/home/$MYUSER/git/ubuntu-scripts/mozilla/mozilla-extension-manager" "/usr/local/bin/mozilla-extension-manager"
}

RemoveMozExtensionMgr(){
  su $MYUSER -c "rm -rf ~/git/ubuntu-scripts" # remove github repo clone
  rm "/usr/local/bin/firefox-extension-manager"  &>/dev/null # remove symlink
  rm "/usr/local/bin/mozilla-extension-manager"  &>/dev/null # remove symlink
}

################################################################
###### Web Browsers ###
################################################################

InstallChromium(){
  # Install Chromium browser
  dnf install -y chromium
}

RemoveChromium(){
  # Install Chromium browser
  dnf remove -y chromium
}

InstallChrome(){
  # download and install chrome and it's dependencies

  CHROMEREPO=/etc/yum.repos.d/google-chrome.repo

echo '[google-chrome]
name=google-chrome - $basearch
baseurl=http://dl.google.com/linux/chrome/rpm/stable/$basearch
enabled=1
gpgcheck=1
gpgkey=https://dl-ssl.google.com/linux/linux_signing_key.pub' > $CHROMEREPO

  dnf install -y google-chrome-stable
}

RemoveChrome(){
  CHROMEREPO=/etc/yum.repos.d/google-chrome.repo
  rm $CHROMEREPO
  dnf remove -y google-chrome-stable
}

SetChromePreferences(){
  # Create the master_preferences file
  # File contents based on source fils: https://src.chromium.org/viewvc/chrome/trunk/src/chrome/common/pref_names.cc

  CHROMEINSTALLDIR=/opt/google/chrome/
  CHROMEPREFFILE=$CHROMEINSTALLDIR"master_preferences"

echo '{
 "homepage" : "https://www.google.com",
 "homepage_is_newtabpage" : false,
 "dns_prefetching.enabled" : false,
 "browser" : {
   "show_home_button" : true,
   "check_default_browser" : false
 },
 "safebrowsing" : {
   "enabled" : false,
   "reporting_enabled" : false
 },
 "net": {"network_prediction_options": 2},
 "bookmark_bar" : {
   "show_on_all_tabs" : true
 },
 "distribution" : {
  "import_bookmarks" : false,
  "import_history" : false,
  "import_home_page" : false,
  "import_search_engine" : false,
  "suppress_first_run_bubble" : true,
  "do_not_create_desktop_shortcut" : true,
  "do_not_create_quick_launch_shortcut" : true,
  "do_not_create_taskbar_shortcut" : true,
  "do_not_launch_chrome" : true,
  "do_not_register_for_update_launch" : true,
  "make_chrome_default" : false,
  "make_chrome_default_for_user" : false,
  "msi" : true,
  "require_eula" : false,
  "suppress_first_run_default_browser_prompt" : true,
  "system_level" : true,
  "verbose_logging" : true
 },
 "first_run_tabs" : [
   "http://www.google.com",
   "welcome_page",
   "new_tab_page"
 ]
}' > $CHROMEPREFFILE
}

UnsetChromePreferences(){
  CHROMEINSTALLDIR=/opt/google/chrome/
  v=$CHROMEINSTALLDIR"master_preferences"
  rm $CHROMEPREFFILE
}

SetFirefoxPreferences() {
  #Creates config files for firefox

  FIREFOXINSTALLDIR=/usr/lib64/firefox/
  FIREFOXPREFFILE=$FIREFOXINSTALLDIR"mozilla.cfg"

echo '//
pref("network.dns.disablePrefetch", true);
pref("network.prefetch-next", false);
pref("browser.rights.3.shown", true);
pref("browser.startup.homepage_override.mstone","ignore");
pref("browser.newtabpage.introShown", false);
pref("startup.homepage_welcome_url.additional", "https://encrypted.google.com");
pref("browser.usedOnWindows10", true);
pref("browser.startup.homepage", "https://encrypted.google.com");
pref("browser.newtabpage.pinned", "https://encrypted.google.com");
pref("datareporting.healthreport.service.enabled", false);
pref("datareporting.healthreport.uploadEnabled", false);
pref("datareporting.policy.dataSubmissionEnabled", false);
pref("toolkit.crashreporter.enabled", false);
pref("services.sync.enabled", false);
pref("media.peerconnection.enabled", false);
pref("extensions.pocket.enabled", false);' > $FIREFOXPREFFILE

  # Create the autoconfig.js file (enables preferences)
  FIREFOXAUTOCONFIG=$FIREFOXINSTALLDIR"defaults/pref/autoconfig.js"
echo 'pref("general.config.obscure_value", 0);
pref("general.config.filename", "mozilla.cfg");' > $FIREFOXAUTOCONFIG

  # Create the override.ini file (disables Migration Wizard)
  FIREFOXOVERRIDEFILE=$FIREFOXINSTALLDIR"browser/override.ini"
echo '[XRE]
EnableProfileMigrator=false' > $FIREFOXOVERRIDEFILE

}

UnsetFirefoxPreferences() {
  #Creates config files for firefox

  FIREFOXINSTALLDIR=/usr/lib64/firefox/
  FIREFOXPREFFILE=$FIREFOXINSTALLDIR"mozilla.cfg"
  FIREFOXAUTOCONFIG=$FIREFOXINSTALLDIR"defaults/pref/autoconfig.js"
  FIREFOXOVERRIDEFILE=$FIREFOXINSTALLDIR"browser/override.ini"
  rm $FIREFOXPREFFILE
  rm $FIREFOXAUTOCONFIG
  rm $FIREFOXOVERRIDEFILE
}


################################################################
###### Multimedia ###
################################################################

InstallSpotifyClient(){
  # install Spotify client
  # See details and firewall config here http://negativo17.org/spotify-client/
  rpm --import https://negativo17.org/repos/RPM-GPG-KEY-slaanesh
  dnf config-manager --add-repo=http://negativo17.org/repos/fedora-spotify.repo
  dnf install -y spotify-client
}

RemoveSpotifyClient(){
  # remove Spotify client
  rpm -e gpg-pubkey-f90c0e97-483e8383 # remove imported PGP key
  SPOTIFYREPO=/etc/yum.repos.d/fedora-spotify.repo
  rm $SPOTIFYREPO
  dnf remove -y spotify-client
}

InstallVLCPlayer(){
  # install VLC player
  # installed from rpmfusion-free-updates repo
  dnf install -y vlc
}

RemoveVLCPlayer(){
  # remove VLC player
  dnf remove -y vlc
}

InstallClementinePlayer(){
  # install clementine media player & pulseaudio equalizer
  dnf install -y clementine gstreamer-plugins-ugly gstreamer-plugins-bad gstreamer-plugins-good
}

RemoveClementinePlayer(){
  # install clementine media player & pulseaudio equalizer
  dnf remove -y clementine gstreamer-plugins-ugly gstreamer-plugins-bad gstreamer-plugins-good
}

InstallPulseAudioEq(){
  dnf install -y pulseaudio
}

RemovePulseAudioEq(){
  dnf remove -y pulseaudio
}

InstallYouTubeDownloader(){
  # install Youtube Downloader
   dnf install -y youtube-dl
}

RemoveYouTubeDownloader(){
  # remove Youtube Downloader
   dnf remove -y youtube-dl
}

################################################################
###### Gnome Tools & Tweaks ###
################################################################

InstallGnomeTools(){
  dnf install -y system-config-printer gnome-tweak-tool
}

RemoveGnomeTools(){
  dnf remove -y system-config-printer gnome-tweak-tool gparted
}

InstallSystemMonitor(){
  # install system monitor dependecies
  dnf install -y libgtop2-devel NetworkManager-glib-devel
  dnf install -y lm_sensors #for fan overview

  # install system monitor from github
  su $MYUSER -c "mkdir -p ~/git &>/dev/null ; mkdir -p ~/.local/share/gnome-shell/extensions > /dev/null"
  su $MYUSER -c "cd ~/git ;  git clone git://github.com/paradoxxxzero/gnome-shell-system-monitor-applet.git"
  su $MYUSER -c "ln -fs ~/git/gnome-shell-system-monitor-applet/system-monitor@paradoxxx.zero.gmail.com ~/.local/share/gnome-shell/extensions/system-monitor"

}

RemoveSystemMonitor(){
  # install system monitor dependecies
  dnf remove -y libgtop2-devel NetworkManager-glib-devel lm_sensors

  su $MYUSER -c "rm ~/git/gnome-shell-system-monitor-applet.git"
  su $MYUSER -c "rm ~/.local/share/gnome-shell/extensions/system-monitor"

}

################################################################
###### Miscellaneous tweaks and installs  ###
################################################################

InstallCheat(){
  # install cheat sheet - http://www.tecmint.com/cheat-command-line-cheat-sheet-for-linux-users/
  dnf install -y python python-pip
  pip install --upgrade pip
  pip install docopt pygments
  su $MYUSER -c 'mkdir -p ~/git &>/dev/null'
  su $MYUSER -c "cd ~/git ; git clone https://github.com/chrisallenlane/cheat.git ; "
  cd /home/$MYUSER/git/cheat
  python setup.py install
}

InstallThinkfanOnThinkpad(){
  # http://thinkfan.sourceforge.net/
  #Check if machine is a ThinkPad
  if [ $( dmidecode -s system-version | grep ThinkPad -i | wc -l ) -ne 0 ] ; then
  # install the thinkfan program
    dnf -y install thinkfan
    systemctl enable thinkfan.service # enable service
  fi
}

RemoveThinkfanIfInstalled(){
      rpm -q --quiet thinkfan && dnf remove -y thinkfan
}

InstallUnifyingOnLaptop(){
  # install the Logitech Unifying Receiver software on laptop
  # if the machine has a battery (it is probably a laptop), install
  if [ $( dmidecode | grep Battery -i | wc -l) -ne 0 ] ; then
    # Battery found - Installing Logitech Unifying Receiver and ACPI
    dnf install -y solaar acpi
  fi
}

RemoveUnifyingOnLaptop(){
  UNIFYINGPACKAGES=("solaar" "acpi")
  for i in ${!UNIFYINGPACKAGES[@]};
  do
    rpm -q --quiet ${UNIFYINGPACKAGES[$i]}  && dnf remove -y ${UNIFYINGPACKAGES[$i]}
  done
}

InstallVMtoolsOnVM(){
  # if a virtual machine, install open-vm-tools
  # for more virtualization vendors check here http://unix.stackexchange.com/questions/89714/easy-way-to-determine-virtualization-technology
  if [ $( dmidecode -s system-product-name | grep -i VMware | wc -l ) -ne 0 ] ; then
    dnf install -y open-vm-tools
  fi
}

RemoveVMtoolsOnVM(){
  # if a virtual machine, install open-vm-tools
  # for more virtualization vendors check here http://unix.stackexchange.com/questions/89714/easy-way-to-determine-virtualization-technology
  if [ $( dmidecode -s system-product-name | grep -i VMware | wc -l ) -ne 0 ] ; then
    rpm -q --quiet open-vm-tools && dnf remove -y open-vm-tools
  fi
}

################################################################
###### 3rd party applications ###
################################################################

InstallOwnCloudClient(){
  # OwnCloud client
  FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number
  dnf config-manager --add-repo http://download.opensuse.org/repositories/isv:ownCloud:desktop/Fedora_$FEDORARELEASE/isv:ownCloud:desktop.repo
  dnf install -y owncloud-client
}

RemoveOwnCloudClient(){
  # Remove OwnCloud client
  rm /etc/yum.repos.d/isv:ownCloud:desktop.repo
  dnf remove -y owncloud-client
}

InstallVeraCrypt(){
  # download and install veracrypt archive
  VERACRYPTDOWNLOADPAGE="https://www.veracrypt.fr/en/Downloads.html"
  VERACRYPTURL=$(curl $VERACRYPTDOWNLOADPAGE 2>&1 | grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 | \
                grep -v freebsd | grep -v legacy | grep setup.tar | grep -v sig | awk NR==1 | sed 's/&#43;/+/g')
  VERACRYPTPKG="${VERACRYPTURL##*/}"

  wget $VERACRYPTURL
  tar xvjf $VERACRYPTPKG -C /tmp veracrypt-*-setup-gui-x64 #extract only the x64 bit console installer
  mv /tmp/veracrypt-*-setup-gui-x64  /tmp/veracrypt-setup-gui-x64
  /tmp/veracrypt-setup-gui-x64

}

InstallVMwareWorkstation(){
  # download and install vmware workstation
  # if serialnumberfile is sourced with script, it can autoadd serial number

  VMWAREURL=https://www.vmware.com/go/getworkstation-linux
  BINARYURL=$(wget $VMWAREURL -O - --content-disposition --spider 2>&1 | grep Location | cut -d ' ' -f2) # Full URL to binary installer
  BINARYFILENAME="${BINARYURL##*/}" # Filename of binary installer
  VMWAREVERSION=$(echo $BINARYURL | cut -d '-' -f4 ) # In the format XX.XX.XX
  MAJORVERSION=$(echo $BINARYURL | cut -d '-' -f4 | cut -d '.' -f1) # In the format XX
  # Another way of getting MAJORVERSION: curl -sIkL $VMWAREURL | grep "filename=" | sed -r 's|^([^.]+).*$|\1|; s|^[^0-9]*([0-9]+).*$|\1|'

  if [ ! -z "VMWARESERIAL$MAJORVERSION" ] ; then # VMWARESERIALXX of the current major release is defined in config file
    # TMPSERIAL is used to translate serial numbers from config file - if major version is 15 then the value of the entry VMWARESERIAL15 is assigned to TMPSERIAL.
    TMPSERIAL=VMWARESERIAL$MAJORVERSION # Addressing of a dynamic variable is different. Therefore it is put into CURRENTVMWSERIAL
    CURRENTVMWSERIAL=${!TMPSERIAL}
  fi

  # Starting with prerequisites
  dnf -y install elfutils-libelf-devel

  wget --content-disposition -N -q --show-progress $VMWAREURL # Overwrite file, quiet
  chmod +x $BINARYFILENAME
  ./$BINARYFILENAME --required --console #

  # add serial number if serial number is defined
  if [ ! -z $CURRENTVMWSERIAL ] ; then #Serial number for major version is loaded as a variable
    /usr/lib/vmware/bin/vmware-vmx --new-sn $CURRENTVMWSERIAL #please note that this variable needs to be addressed differently because it's dynamically defined
  fi

  vmware-modconfig --console --install-all --eulas-agreed

  # enable 3D acceleration in VMware Workstation
  su $MYUSER -c 'mkdir -p ~/.vmware ; touch ~/.vmware/preferences'
  su $MYUSER -c 'echo "mks.gl.allowBlacklistedDrivers = TRUE" >> ~/.vmware/preferences'

}

RemoveVMwareWorkstation(){
  vmware-installer --uninstall-product=vmware-workstation
}


InstallCitrixClient(){
  # Citrix Client
  CITRIXCLIENTURL=https://www.citrix.com/downloads/workspace-app/linux/workspace-app-for-linux-latest.html
  BINARYURL="https:$(curl $CITRIXCLIENTURL 2>&1 | grep rel | grep rhel | grep x86_64 | sed 's/^.*rel/rel/' | cut -d '"' -f2 | grep Web)"
  BINARYFILENAME=$(echo "${BIN##*/}" | sed 's/?.*//' )
  wget $BINARYURL -O $BINARYFILENAME
  dnf -y install $BINARYFILENAME
}

RemoveCitrixClient(){
    rpm -q --quiet ICAClient && dnf remove -y ICAClient FIXME
}



#############################33

_addLUKSpassword(){
  # Add extra password for LUKS
  echo
  for DISKLETTER in {a..z}
  do
    NUMBEROFPARTITIONS=$(ls /dev |grep sd$DISKLETTER. |wc -l)
    for (( PARTITIONNO=1; PARTITIONNO<=$NUMBEROFPARTITIONS; PARTITIONNO++ ))
    do
      if  (cryptsetup isLuks /dev/sd$DISKLETTER$PARTITIONNO) ; then
        PARTITION="sd$DISKLETTER$PARTITIONNO" # partition name
        echo Add password for $PARTITION...
        cryptsetup luksAddKey $PARTITION
      fi
    done
  done
}

_addExtraLUKSdisk(){
  # See more here: https://fedoraproject.org/wiki/Disk_Encryption_User_Guide
  # Check this one too: https://www.centos.org/forums/viewtopic.php?t=50535
  # http://forums.fedoraforum.org/showthread.php?t=304345

  DISKLETTER=b
  MOUNTPOINT=/mnt/sd$DISKLETTER
  DEVICE=/dev/sd$DISKLETTER

  cryptsetup -y -v luksFormat $DEVICE
  cryptsetup isLuks $DEVICE && echo Success
  HDDUUID=$(cryptsetup luksUUID $DEVICE)
  LUKSNAME="luks-$HDDUUID"

  cryptsetup luksOpen $DEVICE $LUKSNAME
  mkfs.ext4 /dev/mapper/$LUKSNAME
  mkdir -p $MOUNTPOINT
  mount /dev/mapper/$LUKSNAME $MOUNTPOINT
  chmod 755 $MOUNTPOINT

  # Generate key file for LUKS encryption
  dd if=/dev/urandom of=/root/keyfile_sd$DISKLETTER bs=1024 count=4
  chmod 0400 /root/keyfile_sd$DISKLETTER
  cryptsetup luksAddKey $DEVICE /root/keyfile_sd$DISKLETTER

  #For /etc/crypttab
  echo "$LUKSNAME UUID=$HDDUUID /root/keyfile_sd$DISKLETTER" >> /etc/crypttab

  #For /etc/fstab
  echo "/dev/mapper/$LUKSNAME   $MOUNTPOINT   ext4   defaults  0  2" >> /etc/fstab

  #sdX_crypt      /dev/sdX  /root/keyfile  luks
  #sdX_crypt      /dev/disk/by-uuid/247ad289-dbe5-4419-9965-e3cd30f0b080  /root/keyfile  luks
}
