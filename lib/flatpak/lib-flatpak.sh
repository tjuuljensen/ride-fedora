#!/bin/sh
#
# Author: Torsten Juul-Jensen
# Edited: November 22, 2022 09:00
# Latest verification and tests done on Fedora 36
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

InstallAuthy(){
  flatpak install -y com.authy.Authy
}

RemoveAuthy(){
  flatpak remove -y com.authy.Authy
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

InstallGtkhsh(){
  # https://github.com/tristanheaven/gtkhash
  flatpak install -y org.gtkhash.gtkhash
}

RemoveGtkhsh(){
  flatpak remove -y org.gtkhash.gtkhash
}

InstallGhidra(){
  # https://gitlab.com/TheEvilSkeleton/Upscaler
  flatpak install -y org.ghidra_sre.Ghidra
}

RemoveGhidra(){
  flatpak remove -y org.ghidra_sre.Ghidra
}

InstallUEFItool(){
  # https://github.com/LongSoft/UEFITool
  flatpak install -y com.github.LongSoft.UEFITool
}

RemoveUEFItool(){
  flatpak remove -y com.github.LongSoft.UEFITool
}

################################################################
###### Communication ###
################################################################

InstallDiscord(){
  flatpak install -y flathub com.discordapp.Discord
}

RemoveDiscord(){
  flatpak remove -y flathub com.discordapp.Discord
}

InstallSlack(){
  flatpak install -y flathub com.slack.Slack
}

RemoveSlack(){
  flatpak remove -y flathub com.slack.Slack
}

InstallSignal(){
  flatpak install -y flathub org.signal.Signal
}

RemoveSignal(){
  flatpak remove -y flathub org.signal.Signal
}

InstallThunderbird(){
  flatpak install -y org.mozilla.Thunderbird
}

RemoveThunderbird(){
  flatpak remove -y org.mozilla.Thunderbird
}


################################################################
###### Productivity ###
################################################################

InstallXmind(){
  flatpak install -y net.xmind.XMind
}

RemoveXmind(){
  flatpak remove -y net.xmind.XMind
}

InstallColorPicker(){
  flatpak install -y nl.hjdskes.gcolor3
}

RemoveColorPicker(){
  flatpak remove -y nl.hjdskes.gcolor3
}

InstallPDFtricks(){
  flatpak install -y com.github.muriloventuroso.pdftricks
}

RemovePDFtricks(){
  flatpak remove -y com.github.muriloventuroso.pdftricks
}
