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


InstallTheHarvester(){
  # https://github.com/laramies/theHarvester

  cd /opt
  git clone https://github.com/laramies/theHarvester
  setfacl -m u:$MYUSER:rwx theHarvester/
  cd theHarvester

  # Change requirement (November 2022 incompatibility)
  # dnspython<=2.0.0
  sed -i "s/^dnspython/#dnspython/g" requirements/base.txt
  sed -i -e '$adnspython<=2.0.0' requirements/base.txt
  sudo -u $MYUSER python3 -m pip install -r requirements/base.txt

  SCRIPTFILE=/opt/theHarvester/theHarvester.sh
  cat << EOF > $SCRIPTFILE
#!/bin/bash
STARTDIR=$PWD
cd /opt/theHarvester && ./theHarvester.py $@ && cd $STARTDIR
EOF

  chmod +x $SCRIPTFILE

  ln -s $SCRIPTFILE /usr/local/bin/


}

RemoveTheHarvester(){

  rm -rf /opt/theHarvester/
  rm -f /usr/local/bin/theHarvester.sh

}

InstallYETI(){
  # https://github.com/yeti-platform/yeti

  YETIINSTALLDIR=/opt/yeti
  # modified install  script based on
  # https://raw.githubusercontent.com/yeti-platform/yeti/master/extras/centos_bootstrap.sh

  ### Create the MongoDB repository

  cat << EOF > /etc/yum.repos.d/mongodb-org-4.4.repo
[mongodb-org-4.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/8/mongodb-org/4.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-4.4.asc
EOF

  ### Prepare the field for Yarn

  sudo -u $MYUSER curl --silent --location https://rpm.nodesource.com/setup_19.x | bash -
  wget https://dl.yarnpkg.com/rpm/yarn.repo -O /etc/yum.repos.d/yarn.repo


  # Install mongoDB packages
  dnf install mongodb-org-server mongodb-org-tools -y

  ### Install the YETI Dependencies
  dnf groupinstall "Development Tools" -y
  dnf install python-pip git mongodb-org python-devel libxml2-devel libxslt-devel zlib-devel redis firewalld yarn vim curl wget net-tools nginx uwsgi -y

  # install in users context
  sudo -u $MYUSER pip install --upgrade pip
  sudo -u $MYUSER pip install uwsgi

  ### Install YETI
  mkdir /var/log/yeti
  setfacl -m u:$MYUSER:rwx /var/log/yeti
  cd /opt
  git clone https://github.com/yeti-platform/yeti.git
  setfacl -m u:$MYUSER:rwx /opt/yeti
  cd yeti

  # add constraint on werkzeug version (august 2022 issue, https://werkzeug.palletsprojects.com/en/2.2.x/changes/)
  # werkzeug<=2.1.2
  sed -i -e '$awerkzeug<=2.1.2' requirements.txt

  sudo -u $MYUSER pip install -r requirements.txt
  sudo -u $MYUSER yarn install
  PWD1=`pwd`

  # make changes to service files
  chmod +x $PWD1/extras/systemd/*
  sed -i s'/\/usr\/local\/bin\/uwsgi/\/usr\/bin\/uwsgi\ --plugin\ python/g' $PWD1/extras/systemd/yeti_uwsgi.service
  sed -i s'/\/usr\/local\/bin/\/usr\/bin/g' $PWD1/extras/systemd/yeti_uwsgi.service
  sed -i s'/\/usr\/local\/bin/\/bin/g' $PWD1/extras/systemd/*
  sed -i s"/User=yeti/User=$MYUSER/g" /opt/yeti/extras/systemd/* # replace expected yeti user with user on this system

  # create symbolic links for service files
  ln -s $PWD1/extras/systemd/* /lib/systemd/system/

  ### Secure your instance
  # Add firewall rules for YETI
  #systemctl enable firewalld
  #systemctl start firewalld
  #firewall-cmd  --permanent --zone=public --add-port 5000/tcp
  #firewall-cmd --reload

  # Prepare for startup
  systemctl enable mongod
  systemctl start mongod

  # Launch Yeti
  systemctl enable yeti_web.service
  systemctl enable yeti_analytics.service
  systemctl enable yeti_beat.service
  systemctl enable yeti_exports.service
  systemctl enable yeti_feeds.service
  systemctl enable yeti_oneshot.service
  systemctl enable yeti_uwsgi.service
  systemctl enable redis

  systemctl start yeti_web.service
  systemctl start yeti_analytics.service
  systemctl start yeti_beat.service
  systemctl start yeti_exports.service
  systemctl start yeti_feeds.service
  systemctl start yeti_oneshot.service
  systemctl start yeti_uwsgi.service
  systemctl start redis

  cd $YETIINSTALLDIR
  wget https://github.com/tjuuljensen/bootstrap-fedora/raw/master/lib/osint/yeti.png

  # create desktop file
  DESKTOPFILE=/usr/share/applications/yeti.desktop
  cat << EOF > $DESKTOPFILE
[Desktop Entry]
Version=1.0
Type=Application
Name=YETI
Comment=Yeti is a platform meant to organize observables, indicators of compromise, TTPs, and knowledge on threats in a single, unified repository.
Icon=/opt/yeti/yeti.png
Exec=firefox localhost:5000
Actions=
Categories=Network;WebBrowser;
EOF

}

RemoveYETI(){
  # This is not a complete uninstall as this would disable other features
  # Only main uninstallation tasks are added here

  #firewall-cmd --permanent --zone=public --remove-port 5000/tcp
  #irewall-cmd --reload

  systemctl stop mongod
  systemctl stop yeti_web.service
  systemctl stop yeti_analytics.service
  systemctl stop yeti_beat.service
  systemctl stop yeti_exports.service
  systemctl stop yeti_feeds.service
  systemctl stop yeti_oneshot.service
  systemctl stop yeti_uwsgi.service
  systemctl stop redis

  dnf remove mongodb-org-server mongodb-org-tools -y
  dnf remove mongodb-org redis yarn nginx uwsgi -y

  rm /etc/yum.repos.d/yarn.repo
  rm /etc/yum.repos.d/mongodb-org-4.4.repo

  # Remove symbolic links
  echo Removing symbolic links...
  INSTALLDIR=/opt/yeti/
  SYMLINKSDIR=${INSTALLDIR}extras/systemd/
  find /lib/systemd/system -lname "$SYMLINKSDIR*" -delete -print 2>/dev/null

  # remove desktop file
  DESKTOPFILE=/usr/share/applications/yeti.desktop
  rm -f $DESKTOPFILE

  # uninstall packages
  sudo -u $MYUSER pip uninstall uwsgi -y

  # remove installdir
  rm -rf $INSTALLDIR
}


InstallSpiderFoot(){
  # https://github.com/smicallef/spiderfoot
  # Install Development branch

  cd /opt
  git clone https://github.com/smicallef/spiderfoot.git
  setfacl -m u:$MYUSER:rwx spiderfoot/
  cd spiderfoot
  sudo -u $MYUSER pip3 install -r requirements.txt
  #  python3 ./sf.py -l 127.0.0.1:5001

  SERVICEFILE=/opt/spiderfoot/spiderfoot.service
  cat << EOF > $SERVICEFILE
[Unit]
Description=Spiderfoot web server

[Service]
Type=simple
User=$MYUSER
WorkingDirectory=/opt/spiderfoot
ExecStart=/opt/spiderfoot/sf.py -l 127.0.0.1:5001

[Install]
WantedBy=multi-user.target
EOF

# create symbolic link for service file
ln -s $SERVICEFILE /lib/systemd/system/

# create desktop file
DESKTOPFILE=/usr/share/applications/spiderfoot.desktop
cat << EOF > $DESKTOPFILE
[Desktop Entry]
Version=1.0
Type=Application
Name=Spiderfoot
Comment=SpiderFoot automates OSINT so you can find what matters, faster.
Icon=/opt/spiderfoot/spiderfoot/static/img/spiderfoot-icon.png
Exec=firefox localhost:5001
Actions=
Categories=Network;WebBrowser;
EOF

}

RemoveSpiderFoot(){

  # remove desktop file
  DESKTOPFILE=/usr/share/applications/spiderfoot.desktop
  rm $DESKTOPFILE

  # Stop service and remove service file
  systemctl stop spiderfoot.service
  rm -f /lib/systemd/system/spiderfoot.service

  # remove library
  rm -rf /opt/spiderfoot/

}
