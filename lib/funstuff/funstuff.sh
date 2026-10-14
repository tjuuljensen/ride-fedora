#!/bin/bash
#
# Author: Torsten Juul-Jensen
# Edited: December 28, 2023 08:00
#
# A tribute to developers creating (mostly) useless but funny linux binaries
# More terminal fun can be found here: https://www.tecmint.com/funny-linux-commands/
#


# ls error typing (train)
function InstallSl(){
    dnf install -y sl
}

function RemoveSl(){
    dnf remove -y sl
}


# apply rainbow colors to terminal output
function InstallLolcat(){
    dnf install -y lolcat
}

function RemoveLolcat(){
    dnf remove -y lolcat
}

# enter the matrix
function InstallCmatrix(){
    dnf install -y cmatrix
}

function RemoveCmatrix(){
    dnf remove -y cmatrix
}

# terminal afire
function InstallAfire(){
    dnf install -y xorg-x11-fonts-misc aalib
}

function RemoveAfire(){
    dnf remove -y xorg-x11-fonts-misc aalib
}

# Desktop cat
function InstallOneko(){
    dnf install -y oneko
}

function RemoveOneko(){
    dnf remove -y oneko
}

# See where you go
function InstallXeyes(){    
    dnf install -y xeyes
}

function RemoveXeyes(){    
    dnf remove -y xeyes
}

# Let the cow speak
function InstallCowsay(){
    dnf install -y cowsay xcowsay
}

function RemoveCowsay(){
    dnf remove -y cowsay xcowsay
}

# Ascii aquarium
function InstallAsciiaquarium(){
    dnf install -y asciiquarium
}

function RemoveAsciiaquarium(){
    dnf remove -y asciiquarium
}

# Output text in Acii art 
function InstallFiglet(){
    dnf install -y figlet
}

function RemoveFiglet(){
    dnf remove -y figlet
}

# Output text (simpler)
function InstallToilet(){
    dnf install -y toilet
}

function RemoveToilet(){
    dnf remove -y toilet
}

# quotes
function InstallFortune(){
    dnf install -y fortune-mod
}

function RemoveFortune(){
    dnf remove -y fortune-mod
}

# corrects errors in previous console commands
function InstallThefuck(){
    dnf install -y thefuck
}

function RemoveThefuck(){
    dnf remove -y thefuck
}

# funny man pages - https://github.com/ltworf/funny-manpages/
InstallFunnyManpages(){

  AUTHOR=ltworf
  REPO=funny-manpages
  FILETYPE=tar.gz 
  GITHUBURL=https://api.github.com/repos/${AUTHOR}/${REPO}/releases
  URL=$(curl $GITHUBURL  2>&1 | grep browser_download_url | grep ${FILETYPE} | awk NR==1 | cut -d'"' -f4)
  INSTALLPKG="${URL##*/}"
  INSTALLDIR=/opt

  cd $DOWNLOADDIR

  wget -q --show-progress  $URL
  tar xvf $INSTALLPKG -C $INSTALLDIR 

  cd ${INSTALLDIR}/${REPO}
  make install
}

RemoveFunnyManpages(){
  rm -rf /opt/funny-manpages/ 
  rm /usr/share/man/man1/*.1fun
  rm /usr/share/man/man3/strfry.3fun
  rm /usr/share/man/man6/sex.6fun
}

# Convert jpg to ascii
InstallAview(){
  AUTHOR=rpmsphere
  REPO=noarch
  GITHUBURL=https://api.github.com/repos/${AUTHOR}/${REPO}/contents/r
  URL=$(curl $GITHUBURL  2>&1 | grep rpmsphere-release | grep download_url | cut -d'"' -f4)
  rpm -Uvh $URL

  dnf install -y aview
}

RemoveAview(){
  # remove rpmsphere repo file
  rm /etc/yum.repos.d/rpmsphere.repo
  dnf remove -y aview
}
