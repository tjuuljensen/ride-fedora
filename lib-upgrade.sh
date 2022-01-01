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
MYUSERDIR=$(eval echo "~$MYUSER")

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

  if [ -f lib-fedora.sh ] ; then

    RELEASEREPOS=(  )
    RELEASEREPOS+=( $(grep "http.*\.noarch.rpm$" lib-fedora.sh  | cut -d"=" -f2 | sed "s/\$FEDORARELEASE/$NEXTFEDORARELEASE/g") )
    RELEASEREPOS+=( $(grep "http.*\.repo$" lib-fedora.sh  | cut -d"=" -f2 | sed "s/\$FEDORARELEASE/$NEXTFEDORARELEASE/g") )

    for i in ${!RELEASEREPOS[@]};
    do
       wget --spider -q  ${RELEASEREPOS[$i]} && echo -e "\e[1mOK\e[0m: ${RELEASEREPOS[$i]}" || echo -e "\e[1m\e[31mFAIL\e[0m: ${RELEASEREPOS[$i]}"
    done
  else
    echo "File lib-fedora.sh not found"
  fi
}


InstallKernelHeaders(){
  # Install kernel headers
  # https://tutorialforlinux.com/2021/03/09/how-to-install-kernel-5-12-from-source-on-fedora-34/

  dnf group install -y "C Development Tools and Libraries"
  dnf install -y openssl-devel dwarves rpm-build

  # get the file namesudo s
  KERNELVERSION=$(uname -r | cut -d "-" -f1)
  MAJORKERNELVER="${KERNELVERSION%%\.*}"
  DOWNLOADURL="https://mirrors.edge.kernel.org/pub/linux/kernel/v$MAJORKERNELVER.x/"

  KERNELFILENAME=$(curl $DOWNLOADURL 2>&1 | grep -o -E 'href="([^"#]+)"' | cut -d'"' -f2 | grep $KERNELVERSION | grep gz)
  KERNELSIGNNAME=$(curl $DOWNLOADURL 2>&1 | grep -o -E 'href="([^"#]+)"' | cut -d'"' -f2 | grep $KERNELVERSION | grep sign)

  LOCALKERNELFILE=$MYUSERDIR/Downloads/$KERNELFILENAME
  LOCALKRNLSIGNFILE=$MYUSERDIR/Downloads/$KERNELSIGNNAME

  # download files
  if [ ! -f $LOCALKERNELFILE ] ; then
    wget -q --show-progress $DOWNLOADURL$KERNELFILENAME -O $LOCALKERNELFILE
    wget -q --show-progress $DOWNLOADURL$KERNELSIGNNAME -O $LOCALKRNLSIGNFILE

    chown $MYUSER:$MYUSER $LOCALKERNELFILErpm -qa kernel-devel | cut -d"-" -f3
    chown $MYUSER:$MYUSER $LOCALKRNLSIGNFILE
  fi

  # enter working directory (/root)
  mkdir -p /root/kernel
  cd  /root/kernel

  # unpack kernel
  tar -xvzf --overwrite $LOCALKERNELFILE
  cd *$KERNELVERSION

  # create config file & compile kernel packages
  find /boot/ \( -iname "*config*64" -a -iname "*`uname -r`*" \) -exec cp -i -t ./ {} \;
  mv *`uname -r`* .config

  make clean
  make rpm-pkg

  # check that rpm packages are there
  # ls /root/rpmbuild/RPMS/x86_64/ | grep kernel

  # install package
  dnf install -y /root/rpmbuild/RPMS/x86_64/kernel-headers-$KERNELVERSION*.rpm

  # verify that nstalled kernel-devel file matches
  KERNELDEVELVERSION=$(rpm -qa kernel-devel | cut -d"-" -f3) #Installed kernel-devel version
  if [ $KERNELDEVELVERSION != $KERNELVERSION ] ; then
      dnf remove -y kernel-devel
      dnf install -y kernel-devel-$KERNELVERSION
  fi

  echo -n Rebooting in 10 seconds...
  for ((i=1;i<=10;++i))
  do
      echo -n $i
      sleep 0.5
      echo -n "."
      sleep 0.5
  done
  echo
  echo Rebooting now!
  sleep 2

  reboot

}
