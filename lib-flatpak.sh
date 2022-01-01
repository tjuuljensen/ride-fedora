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
  flatpak install -y org.gnome.Extensions
}

RemoveGnomeExtensions(){
  flatpak remove -y org.gnome.Extensions 
}
