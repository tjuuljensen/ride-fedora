#!/bin/sh
#
# Author: Torsten Juul-Jensen
# Edited: January 1, 2021 09:00
# Latest verification and tests done on Fedora 31
#
# This file is a Fedora function library only and is meant for sourcing into other scripts
# It is a part of the github repo https://github.com/tjuuljensen/bootstrap-fedora
#

# Declare variables
if [ -z $SCRIPT_VARSSET ] ; then
  # if the vars are not exported to bash from another shell script, set variables in this scope (in the case the script is sourced)
  FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number
  SCRIPTDIR=$( dirname $( realpath "${BASH_SOURCE[0]}" )) #set the variable to the place where script is loaded from
  WORKDIR=$(pwd)
  MYUSER=$(logname)
  LOGINUSERUID=$(id -u ${MYUSER})
  DOWNLOADDIR=/tmp
  MYUSERDIR=$(eval echo "~$MYUSER")
else # if the bash variables are set from a parent script
  # set local variables from the exported bash variables
  FEDORARELEASE=$SCRIPT_FEDORARELEASE
  SCRIPTDIR=$SCRIPT_SCRIPTDIR
  WORKDIR=$SCRIPT_WORKDIR
  MYUSER=$SCRIPT_MYUSER
  LOGINUSERUID=$SCRIPT_LOGINUSERUID
  DOWNLOADDIR=$SCRIPT_DOWNLOADDIR
  MYUSERDIR=$SCRIPT_MYUSERDIR
fi

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

################################################################
###### Offensive Tools ###
################################################################

InstallJohn(){
  flatpak install -y com.openwall.John
}

RemoveJohn(){
  flatpak remove -y com.openwall.John
}

################################################################
###### Forensic Tools ###
################################################################

InstallUpscaler(){
  # https://gitlab.com/TheEvilSkeleton/Upscaler
  flatpak install -y io.gitlab.theevilskeleton.Upscaler
}

RemoveUpscaler(){
  flatpak remove -y io.gitlab.theevilskeleton.Upscaler
}


################################################################
###### Productivity ###
################################################################

InstallThunderbird(){
  flatpak install -y org.mozilla.Thunderbird
}

RemoveThunderbird(){
  flatpak remove -y org.mozilla.Thunderbird
}
