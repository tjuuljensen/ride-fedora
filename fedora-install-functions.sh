#!/bin/sh
#
# Author: Torsten Juul-Jensen
# Edited: May 4, 2019 15:50
#
# This file is a function library only and is meant for . sourcing into other scripts
# It is a part of the github repo https://github.com/tjuuljensen/bootstrap-fedora
#

MYUSER=$(logname)
LOGINUSERUID=$(id -u ${MYUSER})
DOWNLOADDIR=/tmp
FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number


################################################################
###### Auxiliary Functions  ###
################################################################

RequireAdmin(){
    # check if script is root and restart as root if not
    [ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"
}

SetupUserDefaultDirs(){
  # Create user's bin and git directories
  MYUSERDIR=/home/$MYUSER
  cd $MYUSERDIR
  mkdir -p git > /dev/null
  chown $MYUSER:$MYUSER git
  mkdir -p bin > /dev/null
  chown $MYUSER:$MYUSER bin

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

PressAnyKeyToContinue(){
    read -n 1 -s -r -p "Press any key to continue"
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

InstallPython(){
  # Install pyhton and pip
  dnf install -y python python-pip
  pip install --upgrade pip

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
  #remove atom gpg key, repo and package
  rpm -e gpg-pubkey-de9e3b09-5a34231f
  rm /etc/yum.repos.d/atom.repo
  dnf remove -y atom
}

InstallAtomPlugins(){
    if ( command -v atom > /dev/null 2>&1 ) ; then
      sudo -u $MYUSER apm install minimap
      sudo -u $MYUSER apm install line-ending-converter
      sudo -u $MYUSER apm install git-plus
      sudo -u $MYUSER apm install atom-beautify
      sudo -u $MYUSER apm install autoclose-html
      sudo -u $MYUSER apm install ask-stack
      sudo -u $MYUSER apm install open-recent
      sudo -u $MYUSER apm install compare-files
      sudo -u $MYUSER apm install language-powershell
    fi
}

RemoveAtomPlugins(){
    if ( command -v atom > /dev/null 2>&1 ) ; then
      sudo -u $MYUSER apm uninstall minimap
      sudo -u $MYUSER apm uninstall line-ending-converter
      sudo -u $MYUSER apm uninstall git-plus
      sudo -u $MYUSER apm uninstall atom-beautify
      sudo -u $MYUSER apm uninstall autoclose-html
      sudo -u $MYUSER apm uninstall ask-stack
      sudo -u $MYUSER apm uninstall open-recent
      sudo -u $MYUSER apm uninstall compare-files
      sudo -u $MYUSER apm uninstall language-powershell
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

InstallThunderbirdExts(){
  # Install Thunderbird Extensions

  if ( command -v mozilla-extension-manager  > /dev/null 2>&1 ) ; then

    ADDONS=(
      "https://addons.mozilla.org/thunderbird/downloads/latest/71/addon-71-latest.xpi"
      "https://addons.mozilla.org/thunderbird/downloads/latest/google-search-for-thunderbi/addon-370540-latest.xpi"
      "https://addons.mozilla.org/thunderbird/downloads/latest/provider-for-google-calendar/addon-4631-latest.xpi"
      "https://addons.mozilla.org/thunderbird/downloads/latest/provider-for-google-calendar/addon-4631-latest.xpi"
      "https://addons.mozilla.org/thunderbird/downloads/latest/thunderkeep/addon-464405-latest.xpi"
      "https://addons.mozilla.org/thunderbird/downloads/latest/dansk-ordbog/addon-3596-latest.xpi"
      "https://github.com/ExchangeCalendar/exchangecalendar/releases/download/v4.0.0-beta5/exchangecalendar-v4.0.0-beta5.xpi"
    )

    cd /tmp

    sudo -u $MYUSER thunderbird & # start Thunderbird so profile is created
    sleep 15
    pkill thunderbird

    for ADDON in "${ADDONS[@]}"
    do
      su $MYUSER -c "mozilla-extension-manager --install --user --url $ADDON"
    done
  fi

}

RemoveThunderbirdExts(){
  # Remove Thunderbird Extensions

  if ( command -v mozilla-extension-manager  > /dev/null 2>&1 ) ; then

    ADDONS=(
      "https://addons.mozilla.org/thunderbird/downloads/latest/71/addon-71-latest.xpi"
      "https://addons.mozilla.org/thunderbird/downloads/latest/google-search-for-thunderbi/addon-370540-latest.xpi"
      "https://addons.mozilla.org/thunderbird/downloads/latest/provider-for-google-calendar/addon-4631-latest.xpi"
      "https://addons.mozilla.org/thunderbird/downloads/latest/provider-for-google-calendar/addon-4631-latest.xpi"
      "https://addons.mozilla.org/thunderbird/downloads/latest/thunderkeep/addon-464405-latest.xpi"
      "https://addons.mozilla.org/thunderbird/downloads/latest/dansk-ordbog/addon-3596-latest.xpi"
      "https://github.com/ExchangeCalendar/exchangecalendar/releases/download/v4.0.0-beta5/exchangecalendar-v4.0.0-beta5.xpi"
    )

    cd /tmp

    for ADDON in "${ADDONS[@]}"
    do
      su $MYUSER -c "mozilla-extension-manager --remove --user --url $ADDON"
    done
  fi

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

  MYUSERDIR=/home/$MYUSER
  if [ ! -d $MYUSERDIR ] ; then
    cd $MYUSERDIR
    mkdir -p git > /dev/null
    chown $MYUSER:$MYUSER git
  fi

  su $MYUSER -c "cd $MYUSERDIR/git ;  git clone git://git.infradead.org/users/dwmw2/openconnect.git ; cd openconnect/ ; ./autogen.sh ; ./configure --with-vpnc-script=/etc/vpnc/vpnc-script --without-openssl-version-check --prefix=/usr/ --disable-nls ; make"
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

  # Check if git library exists and create if it doesn't
  MYUSERDIR=/home/$MYUSER
  if [ ! -d $MYUSERDIR=/home/$MYUSER/git ] ; then
    cd $MYUSERDIR
    mkdir -p git > /dev/null
    chown $MYUSER:$MYUSER git
  fi

  su $MYUSER -c "cd $MYUSERDIR/git ; git clone https://github.com/brunelli/gnome-shell-extension-installer"
  ln -fs "$MYUSERDIR/git/gnome-shell-extension-installer/gnome-shell-extension-installer" "/usr/local/bin/gnome-shell-extension-installer"
}

RemoveGnomeExtInstaller(){
  # Script for searching and installing Gnome extensions
  # http://www.bernaerts-nicolas.fr/linux/76-gnome/345-gnome-shell-install-remove-extension-command-line-script
  MYUSERDIR=/home/$MYUSER
  rm -rf $MYUSERDIR/git/gnome-shell-extension-installer # remove github repo clone
  rm "/usr/local/bin/gnome-shell-extension-installer" &>/dev/null # remove symlink
}


InstallMozExtensionMgr(){
  # Script for searching and installing Firefox extensions
  # http://www.bernaerts-nicolas.fr/linux/74-ubuntu/271-ubuntu-firefox-thunderbird-addon-commandline

  # Check if git library exists and create if it doesn't
  MYUSERDIR=/home/$MYUSER
  if [ ! -d $MYUSERDIR ] ; then
    cd $MYUSERDIR
    mkdir -p git > /dev/null
    chown $MYUSER:$MYUSER git
  fi

  su $MYUSER -c "cd $MYUSERDIR/git ; git clone https://github.com/NicolasBernaerts/ubuntu-scripts"

  # Fix missing executable flag when fetched from repo
  chmod 755 "/home/$MYUSER/git/ubuntu-scripts/mozilla/firefox-extension-manager"

  # create symlinks
  ln -fs "/home/$MYUSER/git/ubuntu-scripts/mozilla/firefox-extension-manager" "/usr/local/bin/firefox-extension-manager"
  ln -fs "/home/$MYUSER/git/ubuntu-scripts/mozilla/mozilla-extension-manager" "/usr/local/bin/mozilla-extension-manager"
}

RemoveMozExtensionMgr(){
  MYUSERDIR=/home/$MYUSER
  rm -rf $MYUSERDIR/git/ubuntu-scripts # remove github repo clone
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
  MYUSERDIR=/home/$MYUSER

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

InstallFirefoxAddons(){
  if ( command -v firefox-extension-manager  > /dev/null 2>&1 ) ; then

    ADDONS=(
      "https://addons.mozilla.org/en-US/firefox/addon/ublock-origin"
      "https://addons.mozilla.org/en-US/firefox/addon/privacy-badger17"
      "https://addons.mozilla.org/en-US/firefox/addon/https-everywhere/"
      "https://addons.mozilla.org/en-US/firefox/addon/noscript"
      "https://addons.mozilla.org/en-US/firefox/addon/print-friendly-pdf/"
      "https://addons.mozilla.org/en-US/firefox/addon/disable-autoplay/"
      "https://addons.mozilla.org/en-US/firefox/addon/video-downloadhelper/"
    )

    cd /tmp


    if [ ! -d $(ls -d $MYUSERDIR/.mozilla/firefox/*.default) ] ; then
      mkdir -p $MYUSERDIR/.mozilla/firefox &>/dev/null
      chown $MYUSER:$MYUSER $MYUSERDIR/.mozilla/firefox
      sudo -u $MYUSER firefox & # start Firefox so default profile is created
      sleep 10
      pkill firefox
    fi

    FIREFOXCONFIGDIR=$(ls -d $MYUSERDIR/.mozilla/firefox/*.default)
    su  $MYUSER -c "cd $MYUSERDIR/.mozilla/firefox ; cd $FIREFOXCONFIGDIR ; mkdir extensions &>/dev/null"

    for ADDON in "${ADDONS[@]}"
    do
      su $MYUSER -c "firefox-extension-manager --install --user --url $ADDON"
    done
  fi
}

RemoveFirefoxAddons(){
  if ( command -v firefox-extension-manager  > /dev/null 2>&1 ) ; then

    ADDONS=(
      "https://addons.mozilla.org/en-US/firefox/addon/ublock-origin"
      "https://addons.mozilla.org/en-US/firefox/addon/privacy-badger17"
      "https://addons.mozilla.org/en-US/firefox/addon/https-everywhere/"
      "https://addons.mozilla.org/en-US/firefox/addon/noscript"
      "https://addons.mozilla.org/en-US/firefox/addon/print-friendly-pdf/"
      "https://addons.mozilla.org/en-US/firefox/addon/disable-autoplay/"
      "https://addons.mozilla.org/en-US/firefox/addon/video-downloadhelper/"
    )

    cd /tmp

    for ADDON in "${ADDONS[@]}"
    do
      su $MYUSER -c "firefox-extension-manager --remove --user --url $ADDON"
    done
  fi
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
  # install system monitor dependecies and applet
  # lm_sensors is for fan overview
  dnf install -y libgtop2-devel NetworkManager-glib-devel lm_sensors gnome-shell-extension-system-monitor-applet
}

RemoveSystemMonitor(){
  # install system monitor dependecies
  dnf remove -y libgtop2-devel NetworkManager-glib-devel lm_sensors gnome-shell-extension-system-monitor-applet
}

InstallGnomeExtensions(){
  # Install Gnome extensions

  # Install using gnome-shell-extension-installer script
  if ( command -v gnome-shell-extension-installer > /dev/null 2>&1 ) ; then
    # install frippery move clock - https://extensions.gnome.org/extension/2/move-clock/
    sudo -u $MYUSER gnome-shell-extension-installer 2
    # install caffeine - https://extensions.gnome.org/extension/517/caffeine/
    sudo -u $MYUSER gnome-shell-extension-installer 517
    # Install scale switcher - https://extensions.gnome.org/extension/1306/scale-switcher/
    sudo -u $MYUSER gnome-shell-extension-installer 1306
  fi

  # get gnome extensions from github
  # Check if git library exists and create if it doesn't
  MYUSERDIR=/home/$MYUSER
  if [ ! -d $MYUSERDIR=/home/$MYUSER/git ] ; then
    cd $MYUSERDIR
    mkdir -p git > /dev/null
    chown $MYUSER:$MYUSER git
  fi

  sudo -u $MYUSER mkdir -p $MYUSERDIR/.local/share/gnome-shell/extensions  >/dev/null # setup base directories
  su $MYUSER -c "cd $MYUSERDIR/git ; git clone git://github.com/tjuuljensen/gnome-shell-extension-hostname-in-taskbar.git" # clone
  sudo -u $MYUSER ln -s $MYUSERDIR/git/gnome-shell-extension-hostname-in-taskbar/hostname-in-taskbar $MYUSERDIR/.local/share/gnome-shell/extensions/hostname-in-taskbar # Make symlink

  # restart gnome shell is not available under Wayland
  [[ $XDG_SESSION_TYPE != "wayland" ]] && gnome-shell-extension-installer --restart-shell

}

RemoveGnomeExtensions(){
  # Remove Gnome extensions
  if ( command -v gnome-shell-extension-installer > /dev/null 2>&1 ) ; then
    rm "/home/$MYUSER/.local/share/gnome-shell/extensions/Move_Clock@rmy.pobox.com"
    rm "/home/$MYUSER/.local/share/gnome-shell/extensions/caffeine@patapon.info"
    rm "/home/$MYUSER/.local/share/gnome-shell/extensions/ScaleSwitcher@jabi.irontec.com"
    rm "/home/$MYUSER/.local/share/gnome-shell/extensions/hostname-in-taskbar" # remove symlink

    # restart gnome shell is not available under Wayland
    [[ $XDG_SESSION_TYPE != "wayland" ]] && gnome-shell-extension-installer --restart-shell
  fi

}



EnableScreenSaver(){
  # enable screensaver
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.screensaver idle-activation-enabled 'true'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.screensaver lock-enabled 'true'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.session idle-delay 300
}

DisableScreensaver(){
  # disable screensaver
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.screensaver idle-activation-enabled 'false'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.screensaver lock-enabled 'false'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.session idle-delay 0
}

ShowDateInTaskbar(){
  # add date to top bar
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.interface clock-show-date true
}

HideDateInTaskbar(){
  # add date to top bar
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.interface clock-show-date false
}

ShowWeekNumbersInTaskbar(){
  # show week numbers in calendar drop-down
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.calendar show-weekdate true
}

HideWeekNumbersInTaskbar(){
  # show week numbers in calendar drop-down
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.calendar show-weekdate false
}

ShowGnomeDesktopIcons(){
  #enable desktop icons
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.background show-desktop-icons true
}

HideGnomeDesktopIcons(){
  #enable desktop icons
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.background show-desktop-icons false
}

SetWindowCtlMinMaxClose(){
  # add minimize and maximize buttons to windows
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.wm.preferences button-layout ':minimize,maximize,close'
}

SetWindowCtlAppmenuClose(){
  # AppMenuClose (default in Fedora 28)
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.wm.preferences button-layout ':appmenu:close'
}

SetWindowCtlLeftClsMinMax(){
  # Set buttons on the left - Close, Min & Max
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.wm.preferences button-layout 'close,minimize,maximize:'
}

SetGnomeRegionDaDK(){
  # Set system locale to da_DK
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.system.locale region "'da_DK.UTF-8'"
}

RemoveGnomeRegion(){
  # Remove system locale value (default)
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.system.locale region ''
}

SetScreensaverSlp10Lgn5(){
  # set sleep timeout to 10 minutes (600 seconds), then require login after 5 minutes (300 seconds)
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.session idle-delay 600
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.screensaver idle-activation-enabled 'true'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.screensaver lock-enabled 'true'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.screensaver lock-delay 300
}

SetScreensaverSlp15Lgn5(){
  # set sleep timeout to 15 minutes (900 seconds), then require login after 5 minutes (300 seconds)
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.session idle-delay 900
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.screensaver idle-activation-enabled 'true'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.screensaver lock-enabled 'true'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.screensaver lock-delay 300
}

SetCustomKeyboardShortcut(){

  # add <Super>+D as show-desktop shortcut
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.wm.keybindings show-desktop "['<Super>d']"

  # add the list of custom shortcuts
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/','/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/','/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/']"

  # add the first shortcut - Terminal
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/ name 'Terminal'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/ command 'gnome-terminal'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/ binding '<Control><Shift>t'

  # add the second shortcut - Terminator
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/ name 'Terminator'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/ command 'terminator'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/ binding '<Super><Control>t'

  # add the third shortcut - Home
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/ name 'Nautilus - home folder'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/ command 'nautilus'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/ binding '<Super>e'
}

SetVMKeyboardShortcut(){

  # add <Control><Alt>+D as show-desktop shortcut
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.wm.keybindings show-desktop "['<Control><Alt>d']"

  # add the list of custom shortcuts
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/','/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/','/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/']"

  # add the first shortcut - Terminal
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/ name 'Terminal'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/ command 'gnome-terminal'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/ binding '<Control><Shift>t'

  # add the second shortcut - Terminator
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/ name 'Terminator'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/ command 'terminator'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/ binding '<Control><Alt>t'

  # add the third shortcut - Home
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/ name 'Nautilus - home folder'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/ command 'nautilus'
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/ binding '<Control><Alt>e'

}

RemoveCustomKbrdShortcut(){

  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.wm.keybindings show-desktop "@as []"

  # add the list of custom shortcuts
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "@as []"

  # add the first shortcut - Terminal
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/ name ''
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/ command ''
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/ binding ''

  # add the second shortcut - Terminator
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/ name ''
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/ command ''
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/ binding ''

  # add the third shortcut - Home
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/ name ''
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/ command ''
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/ binding ''

}

SetGnomeCustomFavorites(){
    sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.shell favorite-apps "['firefox.desktop', 'chromium-browser.desktop', 'atom.desktop', 'mozilla-thunderbird.desktop', 'vmware-workstation.desktop', 'libreoffice-writer.desktop', 'org.gnome.gedit.desktop', 'org.gnome.Nautilus.desktop', 'veracrypt.desktop', 'keepassx2.desktop', 'terminator.desktop' ]"
}

SetGnomeDefaultFavorites(){
    ssudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.shell favorite-apps "['firefox.desktop', 'org.gnome.Evolution.desktop', 'rhythmbox.desktop', 'shotwell.desktop', 'org.gnome.Nautilus.desktop', 'org.gnome.Software.desktop']"
}

SetGnomeMinimalFavorites(){
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.shell favorite-apps "['firefox.desktop', 'libreoffice-writer.desktop', 'org.gnome.gedit.desktop', 'org.gnome.Nautilus.desktop',  'org.gnome.Terminal.desktop']"
}

SetGnmLocationServiceOff(){
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.system.location enabled false
}

SetGnmLocationServiceOn(){
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.system.location enabled true
}

SetGnmAutoProblemRptOff(){
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.privacy report-technical-problems false
}

SetGnmAutoProblemRptOn(){
  sudo -u $MYUSER DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${LOGINUSERUID}/bus" gsettings set org.gnome.desktop.privacy report-technical-problems true
}

################################################################
###### Miscellaneous tweaks and installs  ###
################################################################

InstallCheat(){
  # install cheat sheet - http://www.tecmint.com/cheat-command-line-cheat-sheet-for-linux-users/
  # https://github.com/chrisallenlane/cheat.git

  dnf -y copr enable tkorbar/cheat
  dnf install -y cheat

}

RemoveCheat(){
    dnf copr disable tkorbar/cheat
    dnf remove -y cheat
}


InstallThinkfanOnThinkpad(){
  # http://thinkfan.sourceforge.net/
  #Check if machine is a ThinkPad
  if [ $( dmidecode -s system-version | grep ThinkPad -i | wc -l ) -ne 0 ] ; then
  # install the thinkfan program
    dnf install -y thinkfan
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
  ./$BINARYFILENAME --required --console --eulas-agreed #

  # add serial number if serial number is defined
  if [ ! -z $CURRENTVMWSERIAL ] ; then #Serial number for major version is loaded as a variable
    /usr/lib/vmware/bin/vmware-vmx --new-sn $CURRENTVMWSERIAL #please note that this variable needs to be addressed differently because it's dynamically defined
  fi

  vmware-modconfig --console --install-all --eulas-agreed

  MYUSERDIR=/home/$MYUSER
  # enable 3D acceleration in VMware Workstation
  cd $MYUSERDIR
  if [ ! -d $MYUSERDIR/.vmware ] ; then
    mkdir $MYUSERDIR/.vmware
    chown $MYUSER:$MYUSER $MYUSERDIR/.vmware
  fi

  sudo -u $MYUSER touch $MYUSERDIR/.vmware/preferences
  sudo -u $MYUSER echo "mks.gl.allowBlacklistedDrivers = TRUE" >> $MYUSERDIR/.vmware/preferences

}

RemoveVMwareWorkstation(){
  vmware-installer --uninstall-product=vmware-workstation
}


InstallCitrixClient(){
  # Citrix Client
  CITRIXCLIENTURL=https://www.citrix.com/downloads/workspace-app/linux/workspace-app-for-linux-latest.html
  BINARYURL="https:$(curl $CITRIXCLIENTURL 2>&1 | grep rel | grep rhel | grep x86_64 | sed 's/^.*rel/rel/' | cut -d '"' -f2 | grep Web)"
  BINARYFILENAME=$(echo "${BINARYURL##*/}" | sed 's/?.*//' )
  wget $BINARYURL -O $BINARYFILENAME
  dnf -y install $BINARYFILENAME
}

RemoveCitrixClient(){
    rpm -q --quiet ICAClient && dnf remove -y ICAClient
}

################################################################
###### Encryption Functions ###
################################################################

AddExtraLUKSpasswords(){
  # Add extra password for LUKS partition

  LUKSDEVICES=$(blkid -o list | grep "LUKS" | cut -d ' ' -f1)

  for DEVICE in $LUKSDEVICES; do
    PARTITION=${DEVICE##*/}
    if  (cryptsetup isLuks $DEVICE) ; then
      echo Add password for $PARTITION...
      cryptsetup luksAddKey $DEVICE
    fi
  done
}

EncryptUnpartitionedDisks(){

  #####   STILL UNTESTED : Be careful!!!  ##########

  # Reclaim and encrypt disks without partitions (that are not already encrypted using LUKS)
  # BE AWARE that using this function might lead to dataloss - especially if you are using third party encrypting tools.
  MOUNTBASE=/mnt/

  DISKS=$(lsblk -l | grep disk | awk '{print $1}') #sda, sdb
  UNPARTEDDISKS=()

  # Check for upartitioned disks & put in array
  for DISK in $DISKS ; do
    DISKDEVICE="/dev/$DISK"
    PARTITIONS=$(/sbin/sfdisk -d $DISKDEVICE 2>&1 | grep '^/' )
    #Check if DISKDEVICE has 0 partitions and is not a LUKS device itself
    if [[ -z $PARTITIONS ]] ; then
      cryptsetup isLuks $DEVICE || UNPARTEDDISKS+=($DISKDEVICE)
    fi
  done

  for DISKDEVICE in $UNPARTEDDISKS ; do

    echo Removing partition table on $DISKDEVICE and creating new partition
# to create the partitions programatically (rather than manually)
# we're going to simulate the manual input to fdisk
# The sed script strips off all the comments so that we can
# document what we're doing in-line with the actual commands
# Note that a blank line (commented as "default" will send a empty
# line terminated with a newline to take the fdisk default.
sed -e 's/\s*\([\+0-9a-zA-Z]*\).*/\1/' << EOF | fdisk $DISKDEVICE
  g # Create a new GPT partition table
  n # new partition
  1 # partition number 1
    # default - start at beginning of disk
    # default, extend partition to end of disk
  p # print the in-memory partition table
  w # write the partition table
EOF

    NEWPARTITION=$(/sbin/sfdisk -d $DISKDEVICE 2>&1 | grep '^/' | awk '{print $1}')
    echo About to encrypted content of $NEWPARTITION
    cryptsetup -y -v luksFormat $NEWPARTITION
    cryptsetup isLuks $DISK && echo Encryption of $DISKDEVICE was a success
    HDDUUID=$(cryptsetup luksUUID $NEWPARTITION)
    LUKSNAME="luks-$HDDUUID"
    DEVICENAME=${NEWPARTITION##*/}

    echo Opening encrypted device and creating ext4 filesystem
    cryptsetup luksOpen $NEWPARTITION $LUKSNAME
    mkfs.ext4 /dev/mapper/$LUKSNAME
    MOUNTPOINT=$MOUNTBASE$DISK
    mkdir -p $MOUNTPOINT
    mount /dev/mapper/$LUKSNAME $MOUNTPOINT
    chmod 755 $MOUNTPOINT
    chown $MYUSER:$MYUSER $MOUNTPOINT

    # rotate keyfile
    KEYFILE=/root/keyfile_$DEVICENAME
    if [ -f $KEYFILE ] ; then
      i=1
      NEWKEYFILE=$KEYFILE.$i
      while [ -f $NEWKEYFILE ]
      do
        i=$(( $i + 1 ))
        NEWKEYFILE="$KEYFILE.$i"
      done
      mv $KEYFILE $NEWKEYFILE
    fi


    # Generate key file for LUKS encryption
    dd if=/dev/urandom of=$KEYFILE bs=1024 count=4
    chmod 0400 $KEYFILE
    echo Adding a keyfile for $DEVICENAME for atomount configuration
    cryptsetup luksAddKey $NEWPARTITION $KEYFILE

    #Update /etc/crypttab
    echo Updating /etc/crypttab
    echo "$LUKSNAME UUID=$HDDUUID /root/keyfile_$DEVICENAME" >> /etc/crypttab

    #Update /etc/fstab
    echo Updating /etc/fstab
    echo "/dev/mapper/$LUKSNAME   $MOUNTPOINT   ext4   defaults  0  2" >> /etc/fstab

  done

}

ReclaimEncryptDWUnmntPrt(){

  #####   STILL UNTESTED : Be careful!!!  ##########

  # Reclaim and encrypt disks with unmounted partitions
  # This function will reclaim disks with unmounted partitions - encrypted or not
  # BE AWARE! Using this function could make you loose data permanently

    MOUNTBASE=/mnt/

    DISKS=$(lsblk -l | grep disk | awk '{print $1}')
    NOTMOUNTED=$(blkid -o list | grep "not mounted" | cut -d ' ' -f1 | sed '/^$/d')

    if [ ! -z ${#NOTMOUNTED} ] ; then # some partitions are unmounted
      # Check for encrypted partitions & put in array

      for DISK in $DISKS ; do
          DISKDEVICE="/dev/$DISK"
          NUMBEROFDEVICES=$(ls $DISKDEVICE? 2>/dev/null)
          NUMBEROFUNMOUNTED=$(blkid -o list | grep "not mounted" | cut -d ' ' -f1 | sed '/^$/d' | grep $DISKDEVICE)
          #PARTITIONS=$(/sbin/sfdisk -d $DISKDEVICE 2>&1 | grep '^/' )

          #Check if DISKDEVICE has 0 partitions and is not a LUKS device itself
          if [ ${#NUMBEROFDEVICES} == ${#NUMBEROFUNMOUNTED} ] ; then
            echo No mounted partitions found on $DISKDEVICE - cleaning and encrypting

            # to create the partitions programatically (rather than manually)
            # we're going to simulate the manual input to fdisk
            # The sed script strips off all the comments so that we can
            # document what we're doing in-line with the actual commands
            # Note that a blank line (commented as "default" will send a empty
            # line terminated with a newline to take the fdisk default.
sed -e 's/\s*\([\+0-9a-zA-Z]*\).*/\1/' << EOF | fdisk $DISKDEVICE
  g # Create a new GPT partition table
  n # new partition
  1 # partition number 1
    # default - start at beginning of disk
    # default, extend partition to end of disk
  p # print the in-memory partition table
  w # write the partition table
EOF

                NEWPARTITION=$(/sbin/sfdisk -d $DISKDEVICE 2>&1 | grep '^/' | awk '{print $1}')
                echo About to encrypted content of $NEWPARTITION
                cryptsetup -y -v luksFormat $NEWPARTITION
                cryptsetup isLuks $DISK && echo Encryption of $DISKDEVICE was a success
                HDDUUID=$(cryptsetup luksUUID $NEWPARTITION)
                LUKSNAME="luks-$HDDUUID"
                DEVICENAME=${NEWPARTITION##*/}

                echo Opening encrypted device and creating ext4 filesystem
                cryptsetup luksOpen $NEWPARTITION $LUKSNAME
                mkfs.ext4 /dev/mapper/$LUKSNAME
                MOUNTPOINT=$MOUNTBASE$DISK
                mkdir -p $MOUNTPOINT
                mount /dev/mapper/$LUKSNAME $MOUNTPOINT
                chmod 755 $MOUNTPOINT
                chown $MYUSER:$MYUSER $MOUNTPOINT

                # rotate keyfile
                KEYFILE=/root/keyfile_$DEVICENAME
                if [ -f $KEYFILE ] ; then
                  i=1
                  NEWKEYFILE=$KEYFILE.$i
                  while [ -f $NEWKEYFILE ]
                  do
                    i=$(( $i + 1 ))
                    NEWKEYFILE="$KEYFILE.$i"
                  done
                  mv $KEYFILE $NEWKEYFILE
                fi

                KEYFILE=/root/keyfile_$DEVICENAME
                # rotate keyfile
                KEYFILE=/root/keyfile_$DEVICENAME
                if [ -f $KEYFILE ] ; then
                  i=1
                  NEWKEYFILE=$KEYFILE.$i
                  while [ -f $NEWKEYFILE ]
                  do
                    i=$(( $i + 1 ))
                    NEWKEYFILE="$KEYFILE.$i"
                  done
                  mv $KEYFILE $NEWKEYFILE
                fi

                # Generate key file for LUKS encryption
                dd if=/dev/urandom of=$KEYFILE bs=1024 count=4
                chmod 0400 $KEYFILE
                echo Adding a keyfile for $DEVICENAME for atomount configuration
                cryptsetup luksAddKey $NEWPARTITION $KEYFILE

                #Update /etc/crypttab
                echo Updating /etc/crypttab
                echo "$LUKSNAME UUID=$HDDUUID /root/keyfile_$DEVICENAME" >> /etc/crypttab

                #Update /etc/fstab
                echo Updating /etc/fstab
                echo "/dev/mapper/$LUKSNAME   $MOUNTPOINT   ext4   defaults  0  2" >> /etc/fstab

          fi
        done

    fi

}
