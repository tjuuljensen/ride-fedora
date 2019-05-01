#!/bin/sh
# script will automatically escalate to root privileges. Do not run as root
# last edited: April 16, 2019 11:32

MYUSER=$(logname)
DOWNLOADDIR=/home/$MYUSER/Downloads
FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number

#######################################
# define URL locations of packages and scripts
# Filespecific URLs
RPMFUSIONURL=http://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$FEDORARELEASE.noarch.rpm
RPMFUSIONNONFREEURL=https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$FEDORARELEASE.noarch.rpm
VERACRYPTURL=https://launchpad.net/veracrypt/trunk/1.23/+download/veracrypt-1.23-setup.tar.bz2 #downloads/get/1601964
CITRIXCLIENTURL=https://www.citrix.dk/downloads/citrix-receiver/linux/receiver-for-linux-latest.html
FTKURL=https://ad-zip.s3.amazonaws.com/ftkimager.3.1.1_fedora64.tar.gz
# General URLs
VMWAREURL=https://www.vmware.com/go/getworkstation-linux
FEDYURL=http://folkswithhats.org/fedy-installer
ATOMURL=https://atom.io/download/rpm
#ATOMREPO=https://copr.fedorainfracloud.org/coprs/helber/atom/repo/fedora-$FEDORARELEASE/helber-atom-fedora-$FEDORARELEASE.repo
# Script URLs
GNMEXTSCRIPT=https://github.com/ianbrunelli/gnome-shell-extension-installer/raw/master/gnome-shell-extension-installer
MOZEXTMGRSCRIPT=https://raw.githubusercontent.com/NicolasBernaerts/ubuntu-scripts/master/mozilla/mozilla-extension-manager
FFOXEXTMGRSCRIPT=https://raw.githubusercontent.com/NicolasBernaerts/ubuntu-scripts/master/mozilla/firefox-extension-manager
TECMINTMONSCRIPT=http://tecmint.com/wp-content/scripts/tecmint_monitor.sh
#######################################
# extract binary information from URL's using substring manipulation
FTKPKG=${FTKURL##${FTKURL%/*}"/"}
############################################

_confirm () {
  # prompt user for confirmation. Default is No
    read -r -p "${1:-Do you want to proceed? [y/N]} " RESPONSE
    RESPONSE=${RESPONSE,,}
    if [[ $RESPONSE =~ ^(yes|y| ) ]]
      then
        true
      else
        false
    fi
}

_disableScreensaver(){
  # disable screensaver
  su $MYUSER -c "gsettings set org.gnome.desktop.screensaver idle-activation-enabled 'false'"
  su $MYUSER -c "gsettings set org.gnome.desktop.screensaver lock-enabled 'false'"
  su $MYUSER -c "gsettings set org.gnome.desktop.session idle-delay 0"
}

_updateFedora(){
  # update fedora
  echo Updating Fedora...
  dnf update -y
}

_installRPMfusion(){
  # install rpmfusion
  echo
  echo Installing RPMfusion
  dnf install -y $RPMFUSIONURL
  dnf install -y $RPMFUSIONNONFREEURL
}

_installBasicTools(){
  # install basic tools
  echo
  echo Installing basic tools...
  dnf install -y putty gparted keepassx thunderbird gpg gnome-tweak-tool nano gnome-commander mc remmina vim  chromium
  dnf install -y gcc kernel-devel kernel-headers
  dnf install -y dia flow-tools tcpdump wireshark-gnome tftp-server hexchat minicom pidgin pidgin-otr pv nmap macchanger
  dnf install -y NetworkManager-l2tp NetworkManager-l2tp-gnome

  # install system-config-printer for installing printers in fedora (add printers by running system-config-printer)
  dnf install -y system-config-printer
}

_installFedy(){
  # Installing fedy
  echo
  echo Installing fedy
  # From https://www.folkswithhats.org/
  dnf install https://dl.folkswithhats.org/fedora/$(rpm -E %fedora)/RPMS/fedy-release.rpm
  dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
  dnf install fedy
}

_installForensicsTools(){
  # install exfat utils (depends on RPMfusion)
  echo
  echo Installing exfat utilities
  dnf -y install exfat-utils fuse-exfat

  # install libewf - a library for access to EWF (Expert Witness Format)
  # See more at https://github.com/libyal/libewf
  # sleuthkit added
  echo
  echo Installing libewf
  dnf -y install libewf sleuthkit

  # download ftkimager from AccessSoftware and put it in /usr/bin
  echo
  echo Installing ftkimager
  cd $DOWNLOADDIR
  wget $FTKURL
  tar xzvf $FTKPKG -C /usr/bin/
  chown $MYUSER:$MYUSER $FTKPKG

  # install ExifTool
  echo
  echo Installing ExifTool
  dnf -y install perl-Image-ExifTool

}

_installAtomEditor(){
  # install atom editor
  echo
  echo Installing atom editor
  cd $DOWNLOADDIR
  #wget -O /etc/yum.repos.d/helber-atom-fedora-$FEDORARELEASE.repo $ATOMREPO
  #dnf install -y atom
  wget -O atom.x86_64.rpm $ATOMURL
  dnf install -y atom.x86_64.rpm
  chown $MYUSER:$MYUSER atom.x86_64.rpm
}

_installScripts(){
  # get script for gnome extension installation
  # see more at http://www.bernaerts-nicolas.fr/linux/76-gnome/345-gnome-shell-install-remove-extension-command-line-script
  # Source from https://github.com/brunelli/gnome-shell-extension-installer
  echo
  echo Fetching gnome extension installation script
  wget -O /usr/local/bin/gnome-shell-extension-installer $GNMEXTSCRIPT
  chmod +x /usr/local/bin/gnome-shell-extension-installer

  # get tecmint montor script
  echo
  echo Fetching tecmit monitor script
  wget -O /usr/local/bin/tecmint_monitor.sh $TECMINTMONSCRIPT
  chmod 755 /usr/local/bin/tecmint_monitor.sh

  # get mozilla xpi installation script
  echo
  echo Fetching mozilla extension installation script
  wget -O /usr/local/bin/mozilla-extension-manager $MOZEXTMGRSCRIPT
  chmod 755 /usr/local/bin/mozilla-extension-manager
  wget -O /usr/local/bin/firefox-extension-manager $FFOXEXTMGRSCRIPT
  chmod 755 /usr/local/bin/firefox-extension-manager
}

_installChrome(){
  # download and install chrome and it's dependencies
  echo
  echo Enabling Google repo and installing Google Chrome

  CHROMEREPO=/etc/yum.repos.d/google-chrome.repo
  #touch $CHROMEREPO

cat << 'EOF' > $CHROMEREPO
[google-chrome]
name=google-chrome - $basearch
baseurl=http://dl.google.com/linux/chrome/rpm/stable/$basearch
enabled=1
gpgcheck=1
gpgkey=https://dl-ssl.google.com/linux/linux_signing_key.pub
EOF

  dnf install -y google-chrome-stable
}

_createFirefoxPreferenceFiles() {
  #Creates config files for firefox

  FIREFOXINSTALLDIR=/usr/lib64/firefox/

cat << 'EOF1'  > $FIREFOXINSTALLDIR"mozilla.cfg"
//
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
pref("extensions.pocket.enabled", false);
EOF1

  # Create the autoconfig.js file
cat << 'EOF2' > $FIREFOXINSTALLDIR"defaults/pref/autoconfig.js"
pref("general.config.obscure_value", 0);
pref("general.config.filename", "mozilla.cfg");
EOF2

  # Create the override.ini file (disables Migration Wizard)
cat << 'EOF3' > $FIREFOXINSTALLDIR"browser/override.ini"
[XRE]
EnableProfileMigrator=false
EOF3
}

_createChromePreferenceFiles(){

  CHROMEINSTALLDIR=/opt/google/chrome/

  # Create the master_preferences file
  # File contents based on source fils: https://src.chromium.org/viewvc/chrome/trunk/src/chrome/common/pref_names.cc
cat << 'EOF4' > $CHROMEINSTALLDIR"master_preferences"
{
 "homepage" : "https://encrypted.google.com",
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
   "http://encrypted.google.com",
   "welcome_page",
   "new_tab_page"
 ]
}
EOF4

}

_installOpenconnect(){
  # OpenConnect for use with Juniper VPN
  sudo dnf install -y automake libtool openssl-devel libxml2 libxml2-devel vpnc-script NetworkManager-openconnect-gnome
  su $MYUSER -c 'mkdir ~/git_projects ; cd ~/git_projects ;  git clone git://git.infradead.org/users/dwmw2/openconnect.git ; cd openconnect/ ; ./autogen.sh ; ./configure --with-vpnc-script=/etc/vpnc/vpnc-script --without-openssl-version-check --prefix=/usr/ --disable-nls ; make'
  make install
}

_installTerminator(){
  echo
  echo Installing terminator
  dnf -y install terminator
}

_installWine(){
  dnf install -y wine
}

_installPackagingTools(){
  # install 7zip and dependencies
  echo
  echo Installing 7zip and unrar #its dependencies
  dnf install -y p7zip unrar
}

_installMultimediaTools(){
  # install Spotify client
  # See details and firewall config here http://negativo17.org/spotify-client/
  echo
  echo Installing Spotify client
  dnf config-manager --add-repo=http://negativo17.org/repos/fedora-spotify.repo
  dnf install -y spotify-client

  # install VLC player
  # installed from rpmfusion-free-updates repo
  echo Installing VLC Player
  dnf install -y vlc

  # install clementine media player & pulseaudio equalizer
  echo
  echo Installing clementine
  dnf -y install clementine gstreamer-plugins-ugly gstreamer-plugins-bad gstreamer-plugins-good pulseaudio

  # install Youtube Downloader
  echo
  echo Installing YouTube downloader
  dnf -y install youtube-dl
}

_installLaptopTools(){

  #Check if machine is a ThinkPad
  if [ $( dmidecode -s system-version | grep ThinkPad -i | wc -l ) -ne 0 ] ; then
  # install the thinkfan program
    echo
    echo Installing Thinkfan
    dnf -y install thinkfan
    systemctl enable thinkfan.service # enable service

  fi

  # install the Logitech Unifying Receiver on laptop
  # if the machine has a battery (it is probably a laptop), install
  if [ $( dmidecode |grep Battery -i | wc -l) -ne 0 ] ; then
    echo
    echo Battery found - Installing Logitech Unifying Receiver and ACPI
    dnf install -y solaar acpi
  fi
}

_installVMtools(){
  # if a virtual machine, install open-vm-tools
  # for more virtualization vendors check here http://unix.stackexchange.com/questions/89714/easy-way-to-determine-virtualization-technology
  if [ $( dmidecode -s system-product-name | grep -i VMware | wc -l ) -ne 0 ] ; then
    dnf -y install open-vm-tools
  fi
}

_installCheat(){
  # install cheat sheet - http://www.tecmint.com/cheat-command-line-cheat-sheet-for-linux-users/
  dnf install -y python python-pip
  pip install --upgrade pip
  pip install docopt pygments
  mkdir -p /home/$MYUSER/git_projects
  cd /home/$MYUSER/git_projects
  su $MYUSER -c "git clone https://github.com/chrisallenlane/cheat.git"
  cd cheat
  python setup.py install
}

_installCitrixClient(){
  # Citrix Client - must be downloaded using browser
  # a litte notes from the Ubuntu people https://help.ubuntu.com/community/CitrixICAClientHowTo
  echo
  echo Download Citrix Client from URL below - using a browser - and put it in the default Downloads folder.
  echo Opening Firefox at: $CITRIXCLIENTURL
  su $MYUSER -c "firefox -new-window $CITRIXCLIENTURL"
  if _confirm "Continue after downloading the file... [yN]" ; then
    dnf -y install ICA*.rpm
  fi
}

_installOwnCloudClient(){
  # OwnCloud client
  dnf config-manager --add-repo http://download.opensuse.org/repositories/isv:ownCloud:desktop/Fedora_$FEDORARELEASE/isv:ownCloud:desktop.repo
  dnf install -y owncloud-client
}

_installSystemMonitor(){
  # install system monitor dependecies
  dnf install -y libgtop2-devel NetworkManager-glib-devel
  dnf install -y lm_sensors #for fan overview
}

_installVeraCrypt(){
  # download and install veracrypt archive

  #VERACRYPTPKG=veracrypt-setup.tar.bz2

  echo
  echo Downloading and installing VeraCrypt
  echo
  cd $DOWNLOADDIR
  wget $VERACRYPTURL
    VERACRYPTPKG=$(ls veracrypt*)
    tar xvjf $VERACRYPTPKG -C /tmp veracrypt-*-setup-gui-x64 #extract only the x64 bit console installer
    mv /tmp/veracrypt-*-setup-gui-x64  /tmp/veracrypt-setup-gui-x64
    /tmp/veracrypt-setup-gui-x64
  #fi
}

_installVMwareWorkstation(){
  # download and install vmware workstation
  echo
  echo Downloading and installing VMware Workstation
  echo Starting with prerequisites
  dnf -y install elfutils-libelf-devel
  cd $DOWNLOADDIR
  su $MYUSER -c "wget --content-disposition -O vmware-installer.bundle $VMWAREURL"
  chmod +x vmware-installer.bundle # $VMWAREBIN
  ./vmware-installer.bundle --required --console # /$VMWAREBIN --required --console
  # add serial number
  echo NOTICE!!!
  echo "This applies to VMWare 14 and above:"
  echo "1. Under Wayland (default in Fedora) it can be tricky to register serials. Please change to X if you have problems."
  echo "2. Remember to disable Secure boot in host BIOS - otherwise VM's can't start."
}

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

_setHostname(){
  # set hostname
  echo
  echo Current hostname is $HOSTNAME
  read -r -p "Enter NEW hostname: " NEWHOSTNAME
  hostnamectl set-hostname --static "$NEWHOSTNAME"

}

_enableScreenSaver(){
  # enable screensaver
  echo
  echo Enabling ScreenSaver
  echo
  su $MYUSER -c "gsettings set org.gnome.desktop.screensaver idle-activation-enabled 'true'"
  su $MYUSER -c "gsettings set org.gnome.desktop.screensaver lock-enabled 'true'"
  su $MYUSER -c "gsettings set org.gnome.desktop.session idle-delay 300"
}

_dnsConfig(){
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

#### MAIN #######################################

# elevate privileges to root
[ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"
echo

_disableScreensaver

_updateFedora
_installRPMfusion
_installBasicTools

_installFedy
_installForensicsTools
_installAtomEditor
_installScripts

_installChrome
_createFirefoxPreferenceFiles
_createChromePreferenceFiles

_installOpenconnect
_installTerminator
_installWine
_installPackagingTools
_installMultimediaTools

_installLaptopTools
_installVMtools
_installCheat

_confirm "Do you want to install Citrix Client? [yN]" && _installCitrixClient
_confirm "Do you want to install the OwnCloud Client? [yN]" && _installOwnCloudClient
_confirm "Do you want to install tools for System Monitor? [yN]" && _installSystemMonitor
_confirm "Do you want to install VeraCrypt? [yN]" && _installVeraCrypt
_confirm "Do you want to install VMware Workstation? [yN]" && _installVMwareWorkstation
_confirm "Do you want to add a LUKS key? [yN] " && _addLUKSpassword
_confirm "Do you want to change hostname from $HOSTNAME? [yN] " && _setHostname
_confirm "Do you want to change DNS config (disable Multicast DNS)? [yN]" && _dnsConfig

_enableScreenSaver

_confirm "Do you want to reboot? [yN]" && reboot
#_confirm "Do you want to run usr script? [yN]" && sudo su ...
#####################################################
