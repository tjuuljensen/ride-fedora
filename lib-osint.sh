#!/bin/sh
#
# Author: Torsten Juul-Jensen
# Edited: July 22, 2020 16:30
# Latest verification and tests done on Fedora XX
#
# This file is a Fedora function library only and is meant for sourcing into other scripts
# It is a part of the github repo https://github.com/tjuuljensen/bootstrap-fedora
#


MYUSER=$(logname)
LOGINUSERUID=$(id -u ${MYUSER})
DOWNLOADDIR=/tmp
FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number
MYUSERDIR=$(eval echo "~$MYUSER")


InstallTheHarvester(){
  # https://github.com/laramies/theHarvester
}

RemoveTheHarvester(){

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
