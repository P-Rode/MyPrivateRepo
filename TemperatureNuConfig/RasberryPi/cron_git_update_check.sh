#!/bin/bash

# ****************************************************************
#
# This script is created to be used by crontab to make sure that 
# git repo is updated
#
# ****************************************************************

cd ..

git remote update

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
BASE=$(git merge-base @ @{u})
extraRestart=false

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date"
elif [ $LOCAL = $BASE ]; then
    echo "Need to pull"
    logger "Git repo will be updated"

    # Check if "oneWire.py" has been changed
    git diff --name-only $LOCAL $REMOTE | grep "oneWire.py"
    rc=$?
    if [[ $rc == 0 ]]; then
      # oneWire.py, need restart after pull
      extraRestart=true
    fi

    git pull
	rc=$?; if [[ $rc != 0 ]]; then logger "pull in cron_rasberry_display.sh failed"; fi

    if [ "$extraRestart" = true ]; then
	 pkill oneWire.py
    fi
elif [ $REMOTE = $BASE ]; then
    echo "Need to push"
else
    echo "Diverged"
fi