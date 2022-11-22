#!/bin/sh
#
# Author: Torsten Juul-Jensen
# Edited: October 25, 2022 13:00
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
###### Forensics ###
################################################################

GetRemnuxVmware(){
  # https://docs.remnux.org/install-distro/get-virtual-appliance
  #Download from sourceforge as box.com requires box CLI installation
  URL=https://docs.remnux.org/install-distro/get-virtual-appliance
  DOWNLOADURL=$(curl $URL  2>&1 |  grep -Eoi 'href="([^"#]+)"'  | cut -d'"' -f2 | grep sourceforge | grep -v virtualbox)

  cd $DOWNLOADDIR
  wget --content-disposition -N -q --show-progress $DOWNLOADURL
}

GetRemnuxVbox(){
  # https://docs.remnux.org/install-distro/get-virtual-appliance
  #Download from sourceforge as box.com requires box CLI installation
  URL=https://docs.remnux.org/install-distro/get-virtual-appliance
  DOWNLOADURL=$(curl $URL  2>&1 |  grep -Eoi 'href="([^"#]+)"'  | cut -d'"' -f2 | grep sourceforge | grep virtualbox)

  cd $DOWNLOADDIR
  wget --content-disposition -N -q --show-progress $DOWNLOADURL
}

GetKaliVMware () {
  cd $DOWNLOADDIR
  IMAGEURL=https://kali.download/virtual-images/current/
  SUBURL=$(curl $IMAGEURL 2>&1 | grep -Eoi '<a [^>]+>' | cut -d'"' -f2 | grep vmware-amd64 | grep -v torrent )
  URL=${IMAGEURL}${SUBURL}
  sudo -u $MYUSER wget -q --show-progress -P $DOWNLOADDIR/ $URL
  sudo -u $MYUSER wget -q --show-progress -P $DOWNLOADDIR/ ${IMAGEURL}SHA256SUMS
}

GetKaliVbox () {
  cd $DOWNLOADDIR
  IMAGEURL=https://kali.download/virtual-images/current/
  SUBURL=$(curl $IMAGEURL 2>&1 | grep -Eoi '<a [^>]+>' | cut -d'"' -f2 | grep virtualbox-amd64 | grep -v torrent )
  URL=${IMAGEURL}${SUBURL}
  sudo -u $MYUSER wget -q --show-progress -P $DOWNLOADDIR/ $URL
  sudo -u $MYUSER wget -q --show-progress -P $DOWNLOADDIR/ ${IMAGEURL}SHA256SUMS
}

GetSANSsift(){
  # SANS Sift image is behind login at https://www.sans.org/tools/sift-workstation/
  URL=https://www.sans.org/tools/sift-workstation/

  # Make checks & fix leftover lock files
  # FFOX_PS_RUNNING=$(ps -aux | grep firefox | wc -l) # returns 1 if no ffox processes are running
  # if [[ $FFOX_PS_RUNNING -ne 1 ]] ; then
    # pkill firefox
    # sudo -u $MYUSER find ~/.mozilla -name "*lock" -delete
  # fi

  nohup runuser -l $MYUSER -c "export DISPLAY=""":0""" && xdg-open ${URL} 2>&1 &" > /dev/null &

  echo Please download SIFT image manually from browser page.
  echo Opening URL in user context: ${URL}
  return 0

}

GetSOFelk () {
  cd $DOWNLOADDIR
  URL=https://for572.com/sof-elk-vm
  DOWNLOADURL=$(curl -I $URL  2>&1 | grep Location | cut -d ' ' -f2)
  BINARYFILENAME=${DOWNLOADURL##*/}

  wget --content-disposition -N -q --show-progress -o $DOWNLOADDIR/$BINARYFILENAME $URL

}
