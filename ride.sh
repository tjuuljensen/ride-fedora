#!/bin/bash
# ride.sh - Remove / Install / Disable / Enable 
#
# Author: Torsten Juul-Jensen
# July 30, 2022
#
# Version:
# Purpose: Assist a slistream/bootloader install of a (Fedora) linux workstation

################################################################
###### Default Bootstrap Library Functions ###
################################################################

RequireAdmin(){
    # Function name if different from rest of script to match the library function names
    # check if script is root and restart as root if not
    [ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"
}

PressAnyKeyToContinue(){
    read -n 1 -s -r -p "Press any key to continue..."
    echo ""
}

Restart(){
  echo Rebooting now...
  reboot now
}

################################################################
###### Bootstrap Loader Functions (local only) ###
################################################################

_help()
{
    SCRIPT_NAME=$(basename $0)
    echo "usage: $SCRIPT_NAME [--include <function library file>] [--preset <filename>] [[_]tweakname]"
    exit 1
}

_setVariables(){

  FEDORARELEASE=$(sed 's/[^0-9]//g' /etc/fedora-release) #Fedora release number
  DOWNLOADDIR=/tmp
  SCRIPTDIR=$( dirname $( realpath "${BASH_SOURCE[0]}" )) #set the variable to the place where script is loaded from
  MYUSER=$(logname)
  LOGINUSERUID=$(id -u ${MYUSER})
  MYUSERDIR=$(eval echo "~$MYUSER")
  WORKDIR=$(pwd)

  export SCRIPT_FEDORARELEASE=$FEDORARELEASE
  export SCRIPT_SCRIPTDIR=$SCRIPTDIR
  export SCRIPT_MYUSER=$MYUSER
  export SCRIPT_LOGINUSERUID=$LOGINUSERUID
  export SCRIPT_DOWNLOADDIR=$DOWNLOADDIR
  export SCRIPT_MYUSERDIRE=$MYUSERDIR
  export SCRIPT_WORKDIR
  export SCRIPT_VARSSET=1

}

_unsetVariables(){

  unset SCRIPT_FEDORARELEASE
  unset SCRIPT_SCRIPTDIR
  unset SCRIPT_MYUSER
  unset SCRIPT_LOGINUSERUID
  unset SCRIPT_DOWNLOADDIR
  unset SCRIPT_MYUSERDIR
  unset SCRIPT_WORKDIR
  unset SCRIPT_VARSSET

}

_logOutput(){
  # Logs the output of the script to a log file
  # Redirect stdout and stderr to tee. Append all to LOGFILE

  if [ "$UID" -ne 0 ] ; then # if script is not run with root privileges
    LOGDIR=~/.log/
  else
    LOGDIR=/var/log/bootstrap-installer
  fi

  LOGFILE=$LOGDIR/bootstrap-log.$(date +"%Y%m%d%H%M%S")

  if [ ! -d $LOGDIR ] ; then # log directory does not exist
    mkdir -p $LOGDIR
  fi

  touch $LOGFILE
  chown $MYUSER:$MYUSER $LOGFILE
  exec >  >(tee -a "${LOGFILE}")
  exec 2> >(tee -a "${LOGFILE}" >&2)

  echo "################################################################"
  echo ""
  echo Logfile:  $LOGFILE
  echo Script: $0
  echo Command line parameters: $@
  echo "Timestamp: "$(date)
  echo ""
  echo "################################################################"
  echo ""
}

_readPresetFile(){
  #cat test.preset | cut -d '#' -f1 | grep -v -e '^[[:space:]]*$' -e '^#' | sed "s/\t\t*//g" | sed 's/ //g'
  PRESETFILECONTENT=( `cat $1 | cut -d '#' -f1 | grep -v -e '^[[:space:]]*$' -e '^#' | sed "s/\t\t*//g" | sed 's/ //g' | sed 's/\r//g'` )
  ACTIONS=("${ACTIONS[@]}" "${PRESETFILECONTENT[@]}")
}

_addOrRemoveAction(){
  PARAMETER=$1
  if [[ ${PARAMETER:0:1} == "_" ]] ; then
    # If parameter value starts with an underscore "_" then exclude the action
    #ACTIONS=( "${ACTIONS[@]/${PARAMETER#?}/}" )
    for i in "${!ACTIONS[@]}"; do
        [ "${PARAMETER#?}" == "${ACTIONS[$i]}" ] && unset "ACTIONS[$i]"
    done

  elif [[ "$PARAMETER" != "" ]]; then
    ACTIONS+=($PARAMETER)
  fi
}

_functionExists() {
    [ `type -t $1`"" == 'function' ]
}

_executeFunctions(){
  # execute all valid functions
  for i in "${!ACTIONS[@]}"; do
      _functionExists "${ACTIONS[$i]}" && echo "::: ${ACTIONS[$i]} :::" &&  (${ACTIONS[$i]}) # print name & execute function
  done
}

_parseArguments () {
    #declare global variable arrays
    declare -g -a PRESET # preset file(s)
    declare -g -a INCLUDE # library file(s)
    declare -g -a ACTIONS # atomic action(s)

    declare -g LOGACTIONS # log yes/no
    LOGACTIONS=1 # controls whether script is logging all output to logfile

    if [[ $# -eq 0 ]] ; then
      _help
      exit 1
    else
      # check if script is root and restart as root if not
      [ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"
    fi

      while [[ $# -gt 0 ]]
      do
        case $1 in
            -i | --include)
                if [ -f $2 ] ; then
                  INCLUDE+="$2"
                  source $2 # Load script from file
                elif [ -f $SCRIPTDIR/$2 ] ; then
                  INCLUDE+="$SCRIPTDIR/$2"
                  source "$SCRIPTDIR/$2" # Load script from file
                else
                  echo Function library $2 was not found
                fi
                shift
                shift
                ;;
            -p | --preset)
              if [ -f $2 ] ; then
                PRESET+="$2"
                _readPresetFile $PRESET
              elif [ -f $SCRIPTDIR/$2 ] ; then
                PRESET+="$SCRIPTDIR/$2"
                _readPresetFile "$SCRIPTDIR/$2"
              else
                echo Preset file does not exist
                exit 2
              fi

              shift
              shift
              ;;
            -n | --nolog)
              $LOGACTIONS=0
              ;;
            -h | --help )
              _help
              exit 1
              ;;
            * )
            _addOrRemoveAction $1
             shift
        esac
        #$i=$((i + 1))
    done
}

#### Main ####
_setVariables $@
_parseArguments $@
(( $LOGACTIONS == 1)) && _logOutput $@
_executeFunctions
_unsetVariables
