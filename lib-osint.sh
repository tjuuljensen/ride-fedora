#!/bin/sh
#
# Author: Torsten Juul-Jensen
# Edited: July 22, 2020 16:30
# Latest verification and tests done on Fedora XX
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

TestFunction(){
  echo $SCRIPTDIR
}

InstallTheHarvester(){
  # https://github.com/laramies/theHarvester
}

RemoveTheHarvester(){

}

InstallYETI(){
  # https://github.com/yeti-platform/yeti
}

RemoveYETI(){

}

InstallSpiderFoot(){
  # https://github.com/smicallef/spiderfoot
  # Install Development branch

  # UNTESTED - FIXME!!!

  # Check if git library exists and create if it doesn't
  if [ ! -d $MYUSERDIR/git ] ; then
    cd $MYUSERDIR
    mkdir -p git > /dev/null
    chown $MYUSER:$MYUSER git
  fi

  su $MYUSER -c "cd $MYUSERDIR/git ; git clone https://github.com/smicallef/spiderfoot.git"
  cd spiderfoot
  sudo -u $MYUSER pip3 install -r requirements.txt
  #  python3 ./sf.py -l 127.0.0.1:5001
}

RemoveSpiderFoot(){

}
