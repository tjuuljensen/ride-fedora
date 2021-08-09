#!/bin/sh
# lib-distro.sh
# Author: Torsten Juul-Jensen
# Edited: July 22, 2020 16:30
# Latest verification and tests done on Fedora XX
#
# This file is a Fedora function library only and is meant for sourcing into other scripts
# It is a part of the github repo https://github.com/tjuuljensen/bootstrap-fedora
#

MYUSER=$(logname)
LOGINUSERUID=$(id -u ${MYUSER})
DOWNLOADDIR=~/Downloads
FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number
MYUSERDIR=$(eval echo "~$MYUSER")


GetDebianTorrent () {
  # debian amd64/i386 cd/dvd

  cd $DOWNLOADDIR
  #Debian DVD amd64
  URL=https://cdimage.debian.org/debian-cd/current/amd64/bt-dvd/
  wget -q --show-progress -r -nH --cut-dirs=4 --no-parent -A "*.torrent" -R  "*mac*" $URL/ -P $DOWNLOADDIR/

  #Debian CD amd64
  URL=https://cdimage.debian.org/debian-cd/current/amd64/bt-cd/
  wget -q --show-progress -r -nH --cut-dirs=4 --no-parent -A "*netinst*" -R  "*mac*" $URL/ -P $DOWNLOADDIR/

  #Debian DVD i386
  URL=https://cdimage.debian.org/debian-cd/current/i386/bt-dvd/
  wget -q --show-progress -r -nH --cut-dirs=4 --no-parent -A "*.torrent" -R  "*mac*" $URL/ -P $DOWNLOADDIR/

  #Debian CD i386
  URL=https://cdimage.debian.org/debian-cd/current/i386/bt-cd/
  wget -q --show-progress -r -nH --cut-dirs=4 --no-parent -A "*netinst*" -R  "*mac*" $URL/ -P $DOWNLOADDIR/

}

GetUbuntuTorrent () {

  cd $DOWNLOADDIR
  # Ubuntu desktop torrent
  URL="https://ubuntu.com/download/alternative-downloads"
  curl $URL 2>&1 | grep -o -E 'href="([^"#]+)"' | grep -E 'http|https' | \
    grep releases | grep desktop | cut -d'"' -f2 | sort -n -r | awk NR==1 | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/

  # Ubuntu server torrent
  # URL="https://ubuntu.com/download/alternative-downloads"
  curl $URL 2>&1 | grep -o -E 'href="([^"#]+)"' | grep -E 'http|https' \
    | grep releases | grep server | cut -d'"' -f2 | sort -n -r | awk NR==1 | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/
}

GetFedoraTorrent () {

  cd $DOWNLOADDIR
  # Fedora Workstation i386
  URL=https://torrent.fedoraproject.org/
  curl $URL 2>&1 | grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
    | grep Workstation | grep -v Atomic | grep -v Beta | grep i386  |sort -n -r | awk NR==1 | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/

  # Fedora Workstation x86_64
  URL=https://torrent.fedoraproject.org/
  curl $URL 2>&1 | grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
    | grep Workstation | grep -v Atomic | grep -v Beta | grep x86_64  |sort -n -r | awk NR==1 | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/

  # Fedora Server i386
  URL=https://torrent.fedoraproject.org/
  curl $URL 2>&1 | grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
    | grep Server | grep -v Beta | grep -e i386 | sort -n -r | awk NR==1 | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/

  # Fedora Server x86_64
  URL=https://torrent.fedoraproject.org/
  curl $URL 2>&1 | grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
    | grep Server | grep -v Beta | grep -e x86_64 | sort -n -r | awk NR==1 | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/
}

GetArchTorrent () {
  cd $DOWNLOADDIR
  # Arch Linux
  BASEURL=https://archlinux.org
  SUBPATH=$(curl $BASEURL/releng/releases/ 2>&1 | grep "torrent/" |  cut -d'"' -f2 | sort -Vr | awk NR==1 )
  URL=$BASEURL$SUBPATH
  # curl $URL 2>&1 | grep "torrent/" |  cut -d'"' -f2 | sort -Vr | awk NR==1

  wget --content-disposition  -q --show-progress  $URL -P $DOWNLOADDIR/

}

GetKaliTorrent () {
  cd $DOWNLOADDIR
  # Kali
  # get listings: curl http://cdimage.kali.org/current/ |  grep -Eoi '<a [^>]+>' | cut -d'"' -f2 | grep -E '(SHA|kali)'

  IMAGEURL=http://cdimage.kali.org/current/
  LATESTISO=$(curl $IMAGEURL 2>&1 | grep -Eoi '<a [^>]+>' | cut -d'"' -f2 | grep installer-amd64)
  LATESTTORRENT=$LATESTISO".torrent"
  TORRENTURL=https://images.kali.org/$LATESTTORRENT

  wget -q --show-progress -P $DOWNLOADDIR/ $TORRENTURL

}

GetKaliISO () {
  cd $DOWNLOADDIR
  # Kali
  # get listings: curl http://cdimage.kali.org/current/ |  grep -Eoi '<a [^>]+>' | cut -d'"' -f2 | grep -E '(SHA|kali)'

  IMAGEURL=http://cdimage.kali.org/current/
  LATESTISO=$(curl $IMAGEURL 2>&1 | grep -Eoi '<a [^>]+>' | cut -d'"' -f2 | grep installer-amd64)

  TORRENTURL=https://images.kali.org/$LATESTISO

  wget -q --show-progress -P $DOWNLOADDIR/ $TORRENTURL

}

GetRaspbianTorrent () {
  cd $DOWNLOADDIR
  # Raspian downloads
  # Download zip files like this: wget --content-disposition https://downloads.raspberrypi.org/raspbian_full_latest

  # Raspbian Stretch with desktop and recommended software (FULL)
  URL=https://www.raspberrypi.org/software/operating-systems
  curl $URL 2>&1 |  grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
    | grep torrent | grep full | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/

  # Raspbian Stretch with desktop
  URL=https://www.raspberrypi.org/software/operating-systems
  curl $URL 2>&1 |  grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
    | grep torrent | grep raspbian_latest | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/

  # Raspbian Stretch Lite
  URL=https://www.raspberrypi.org/software/operating-systems
  curl $URL 2>&1 |  grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
    | grep torrent | grep lite | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/

  # Get SHA-256 sums for all three files directly from web page using this function:
  # wget -qO- $URL | grep -oP 'SHA-256:.*'  | cut -f 3 -d ">" | cut -f 1 -d "<"
  # curl $URL 2>&1 |  grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2  | grep torrent | sed 's/torrent/zip/g'

}

GetSlackware () {
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

GetSuse () {
  cd $DOWNLOADDIR
  # OpenSUSE
  URL=https://get.opensuse.org/leap
  curl $URL 2>&1 | grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
      | grep torrent | grep DVD | sort -n -r | awk NR==1 | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/

  # NetInstall
  curl $URL 2>&1 | grep -Eoi '<a [^>]+>' | grep -E 'http|https' | cut -d'"' -f2 \
      | grep torrent | grep NET | sort -n -r | awk NR==1 | xargs --no-run-if-empty wget -q --show-progress -P $DOWNLOADDIR/

}

GetTails() {
  cd $DOWNLOADDIR
  #https://tails.boum.org/install/linux/usb-download/index.en.html
  URL=https://tails.boum.org/torrents/files/
  TAILSIMAGE=$(curl $URL 2>&1 | grep -Eoi '<a [^>]+>' | grep torrent | cut -d'"' -f2 | grep img )

  wget -q --show-progress -P $DOWNLOADDIR/ $URL$TAILSIMAGE

}

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
  # [[ `wget -S --spider $LATESTISO  2>&1 | grep -E 'HTTP/1.1 200 OK|Remote file exists'` ]] && echo OK || echo no

  # Check Signature:
  # [[ `gpg --verify securityonion-2.3.61-MSEARCH.iso.sig securityonion-2.3.61-MSEARCH.iso`  ]] && echo good || echo bad

}

_cleanup () {
  # unfortunately wget leaves traces after some downloads, so this section is for cleaning up the leftovers
  rm $DOWNLOADDIR/robots.txt.tmp 2> /dev/null
  rm $DOWNLOADDIR/*.html 2> /dev/null
  rm $DOWNLOADDIR/*.html.? 2> /dev/null
}