#!/bin/sh
#
# Author: Torsten Juul-Jensen
# Edited: January 19, 2019 16:00
# Latest verification and tests done on Fedora 30
#
# This file is a Fedora function library only and is meant for sourcing into other scripts
# It is a part of the github repo https://github.com/tjuuljensen/bootstrap-fedora
#

#MYUSER=$(logname)
#LOGINUSERUID=$(id -u ${MYUSER})
#MYUSERDIR=$(eval echo "~$MYUSER")

#DOWNLOADDIR=/tmp
FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number
NEXTFEDORARELEASE=$(($FEDORARELEASE+1))


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
    "https://packages.microsoft.com/config/fedora/$NEXTFEDORARELEASE/prod.repo" # microsoft repo (might not be not used)
  )

for i in ${!RELEASEREPOS[@]};
do
   wget --spider -q  ${RELEASEREPOS[$i]} && echo -e "\e[1mOK\e[0m: ${RELEASEREPOS[$i]}" || echo -e "\e[1m\e[31mFAIL\e[0m: ${RELEASEREPOS[$i]}"
done
}


InstallKernel(){
  # Install kernel headers
  # https://tutorialforlinux.com/2021/03/09/how-to-install-kernel-5-12-from-source-on-fedora-34/

  dnf group install -y "C Development Tools and Libraries"
  dnf install -y openssl-devel dwarves rpm-build

  # get the file namesudo s
  DOWNLOADURL="https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/"
  KERNELVERSION=$(uname -r)
  KERNELFILENAME=$(curl $DOWNLOADURL 2>&1 | grep -o -E 'href="([^"#]+)"' | cut -d'"' -f2 | grep $KERNELVERSION | grep gz)
  KERNELSIGNNAME=$(curl $DOWNLOADURL 2>&1 | grep -o -E 'href="([^"#]+)"' | cut -d'"' -f2 | grep $KERNELVERSION | grep sign)

  # download files
  wget $DOWNLOADURL$KERNELFILENAME -o ~/Downloads/$KERNELFILENAME
  wget $DOWNLOADURL$KERNELSIGNNAME -o ~/Downloads/$KERNELSIGNNAME

  # enter working directory
  mkdir ~/kernel
  cd ~/kernel

  # unpack kernel
  tar -xvzf ~/Downloads/$KERNELFILENAME
  cd *$KERNELVERSION

  # create config file & compile kernel packages
  find /boot/ \( -iname "*config*64" -a -iname "*`uname -r`*" \) -exec cp -i -t ./ {} \;
  make clean
  make rpm-pkg

  # check that rpm packages are there
  # ls /root/rpmbuild/RPMS/x86_64/ | grep kernel

  # install package
  dnf install -y /root/rpmbuild/RPMS/x86_64/kernel*.rpm

  reboot

}
