#!/bin/sh
# lib-distro.sh
# Author: Torsten Juul-Jensen
# Edited: August 1, 2022 10:00
# Latest verification and tests done on Fedora 36
#
# This file is a bash function library only and is meant for sourcing into other scripts
# It is a part of the github repo https://github.com/tjuuljensen/bootstrap-fedora
#

# Declare static variables
MYUSER=$(logname)
LOGINUSERHOME=$(eval echo "~$(logname)")

if [[ -d $LOGINUSERHOME/Downloads/ ]] ; then
  DOWNLOADDIR=$(realpath $LOGINUSERHOME/Downloads/)
else
  DOWNLOADDIR=$(realpath $LOGINUSERHOME)
fi

################################################################
###### Debian  ###
################################################################

GetDebian () {
  cd $DOWNLOADDIR
  #Debian DVD amd64
  URL=https://cdimage.debian.org/debian-cd/current/amd64/iso-dvd/
  iso_name=$(curl $URL 2>&1 | grep -o -E 'href="([^"#]+)"' | grep -E 'DVD' | grep -v "debian-edu" \
    | grep -v mac | cut -d'"' -f2 | sort -r -n | awk NR==1)
  iso_url="$URL$iso_name"
  wget -q --show-progress $iso_url/ -P $DOWNLOADDIR/
}

GetDebianTorrent () {
  cd $DOWNLOADDIR
  URL=https://cdimage.debian.org/debian-cd/current/amd64/bt-dvd/
  iso_name=$(curl $URL 2>&1 | grep -o -E 'href="([^"#]+)"' | grep 'DVD' | grep -v "debian-edu" \
    | grep -v mac | cut -d'"' -f2 | sort -r -n | awk NR==1)
  iso_url="$URL$iso_name"
  wget -q --show-progress $iso_url/ -P $DOWNLOADDIR/
}

GetDebianNetinst () {
  cd $DOWNLOADDIR
  URL=https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/
  iso_name=$(curl $URL 2>&1 | grep -o -E 'href="([^"#]+)"' | grep -E '-netinst' | grep -v "debian-edu" \
    | grep -v mac | cut -d'"' -f2 | sort -r -n | awk NR==1)
  iso_url="$URL$iso_name"
  wget -q --show-progress $iso_url/ -P $DOWNLOADDIR/
}

################################################################
###### Ubuntu  ###
################################################################

GetUbuntu() {
  cd $DOWNLOADDIR
  # Ubuntu desktop torrent
  URL="https://ubuntu.com/download/alternative-downloads"
  sudo -u $MYUSER curl $URL 2>&1 | grep -o -E 'href="([^"#]+)"' | grep -E 'http|https' \
    | grep releases | grep desktop | cut -d'"' -f2 | sort -n -r | awk NR==1 \
    | awk -F".torr" '{ print $1 }' \
    | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/
}

GetUbuntuTorrent() {
  cd $DOWNLOADDIR
  # Ubuntu desktop torrent
  URL="https://ubuntu.com/download/alternative-downloads"
  sudo -u $MYUSER curl $URL 2>&1 | grep -o -E 'href="([^"#]+)"' | grep -E 'http|https' | \
    grep releases | grep desktop | cut -d'"' -f2 | sort -n -r | awk NR==1 \
    | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/
}


GetUbuntuServer () {
  cd $DOWNLOADDIR
  # Ubuntu server torrent
  URL="https://ubuntu.com/download/alternative-downloads"
  sudo -u $MYUSER curl $URL 2>&1 | grep -o -E 'href="([^"#]+)"' | grep -E 'http|https' \
    | grep releases | grep server | cut -d'"' -f2 | sort -n -r | awk NR==1 \
    | awk -F".torr" '{ print $1 }' \
    | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/
}

GetUbuntuServerTorrent () {
  cd $DOWNLOADDIR
  # Ubuntu server torrent
  URL="https://ubuntu.com/download/alternative-downloads"
  sudo -u $MYUSER curl $URL 2>&1 | grep -o -E 'href="([^"#]+)"' | grep -E 'http|https' \
    | grep releases | grep server | cut -d'"' -f2 | sort -n -r | awk NR==1 \
    | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/
}

################################################################
###### Fedora  ###
################################################################

GetFedora(){
  URL=https://getfedora.org/en/workstation/download/
  sudo -u $MYUSER curl $URL 2>&1 | grep -Eoi '<a [^>]+>' | grep -E 'http|https' | awk -F"href=" '{ print $2}' | cut -d'"' -f2 \
    |  grep download | grep x86_64  |sort -n -r | awk NR==1 \
    | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/
}

GetFedoraTorrent () {
  cd $DOWNLOADDIR
  # Fedora Workstation x86_64
  URL=https://torrent.fedoraproject.org/
  sudo -u $MYUSER curl $URL 2>&1 | grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
    | grep Workstation | grep -v Beta | grep x86_64  |sort -n -r | awk NR==1 \
    | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/
}

GetFedoraServer(){
  URL=https://getfedora.org/en/server/download/
  sudo -u $MYUSER curl $URL 2>&1 | grep -Eoi '<a [^>]+>' | grep -E 'http|https' | awk -F"href=" '{ print $2}' | cut -d'"' -f2 \
    |  grep dvd | grep x86_64  |sort -n -r | awk NR==1 \
    | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/
}

GetFedoraServerTorrent () {
  cd $DOWNLOADDIR
  # Fedora Server x86_64
  URL=https://torrent.fedoraproject.org/
  sudo -u $MYUSER curl $URL 2>&1 | grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
    | grep Server | grep -v Beta | grep -e x86_64 | sort -n -r | awk NR==1 \
    | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/
}


################################################################
###### Kali  ###
################################################################

GetKali () {
  cd $DOWNLOADDIR
  IMAGEURL=http://cdimage.kali.org/current/
  SUBURL=$(curl $IMAGEURL 2>&1 | grep -Eoi '<a [^>]+>' | cut -d'"' -f2 | grep installer-amd64 | grep -v torrent )
  URL="https://images.kali.org/$SUBURL"
  sudo -u $MYUSER wget -q --show-progress -P $DOWNLOADDIR/ $URL
}

GetKaliTorrent () {
  cd $DOWNLOADDIR
  IMAGEURL=http://cdimage.kali.org/current/
  SUBURL=$(curl $IMAGEURL 2>&1 | grep -Eoi '<a [^>]+>' | cut -d'"' -f2 | grep installer-amd64 | grep torrent )
  URL="https://images.kali.org/$SUBURL"
  sudo -u $MYUSER wget -q --show-progress -P $DOWNLOADDIR/ $URL
}

GetKaliLive () {
  cd $DOWNLOADDIR
  IMAGEURL=http://cdimage.kali.org/current/
  SUBURL=$(curl $IMAGEURL 2>&1 | grep -Eoi '<a [^>]+>' | cut -d'"' -f2 | grep live-amd64 | grep -v torrent )
  URL="https://images.kali.org/$SUBURL"
  sudo -u $MYUSER wget -q --show-progress -P $DOWNLOADDIR/ $URL
}

GetKaliLiveTorrent () {
  cd $DOWNLOADDIR
  IMAGEURL=http://cdimage.kali.org/current/
  SUBURL=$(curl $IMAGEURL 2>&1 | grep -Eoi '<a [^>]+>' | cut -d'"' -f2 | grep live-amd64 | grep torrent )
  URL="https://images.kali.org/$SUBURL"
  sudo -u $MYUSER wget -q --show-progress -P $DOWNLOADDIR/ $URL
}

################################################################
###### Mint  ###
################################################################

GetMint(){
  # Linux Mint - Cinnamon
  IMAGEURL=https://mirrors.edge.kernel.org/linuxmint/stable/
  latest_version=$(curl $IMAGEURL 2>&1 | grep -Eoi '<a [^>]+>' | grep -Eow "[0-9\.]{1,4}" | sort -r -g | awk NR==1)
  latest_version_url="$IMAGEURL$latest_version/"
  URL=$(curl $latest_version_url 2>&1 | grep -Eoi '<a [^>]+>' | cut -d'"' -f2 | grep cinnamon)
  sudo -u $MYUSER wget -q --show-progress -P $DOWNLOADDIR/ ${latest_version_url}${URL}
}

################################################################
###### Tails  ###
################################################################

GetTailsTorrent() {
  cd $DOWNLOADDIR
  # https://tails.boum.org/install/expert/index.en.html
  URL=https://tails.boum.org/torrents/files/
  SUBURL=$(curl $URL 2>&1 | grep -Eoi '<a [^>]+>' | grep torrent | cut -d'"' -f2 | grep img )
  download_url="$URL$SUBURL"
  sudo -u $MYUSER wget -q --show-progress -P $DOWNLOADDIR/ $download_url
}

################################################################
###### Raspberry Pi  ###
################################################################

GetRaspiOSTorrent () {
  cd $DOWNLOADDIR
  # Raspian downloads

  # Raspbian with desktop and recommended software (FULL)
  URL=https://www.raspberrypi.com/software/operating-systems/
  sudo -u $MYUSER curl $URL 2>&1 |  grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
    | grep torrent | grep full | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/

  # Raspbian with desktop
  URL=https://www.raspberrypi.com/software/operating-systems/
  sudo -u $MYUSER curl $URL 2>&1 |  grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
    | grep arm64 | grep torrent | grep -v lite \
    | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/

  # Raspbian Lite
  URL=https://www.raspberrypi.com/software/operating-systems/
  sudo -u $MYUSER curl $URL 2>&1 |  grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
    | grep arm64 | grep torrent | grep lite \
    | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/

  # Get SHA-256 sums for all three files directly from web page using this function:
  # wget -qO- $URL | grep -oP 'SHA-256:.*'  | cut -f 3 -d ">" | cut -f 1 -d "<"
  # curl $URL 2>&1 |  grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2  | grep torrent | sed 's/torrent/zip/g'

}

################################################################
###### Other  ###
################################################################

GetSlackwareTorrent () {
  cd $DOWNLOADDIR
  # Slackware

  #Slackware 64bit
  URL=http://www.slackware.com/torrents/
  FILENAME=$(curl $URL 2>&1 |  grep -Eoi '<a [^>]+>' | cut -d'"' -f2  | grep torrent | sort -n -r | awk NR==1 |  cut -f3 -d '/')
  wget -q --show-progress $URL$FILENAME -P $DOWNLOADDIR/

  # Slackware 32bit
  URL=http://www.slackware.com/torrents/
  FILENAME=$(curl $URL 2>&1 |  grep -Eoi '<a [^>]+>' | cut -d'"' -f2  | grep torrent | sort -n -r | awk NR==1 |  cut -f3 -d '/' | sed 's/slackware64/slackware/g')

  wget -q --show-progress $URL$FILENAME -P $DOWNLOADDIR/

}

GetArchTorrent () {
  cd $DOWNLOADDIR
  # Arch Linux
  BASEURL=https://archlinux.org
  SUBPATH=$(curl $BASEURL/releng/releases/ 2>&1 | grep "torrent/" |  cut -d'"' -f2 | sort -Vr | awk NR==1 )
  URL=$BASEURL$SUBPATH
  # curl $URL 2>&1 | grep "torrent/" |  cut -d'"' -f2 | sort -Vr | awk NR==1

  sudo -u $MYUSER wget --content-disposition  -q --show-progress  $URL -P $DOWNLOADDIR/

}


################################################################
###### SecurityOnion  ###
################################################################

GetSecurityOnion(){
  cd $DOWNLOADDIR
  # https://github.com/Security-Onion-Solutions/securityonion/blob/master/VERIFY_ISO.md
  ONIONGPGKEY=https://raw.githubusercontent.com/Security-Onion-Solutions/securityonion/master/KEYS

  BASEURL=https://github.com/Security-Onion-Solutions/securityonion/blob/master/VERIFY_ISO.md
  LATESTISO=$(curl $BASEURL 2>&1 |  grep -Eoi 'href="([^"#]+)"'  | cut -d'"' -f2  | grep iso | grep -v iso.sig)
  LATESTSIG=$(curl $BASEURL  2>&1 |  grep -Eoi 'href="([^"#]+)"'  | cut -d'"' -f2  | grep iso.sig )

  GPGKEYFILE=${ONIONGPGKEY##${ONIONGPGKEY%/*}"/"}
  ISOFILE=${LATESTISO##${LATESTISO%/*}"/"}
  SIGFILE=${LATESTSIG##${LATESTSIG%/*}"/"}

  # Import PGP key
  # gpg --import $GPGKEYFILE

  # Check if file exists
  [[ `wget -S --spider $LATESTISO  2>&1 | grep -E 'HTTP/1.1 200 OK|Remote file exists'` ]] && echo OK || echo no

  sudo -u $MYUSER wget -q --show-progress -P $DOWNLOADDIR/ $LATESTSIG
  sudo -u $MYUSER wget -q --show-progress -P $DOWNLOADDIR/ $LATESTISO

  # Check Signature:
  [[ `gpg --verify $SIGFILE $ISOFILE` ]] && echo good || echo bad

}
