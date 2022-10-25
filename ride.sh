#!/bin/bash
# ride.sh - Remove / Install / Disable / Enable
#
# Author: Torsten Juul-Jensen
# October 35, 2022
#
# Version:
# Purpose: Assist a slipstream/bootloader install of a (Fedora) linux workstation

################################################################
###### Default Bootstrap Library Functions ###
################################################################

# Function used across library files
RequireAdmin(){
    # Function name if different from rest of script to match the library function names
    # check if script is root and restart as root if not
    [ "$UID" -eq 0 ] || exec sudo bash "$0" "$@" ; return 2> /dev/null; exit
}

# Function used across library files
PressAnyKeyToContinue(){
    read -n 1 -s -r -p "Press any key to continue..."
    echo ""
}

# Function used across library files
Restart(){
  echo Rebooting now...
  reboot now
}

################################################################
###### Bootstrap Loader Functions (local only) ###
################################################################

usage_help()
{
    SCRIPT_NAME=$(basename $0)
    echo 'usage: $SCRIPT_NAME [--include <function library file>] [--preset <filename>] [{--list}/{--verbose} <function file>] [[_]tweakname]'

    echo '-i | --include <function library file>       - the RIDE function file contains all the functions for installing/removing tools'
    echo '-p | --preset  <preset filename>             - the preset file contains what functions in the ridefunction file to use'
    echo '-l | --list    <function library file>       - list the RIDE functions available from the functions file'
    echo '-c | --verbose <function file>               - list the RIDE functions with sections from the functions file'
    echo '-v | --compare <function file> <preset file> - compare contents of functions file and preset file'
    echo '-n | --nolog                                 - disable logging'
    exit 1

}

set_constants(){

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
  export SCRIPT_MYUSERDIR=$MYUSERDIR
  export SCRIPT_WORKDIR
  export SCRIPT_VARSSET=1

}

unset_constants(){

  unset SCRIPT_FEDORARELEASE
  unset SCRIPT_SCRIPTDIR
  unset SCRIPT_MYUSER
  unset SCRIPT_LOGINUSERUID
  unset SCRIPT_DOWNLOADDIR
  unset SCRIPT_MYUSERDIR
  unset SCRIPT_WORKDIR
  unset SCRIPT_VARSSET

}

log_output(){
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
  echo "Timestamp: $(date)"
  echo ""
  echo "################################################################"
  echo ""
}

read_preset_file(){
  PRESETFILE=$1
  PRESETFILECONTENT=( $(awk '{print $1}' ${PRESETFILE} | grep -v '^#' | awk 'NF') )
  ACTIONS=("${ACTIONS[@]}" "${PRESETFILECONTENT[@]}")
}

add_remove_action(){
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

execute_functions() {
    # execute all valid functions
    echo "Performing: ${ACTIONS[@]}"
    echo ""
    for action in "${!ACTIONS[@]}"; do
        ENTRYTYPE=$( type -t ${ACTIONS[action]} )
        if [ x${ENTRYTYPE} == x'function' ]; then
            echo "::: ${ACTIONS[$action]} :::"
            (${ACTIONS[$action]})
        else
            echo "${action} is NOT a function - will not be executed"
            continue
        fi
        echo ''
    done
}

list_functions() {
  PRESETFILEFIRSTLINE=$(grep -En "^[[:alnum:]]" $1 | head -n 1 | cut -d: -f1)
  sed -n "${PRESETFILEFIRSTLINE},\$p" $1 | grep -i -E '^[[:space:]]*([[:alnum:]_]+[[:space:]]*\(\)|function[[:space:]]+[[:alnum:]_]+)' | sed -e 's/[(){)]//g' | sed -e 's/function //I' | sed 's/\r$//g'
}

verbose_list_functions() {
  PRESETFILEFIRSTLINE=$(grep -En "^[[:alnum:]]" $1 | head -n 1 | cut -d: -f1)
  sed -n "${PRESETFILEFIRSTLINE},\$p" $1 | grep -i -E '^[[:space:]]*([[:alnum:]_]+[[:space:]]*\(\)|function[[:space:]]+[[:alnum:]_]+)|###+' | sed -e 's/[(){)]//g' | sed -e 's/function //I' | sed 's/\r$//g' | grep -v -e '^##############'
}

#
# Args: $1 is Function Library - $2 is preset file
compare_library_preset() {
  # preset file read
  LIBFUNCTIONS=$(grep -i -E '^[[:space:]]*([[:alnum:]_]+[[:space:]]*\(\)|function[[:space:]]+[[:alnum:]_]+)' $1 | sed -e 's/[(){)]//g' | sed -e 's/function //I' | sed 's/\r$//g'  )
  PRESETFILEFIRSTLINE=$(grep -En "^[[:alnum:]]" $2 | head -n 1 | cut -d: -f1)
  PRESETFILECONTENT=$( sed -n "${PRESETFILEFIRSTLINE},\$p" $2 | grep -v -e '^##'  | sed 's/#/\n/g'| grep -v -e '^[[:space:]]*$' -e '^#'  | sed "s/\t\t*//g" | sed 's/ //g' | sed 's/\r$//g'  )

  echo Preset functions from $2 missing in library file $1:
  for PRESET in $PRESETFILECONTENT ; do
    case "${LIBFUNCTIONS[@]}" in
      *"$PRESET"*)
        #echo -e "$PRESET - \e[1mOK\e[0m"
        ;;
      *)
        echo -e "  $PRESET - \e[1m\e[31mMissing\e[0m"
        ;;
    esac
  done

  echo "${PRESETFILECONTENT[@]}" > /tmp/debug.txt
  echo Library functions from $1 not in preset file $2:
  for LIB in $LIBFUNCTIONS ; do
    case "${PRESETFILECONTENT[@]}" in
      *"$LIB"*)
        #echo -e "$LIB - \e[1mOK\e[0m"
        ;;
      *)
        echo -e "  $LIB - \e[1m\e[31mMissing\e[0m"
    esac
  done
}

parse_arguments() {
    #declare global variable arrays
    declare -g -a PRESET # preset file(s)
    declare -g -a INCLUDE # library file(s)
    declare -g -a ACTIONS # atomic action(s)

    declare -g LOGACTIONS # log yes/no
    LOGACTIONS=1 # controls whether script is logging all output to logfile

    if [[ $# -eq 0 ]] ; then
      usage_help
      exit 1
    fi

      while [[ $# -gt 0 ]]
      do
        case $1 in
            -i | --include)
                [[ "$UID" -eq 0 ]] || exec sudo bash "$0" "$@"
                if [ -f $2 ] ; then
                  INCLUDE+="$2"
                  source $2 # Load script from file
                elif [ -f $SCRIPTDIR/$2 ] ; then
                  INCLUDE+="$SCRIPTDIR/$2"
                  source "$SCRIPTDIR/$2" # Load script from file
                else
                  echo Function library $2 was not found
                  exit 2
                fi
                shift
                shift
                ;;
            -p | --preset)
              [[ "$UID" -eq 0 ]] || exec sudo bash "$0" "$@"
              if [[ -f $2 ]] ; then
                PRESET+="$2"
                read_preset_file $PRESET
              elif [[ -f $SCRIPTDIR/$2 ]] ; then
                PRESET+="$SCRIPTDIR/$2"
                read_preset_file "$SCRIPTDIR/$2"
              else
                echo Preset file does not exist
                exit 2
              fi

              shift
              shift
              ;;
            -l | --list )
              LOGACTIONS=0
              if [[ -f $2 ]] ; then
                list_functions $2
              elif [[ -f $SCRIPTDIR/$2 ]] ; then
                list_functions "$SCRIPTDIR/$2"
              else
                echo Function library $2 was not found and could not be listed
                usage_help
              fi
              exit 0
              ;;
            -c | --compare )
              LOGACTIONS=0
              if [[ -f $2 ]] && [[ -f $3 ]]; then
                compare_library_preset $2 $3
              else
                echo "Compare command need two existing files as parameter (files not found)"
                usage_help
                exit 1
              fi
              exit 0
              ;;
            -v | --verbose_list )
              LOGACTIONS=0
              if [[ -f $2 ]] ; then
                verbose_list_functions $2
              elif [ -f $SCRIPTDIR/$2 ] ; then
                verbose_list_functions "$SCRIPTDIR/$2"
              else
                echo "Verbose list command need an existing file as parameter (file not found)"
                usage_help
              fi
              exit 0
              ;;
            -n | --nolog)
              LOGACTIONS=0
              shift
              ;;
            -h | --help )
              usage_help
              exit 1
              ;;
            * )
            add_remove_action $1
            shift
        esac
        #$i=$((i + 1))
    done
}

#### Main ####
set_constants $@
parse_arguments $@
[[ $LOGACTIONS==1 ]] && log_output $@
execute_functions
unset_constants
