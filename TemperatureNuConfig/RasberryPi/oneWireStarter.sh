#!/bin/sh

# ****************************************************
# Script that controll that RasberryPi.py is running
# ****************************************************

ps auxw | grep oneWire.py | grep -v grep | grep -v sudo > /dev/null

if [ $? != 0 ]; then
	msg="INFO: Starting oneWire.py because it was not running"
	logger $msg
	echo $msg
	cd /home/Per/MyPrivateRepo/TemperatureNuConfig/RasberryPi
	/usr/bin/python2.7 oneWire.py -d 1&
fi

#if ! git diff-index --quiet HEAD --; then
#	msg="INFO: Updating git repo and restarting oneWire.py"
#	logger $msg
#	echo $msg
#	git pull
#	pkill oneWire.py
#	cd /home/Per/MyPrivateRepo/TemperatureNuConfig/RasberryPi
#	/usr/bin/python2.7 oneWire.py -d 1&
#fi