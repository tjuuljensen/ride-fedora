#!/bin/bash
# list-functions.#!/bin/sh
#
# Helper for outputting contents of code-libraries

_help()
{
  # output help text (syntax)
  SCRIPT_NAME=$(basename $0)
  echo "usage: $SCRIPT_NAME [--verbose] <code-library.sh> | [--compare <code-library.sh> <functions.preset>] | [--help] "
}

# parse command line arguments
_parseArguments(){
  if [[ $# -eq 0 ]] ; then
    _help
  fi

    while [[ $# -gt 0 ]]
    do
      case $1 in
          -v | --verbose )
            if [ ! -f $2 ] ; then #
              echo "Verbose command need an existing file as parameter (file not found)"
              _help
              exit 1
            fi
            grep -E '^[[:space:]]*([[:alnum:]_]+[[:space:]]*\(\)|function[[:space:]]+[[:alnum:]_]+)|###+' $2 | sed -e 's/[(){)]//g' | grep -v -e '^##############'
            exit 0
            shift
            shift
            ;;
          -c | --compare )
            if [ ! -f $2 ] && [ ! -f $3 ]; then #
              echo "Compare command need two existing files as parameter (files not found)"
              _help
              exit 1
            fi
            # preset file read
            LIBFUNCTIONS=$(grep -E '^[[:space:]]*([[:alnum:]_]+[[:space:]]*\(\)|function[[:space:]]+[[:alnum:]_]+)' $2 | sed -e 's/[(){)]//g')
            PRESETFILECONTENT=$( cat $3 | sed -n '7,$p' | grep -v -e '^##'  | sed 's/#/\n/g'| grep -v -e '^[[:space:]]*$' -e '^#'  | sed "s/\t\t*//g" | sed 's/ //g' | sed 's/\r//g' )

            echo Preset functions from $3 missing in library file $2:
            for PRESET in $PRESETFILECONTENT ; do
              case "${LIBFUNCTIONS[@]}" in
                *"$PRESET"*)
                  #echo -e "$PRESET - \e[1mOK\e[0m"
                  ;;
                *)
                  echo -e "$PRESET - \e[1m\e[31mMissing\e[0m"
                  ;;
              esac
            done

            echo Library functions from $2 not in preset file $3:
            for LIB in $LIBFUNCTIONS ; do
              case "${PRESETFILECONTENT[@]}" in
                *"$LIB"*)
                  #echo -e "$LIB - \e[1mOK\e[0m"
                  ;;
                *)
                  echo -e "$LIB - \e[1m\e[31mMissing\e[0m"
                  ;;
              esac
            done
            exit 0
            shift
            shift
            shift
            ;;
          -h | --help )
            _help
            exit 1
            ;;
          * )
           grep -E '^[[:space:]]*([[:alnum:]_]+[[:space:]]*\(\)|function[[:space:]]+[[:alnum:]_]+)' $1 | sed -e 's/[(){)]//g'
           exit 0
           shift
      esac
  done

}

### main ####
_parseArguments $@
