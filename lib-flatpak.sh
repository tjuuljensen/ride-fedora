#!/bin/sh
#
# Author: Torsten Juul-Jensen
# Edited: February 17, 2020 17:30
# Latest verification and tests done on Fedora 31
#
# This file is a Fedora function library only and is meant for sourcing into other scripts
# It is a part of the github repo https://github.com/tjuuljensen/bootstrap-fedora
#

MYUSER=$(logname)
LOGINUSERUID=$(id -u ${MYUSER})
DOWNLOADDIR=/tmp
FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number
MYUSERDIR=$(eval echo "~$MYUSER")


################################################################
###### Flatpak & Flathub ###
################################################################

InstallFlatpak(){
  # Flatpak Install (user context)
  dnf install -y flatpak
}

RemoveFlatpak(){
  flatpak uninstall --all
  dnf autoremove -y flatpak
}

InstallFlathub(){
  flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
}

RemoveFlathub(){
  flatpak uninstall flathub
}



################################################################
###### Multimedia ###
################################################################

InstallSpotifyClient(){
  # install Spotify client
  # See details and firewall config here http://negativo17.org/spotify-client/
  flatpak install -y flathub com.spotify.Client
}

RemoveSpotifyClient(){
  # remove Spotify client
  flatpak remove -y flathub com.spotify.Client
}

InstallVLCPlayer(){
  # install VLC player
  # installed from rpmfusion-free-updates repo
  flatpak install -y flathub org.videolan.VLC
}

RemoveVLCPlayer(){
  # remove VLC player
  flatpak remove -y flathub org.videolan.VLC
}

InstallClementinePlayer(){
  # install clementine media player & pulseaudio equalizer
  flatpak install -y flathub org.clementine_player.Clementine
}

RemoveClementinePlayer(){
  # install clementine media player & pulseaudio equalizer
  flatpak remove -y flathub org.clementine_player.Clementine
}


################################################################
###### Gnome Tools & Tweaks ###
################################################################


InstallGnomeExtensions(){
  # Install Gnome extensions
  # flatpak install flathub org.gnome.Extensions -y
  dnf install -y gnome-extensions-app
  dnf install -y chrome-gnome-shell # Gnome integration for browsers

  GNOMEEXTENSIONS=(
    2    # move-clock - https://extensions.gnome.org/extension/2/move-clock/
    4135  # Espresso - https://extensions.gnome.org/extension/4135/espresso/
    615  # AppIndicator Support - https://extensions.gnome.org/extension/615/appindicator-support/
    1401 # bluetooth-quick-connect/ - https://extensions.gnome.org/extension/1401/bluetooth-quick-connect/
    4141 # username and hostname in top bar - https://extensions.gnome.org/extension/4141/add-userhost-to-panel/

    # The following are disabled after Fedora 34 with Gnome 40
    #1166 # Extension Update Notifier - https://extensions.gnome.org/extension/1166/extension-update-notifier/
    #1018 # Text scaler - https://extensions.gnome.org/extension/1018/text-scaler/
    #307  # Dash-to-dock - https://extensions.gnome.org/extension/307/dash-to-dock/
    #1465 # Desktop Icons - https://extensions.gnome.org/extension/1465/desktop-icons/
    #517  # Caffeine - https://extensions.gnome.org/extension/517/caffeine/
    #15   # Alternate Tab - https://extensions.gnome.org/extension/15/alternatetab/
    #120  # System Monitor - https://github.com/paradoxxxzero/gnome-shell-system-monitor-applet
  )

  # Install using gnome-shell-extension-installer script
  if ( command -v gnome-shell-extension-installer > /dev/null 2>&1 ) ; then
    for GNOMEEXTENSION in "${GNOMEEXTENSIONS[@]}"
    do
      sudo -u $MYUSER gnome-shell-extension-installer $GNOMEEXTENSION --restart-shell
    done
  fi

}

RemoveGnomeExtensions(){
  # Remove Gnome extensions
  if ( command -v gnome-shell-extension-installer > /dev/null 2>&1 ) ; then
    rm "/home/$MYUSER/.local/share/gnome-shell/extensions/Move_Clock@rmy.pobox.com"
    #rm "/home/$MYUSER/.local/share/gnome-shell/extensions/caffeine@patapon.info"
    #rm "/home/$MYUSER/.local/share/gnome-shell/extensions/ScaleSwitcher@jabi.irontec.com"

    # restart gnome shell is not available under Wayland
    [[ $XDG_SESSION_TYPE != "wayland" ]] && gnome-shell-extension-installer --restart-shell
  fi

}
