#!/bin/bash
# Bootstrap loader to ride-fedora repo
#
# Torsten Juul-Jensen
# November 30, 2022

AUTHOR=tjuuljensen
REPO=ride-fedora

# Direct URL to bootstrap master archive on github
BOOTSTRAP_ARCHIVE="https://github.com/${AUTHOR}/${REPO}/archive/master.zip"
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" #set the variable to the place where script is loaded from

# Fail on any error
set -e

usage_help()
{
  SCRIPT_NAME=$(basename $0)
  echo "normal usage:     $SCRIPT_NAME [--ride <options...>] [--default] [--stop] [--edit | --vi ]"
  echo "specific release: $SCRIPT_NAME --release v37.0.0"
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

  if [[ $# -ne 0 ]] && [[ "--release | -r" == *"$1"* ]]; then
    BOOTSTRAP_ARCHIVE="https://github.com/${AUTHOR}/${REPO}/archive/refs/tags/${2}.zip"  
    ARCHIVE=${2}
    shift 2 
  else
    ARCHIVE=master
  fi

  TEMPDIR="$(mktemp -d /tmp/ride.XXXXXXXXXX)"
  echo -e "Downloading \x1b[32m$BOOTSTRAP_ARCHIVE\x1b[m => \x1b[32m$TEMPDIR/\x1b[m"
  cd $TEMPDIR
  wget -q "$BOOTSTRAP_ARCHIVE"
  echo unzipping...
  unzip ${ARCHIVE}.zip > /dev/null  && mv "$TEMPDIR"/${REPO}-${ARCHIVE##*v}/* "$TEMPDIR" && rm ${ARCHIVE}.zip && rm -rf ${REPO}-${ARCHIVE##*v}/ && echo done.
  INSTALLDIR=$(realpath "$TEMPDIR")
  
}

# If this file does not exist it's probably because we're bootstrapping a fresh
# system.  So we download the Git repository and bootstrap from there
if [[ ! -f "$SCRIPTDIR/${REPO}/ride.sh" ]] && [[ ! -f "$SCRIPTDIR/../ride.sh" ]]; then #the ride script does NOT exist in a subdir or one level up (run from repo directory)
  download_source $@
elif [[ -f "$SCRIPTDIR/${REPO}/ride.sh" ]] ; then
  INSTALLDIR=$(realpath "$SCRIPTDIR/${REPO}/")
elif [[ -f "$SCRIPTDIR/../ride.sh" ]] ; then
  INSTALLDIR=$(realpath "$SCRIPTDIR/../")
fi

if [[ $# -eq 0 ]] ; then
  # show syntax
  echo No command line parameters entered

  # If no parameters were given, and the tempdir exists, move the directory to the script directory
  if [[ ! -z $TEMPDIR ]] && [[ ! -d $SCRIPTDIR/${REPO}/ ]]; then
    cd $SCRIPTDIR
    mv $TEMPDIR ${SCRIPTDIR}/${REPO}/
    echo Files can be found in: $(realpath "${SCRIPTDIR}/${REPO}/")
  fi
  usage_help
elif [[ "--help | -h" == *"$1"* ]]; then
  # show syntax
  usage_help
elif [[ "--default" == *"$1"* ]] ; then
  # Start the installation of the default preset
  cd $INSTALLDIR
  ./ride.sh --include lib-fedora.sh --preset default.preset
elif [[  "--stop | -s" == *"$1"* ]] || [[  "--release | -r" == *"$1"* ]]  ; then
  echo "No installation tasks performed. It is up to you now to do the magic."
  if [[ ! -z $TEMPDIR ]]  && [[ ! -d $SCRIPTDIR/${REPO}/ ]]; then
    cd $SCRIPTDIR
    mv $TEMPDIR ${SCRIPTDIR}/${REPO}/
    echo Files can be found in: $(realpath "${SCRIPTDIR}/${REPO}/")
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
