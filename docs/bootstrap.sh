#!/bin/bash
# Bootstrap loader to bootstrap-fedora repo
#
# Torsten Juul-Jensen
# October 28, 2022

GITHUB_REPO=bootstrap-fedora
# Direct URL to bootstrap master archive on github
BOOTSTRAP_ARCHIVE="https://github.com/tjuuljensen/${GITHUB_REPO}/archive/master.zip"
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" #set the variable to the place where script is loaded from

# Fail on any error
set -e

usage_help()
{
  SCRIPT_NAME=$(basename $0)
  echo "usage: $SCRIPT_NAME [--ride <options...>] [--default] [--stop] [--edit | --vi ]"
  exit 1
}

download_source()
{
  # Install required packages
  REQUIREDPACKAGES=("unzip" "wget")
  for i in ${!REQUIREDPACKAGES[@]};
  do
    rpm -q --quiet ${REQUIREDPACKAGES[$i]}  || dnf install -y ${REQUIREDPACKAGES[$i]}
  done

  TEMPDIR="$(mktemp -d /tmp/ride.XXXXXXXXXX)"
  echo -e "Downloading \x1b[32m$BOOTSTRAP_ARCHIVE\x1b[m => \x1b[32m$TEMPDIR/\x1b[m"
  cd $TEMPDIR
  wget -q "$BOOTSTRAP_ARCHIVE"
  echo unzipping...
  unzip master.zip > /dev/null  && mv "$TEMPDIR"/${GITHUB_REPO}-master/* "$TEMPDIR" && rm master.zip && rm -rf ${GITHUB_REPO}-master/ && echo done.
  INSTALLDIR=$(realpath "$TEMPDIR")
}

# If this file does not exist it's probably because we're bootstrapping a fresh
# system.  So we download the Git repository and bootstrap from there
if [[ ! -f "$SCRIPTDIR/${GITHUB_REPO}/ride.sh" ]] && [[ ! -f "$SCRIPTDIR/../ride.sh" ]]; then #the ride script does NOT exist in current dir
  download_source
elif [[ -f "$SCRIPTDIR/${GITHUB_REPO}/ride.sh" ]] ; then
  INSTALLDIR=$(realpath "$SCRIPTDIR/${GITHUB_REPO}/")
elif [[ -f "$SCRIPTDIR/../ride.sh" ]] ; then
  INSTALLDIR=$(realpath "$SCRIPTDIR/../")
fi

if [[ $# -eq 0 ]] ; then
  # show syntax
  echo No command line parameters entered
  if [[ ! -z $TEMPDIR ]] && [[ ! -d $SCRIPTDIR/${GITHUB_REPO}/ ]]; then
    cd $SCRIPTDIR
    mv $TEMPDIR ${SCRIPTDIR}/${GITHUB_REPO}/
    echo Files can be found in: $(realpath "${SCRIPTDIR}/${GITHUB_REPO}/")
  fi
  usage_help
elif [[ "--help | --h" == *"$1"* ]]; then
  # show syntax
  usage_help
elif [[ "--default" == *"$1"* ]] ; then
  # Start the installation of the default preset
  cd $INSTALLDIR
  ./ride.sh --include lib-fedora.sh --preset default.preset
elif [[  "--stop | -s" == *"$1"* ]] ; then
  echo "No installation tasks performed. It is up to you now to do the magic."
  if [[ ! -z $TEMPDIR ]]  && [[ ! -d $SCRIPTDIR/${GITHUB_REPO}/ ]]; then
    cd $SCRIPTDIR
    mv $TEMPDIR ${SCRIPTDIR}/${GITHUB_REPO}/
    echo Files can be found in: $(realpath "${SCRIPTDIR}/${GITHUB_REPO}/")
  fi
  exit 0
elif [[  "--edit | --vi | -e" == *"$1"* ]] ; then
  cd $INSTALLDIR
  cp default.preset custom.preset
  vi custom.preset
  ./ride.sh --include lib-fedora.sh --preset custom.preset
elif [[ "--ride" == *"$1"* ]] ; then
  # Start the RIDE installation with remaining parameters
  cd $INSTALLDIR
  shift
  ./ride.sh $@
else
  usage_help
fi
