#!/bin/bash

#myIfttUser=$1
#myMessage=$2
#opensaf_branch=$3
#myMessage=" This is some extra info"
#myIfttKey=koGp0BdT9BKhl5aOow8Sp
#opensaf_branch=develop

function executeCMD()
{    # Execute command and check return code

    runCommand=$@

	echo "Send command $runCommand"

    set -x
    set +e
    "$@"

    local exitCode=$?
    set +x
    set -e

    if [ "$exitCode" != 0 ] ; then
        echo "ERROR: \"${runCommand[@]}\" command failed with exit code $exitCode"
        echo "<<*<<*<<*<<*<< Info: Finished script $0"
        echo "Last 3 commands: $(history 3)"
        exit $exitCode
    fi
}

#------------------------------------
#------------------------------------
# Main
#------------------------------------
#------------------------------------

echo ">>*>>*>>*>>*>> Info: Start script $0"

if [ $# -eq 0 ]; then
    echo "No arguments provided, use -h for help"
    exit 1
fi

# Parse all arguments
while [ $# -ne 0 ]; do

    case "$1" in
      --help|-h)
          echo "    Help message:"
          echo "    -h or --help    # This message"
          echo "    -m        # Message as a string"
          echo "    -k        # IFTT key"
          echo "    -b        # OpenSAF branch (develop, release or master)"
          echo "    -u        # IFTT user (key is used from script)"
          exit 0
      ;;

    -m) # message
        if [ -n "$2" ] ; then
            myMessage=$2
            shift
        fi
        ;;

    -k) # IFTTT key
        if [ -n "$2" ] ; then
            myIfttKey=$2
            shift
        fi
        ;;

    -b) # OpenSAF branch
        if [ -n "$2" ] ; then
            opensaf_branch=$2
            shift
        fi
        ;;

    -u) # IFTT user
        if [ -n "$2" ] ; then
            myIfttUser=$2
            shift
        fi
        ;;

    *)
        echo "ERROR: Command argument not supported"
        exit 1
        ;;
    esac
    shift
done

case "$myIfttUser" in
	'perrodenvall')
		myIfttKey=koGp0BdT9BKhl5aOow8Sp
		echo "User is $myIfttUser, and key $myIfttKey"
	;;

	*)
		echo "ERROR: No IFTTT key is available for \"$myIfttUser\""
		exit 1
	;;
esac

executeCMD curl -X POST -H "Content-Type: application/json" -d '{"value1":"'"${opensaf_branch}"'", "value2":"'"${myMessage}"'"}' https://maker.ifttt.com/trigger/JenkinsGreen/with/key/$myIfttKey