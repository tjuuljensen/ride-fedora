#!/bin/sh
#
# Author: Torsten Juul-Jensen
# Edited: October 27, 2022 14:00
# Latest verification and tests done on Fedora 36
#
# This file is a Fedora function library only and is meant for sourcing into other scripts
# It is a part of the github repo https://github.com/tjuuljensen/bootstrap-fedora
#

# Declare variables
if [ -z $SCRIPT_VARSSET ] ; then
  # if the vars are not exported to bash from another shell script, set variables in this scope (in the case the script is sourced)
  FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number
  let NEXTFEDORARELEASE=FEDORARELEASE+1
  SCRIPTDIR=$( dirname $( realpath "${BASH_SOURCE[0]}" )) #set the variable to the place where script is loaded from
  WORKDIR=$(pwd)
  MYUSER=$(logname)
  LOGINUSERUID=$(id -u ${MYUSER})
  DOWNLOADDIR=/tmp
  MYUSERDIR=$(eval echo "~$MYUSER")
else # if the bash variables are set from a parent script
  # set local variables from the exported bash variables
  FEDORARELEASE=$SCRIPT_FEDORARELEASE
  let NEXTFEDORARELEASE=FEDORARELEASE+1
  SCRIPTDIR=$SCRIPT_SCRIPTDIR
  WORKDIR=$SCRIPT_WORKDIR
  MYUSER=$SCRIPT_MYUSER
  LOGINUSERUID=$SCRIPT_LOGINUSERUID
  DOWNLOADDIR=$SCRIPT_DOWNLOADDIR
  MYUSERDIR=$SCRIPT_MYUSERDIR
fi


################################################################
###### Upgrade Fedora ###
################################################################

CheckNextVersionRepos(){
  # check if the repos used in the code library are available - testing {Fedoraversion+1} for rpmfusion

  CODE_LIBRARY="lib-fedora.sh"

  if [[ ! -f ${CODE_LIBRARY} ]] ; then
    [[ -f "${SCRIPTDIR}/${CODE_LIBRARY}" ]] && CODE_LIBRARY="${SCRIPTDIR}/${CODE_LIBRARY}"
  fi

  if [ -f ${CODE_LIBRARY} ] ; then

    RELEASEREPOS=(  )
    RELEASEREPOS+=( $(grep "http.*\.rpmfusion.*$" ${CODE_LIBRARY}  | cut -d"=" -f2 | sed "s/\$FEDORARELEASE/$NEXTFEDORARELEASE/g") )
    RELEASEREPOS+=( $(grep "http.*\.repo$" ${CODE_LIBRARY}  | cut -d"=" -f2 | sed "s/\$FEDORARELEASE/$NEXTFEDORARELEASE/g") )

    for i in ${!RELEASEREPOS[@]};
    do
       if wget --spider -q  ${RELEASEREPOS[$i]} ; then
          echo -e "\e[1mOK\e[0m: ${RELEASEREPOS[$i]}"
        else
          echo -e "\e[1m\e[31mFAIL\e[0m: ${RELEASEREPOS[$i]}"
          ERRFLAG=1
        fi
    done
    [[ ! -z ${ERRFLAG} ]] && exit 2
  else
    echo "File ${CODE_LIBRARY} not found"
    exit 2
  fi
  exit 0
}


UpgradeFedora(){
  # next release upgrade fedora
  dnf upgrade -y --refresh
  dnf install -y dnf-plugin-system-upgrade
  dnf system-upgrade download -y --releasever=$NEXTFEDORARELEASE
  dnf system-upgrade -y reboot
}


################################################################
###### Upgrade helper ###
################################################################

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

  cd $DOWNLOADDIR

  # download files
  if [ ! -f $LOCALKERNELFILE ] ; then
    wget -q --show-progress $DOWNLOADURL$KERNELFILENAME -O $LOCALKERNELFILE
    wget -q --show-progress $DOWNLOADURL$KERNELSIGNNAME -O $LOCALKRNLSIGNFILE

    chown $MYUSER:$MYUSER $LOCALKERNELFILE
    chown $MYUSER:$MYUSER $LOCALKRNLSIGNFILE
  fi

  # enter working directory (/root)
  mkdir -p /root/kernel
  cd  /root/kernel

  # unpack kernel
  tar -xvzf $LOCALKERNELFILE --overwrite
  cd *$KERNELVERSION

  # create config file & compile kernel packages
  find /boot/ \( -iname "*config*64" -a -iname "*`uname -r`*" \) -exec cp -i -t ./ {} \;
  mv *`uname -r`* .config

  make clean
  make rpm-pkg

  # check that rpm packages are there
  # ls /root/rpmbuild/RPMS/x86_64/ | grep kernel

  KERNELHEADERFILES=$(find /root/rpmbuild/RPMS/x86_64/ -name kernel-headers-$KERNELVERSION*.rpm)

  if [ ! -z $KERNELHEADERFILES ] ; then
    # install package
    dnf install -y /root/rpmbuild/RPMS/x86_64/kernel-headers-$KERNELVERSION*.rpm

    # verify that installed kernel-devel file matches
    KERNELDEVELVERSION=$(rpm -qa kernel-devel | cut -d"-" -f3 | grep $KERNELVERSION) #Installed kernel-devel version
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
  else
    echo "Something went wrong. Please go investigate what happened..."
  fi

}
