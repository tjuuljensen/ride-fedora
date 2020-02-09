#!/bin/sh
#
# Author: Torsten Juul-Jensen
# Edited: January 19, 2019 16:00
# Latest verification and tests done on Fedora 30
#
# This file is a Fedora function library only and is meant for sourcing into other scripts
# It is a part of the github repo https://github.com/tjuuljensen/bootstrap-fedora
#

MYUSER=$(logname)
LOGINUSERUID=$(id -u ${MYUSER})
DOWNLOADDIR=/tmp
FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number
NEXTFEDORARELEASE=$(($FEDORARELEASE+1))
MYUSERDIR=/home/$MYUSER


################################################################
###### Upgrade Fedora ###
################################################################

UpgradeFedora(){
  # next release upgrade fedora
  dnf upgrade -y --refresh
  dnf install -y dnf-plugin-system-upgrade
  dnf system-upgrade download -y --releasever=$NEXTFEDORARELEASE
  dnf system-upgrade -y reboot

}

CheckNextVersionRepos(){

  RELEASEREPOS=(
    "http://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$NEXTFEDORARELEASE.noarch.rpm" # rpmfusion free
    "https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$NEXTFEDORARELEASE.noarch.rpm" # rpmfusion non-free
    "http://download.opensuse.org/repositories/isv:ownCloud:desktop/Fedora_$NEXTFEDORARELEASE/isv:ownCloud:desktop.repo"  # owncloud
    "MSFEDORAREPO=https://packages.microsoft.com/config/fedora/$NEXTFEDORARELEASE/prod.repo" # microsoft repo (might not be not used)
  )

for i in ${!RELEASEREPOS[@]};
do
   wget --spider -q  ${RELEASEREPOS[$i]} && echo -e "\e[1mOK\e[0m: ${RELEASEREPOS[$i]}" || echo -e "\e[1m\e[31mFAIL\e[0m: ${RELEASEREPOS[$i]}"
done

}
