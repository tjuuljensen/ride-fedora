#!/bin/bash
# ridechk.sh
#
# Author: Torsten Juul-Jensen
# Edited: July 30, 2022 10:00
#
# Helper for outputting contents of code-libraries
# Can be used for creating preset files used in misc. repos, e.g. https://github.com/tjuuljensen/bootstrap-fedora
# Examples:
#   Output all functions:             ridechk.sh code-library.sh
#   Output with section information:  ridechk.sh --verbose code-library.sh
#   Compare code with preset file:    ridechk.sh --compare code-library.sh myfile.preset

_help()
{
  # output help text (syntax)
  SCRIPT_NAME=$(basename $0)
  echo "usage: $SCRIPT_NAME [--verbose] <code-library.sh> | [--compare <code-library.sh> <functions.preset>] | [--help] "
  echo " - Output all functions:             ridechk.sh code-library.sh"
  echo " - Output with section information:  ridechk.sh --verbose code-library.sh"
  echo " - Compare code with preset file:    ridechk.sh --compare code-library.sh myfile.preset"
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
            # find first line without hashmarks and read from there
            PRESETFILEFIRSTLINE=$(grep -n -v ^"#" $2 | head -n1 | cut -d: -f1)
            sed -n "${PRESETFILEFIRSTLINE},\$p" $2 | grep -i -E '^[[:space:]]*([[:alnum:]_]+[[:space:]]*\(\)|function[[:space:]]+[[:alnum:]_]+)|###+' | sed -e 's/[(){)]//g' | sed -e 's/function //I' | sed 's/\r$//g' | grep -v -e '^##############'
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
            LIBFUNCTIONS=$(grep -i -E '^[[:space:]]*([[:alnum:]_]+[[:space:]]*\(\)|function[[:space:]]+[[:alnum:]_]+)' $2 | sed -e 's/[(){)]//g' | sed -e 's/function //I' | sed 's/\r$//g'  )
            PRESETFILEFIRSTLINE=$(grep -n -v ^"#" $3 | head -n1 | cut -d: -f1)
            PRESETFILECONTENT=$( sed -n "${PRESETFILEFIRSTLINE},\$p" $3 | grep -v -e '^##'  | sed 's/#/\n/g'| grep -v -e '^[[:space:]]*$' -e '^#'  | sed "s/\t\t*//g" | sed 's/ //g' | sed 's/\r$//g'  )

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

            echo "${PRESETFILECONTENT[@]}" > /tmp/debug.txt
            echo Library functions from $2 not in preset file $3:
            for LIB in $LIBFUNCTIONS ; do
              case "${PRESETFILECONTENT[@]}" in
                *"$LIB"*)
                  #echo -e "$LIB - \e[1mOK\e[0m"
                  ;;
                *)
                  echo -e "$LIB - \e[1m\e[31mMissing\e[0m"
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
          PRESETFILEFIRSTLINE=$(grep -n -v ^"#" $1 | head -n1 | cut -d: -f1)
          sed -n "${PRESETFILEFIRSTLINE},\$p" $1 | grep -i -E '^[[:space:]]*([[:alnum:]_]+[[:space:]]*\(\)|function[[:space:]]+[[:alnum:]_]+)' | sed -e 's/[(){)]//g' | sed -e 's/function //I' | sed 's/\r$//g'
           exit 0
           shift
      esac
  done

}

### main ####
_parseArguments $@
