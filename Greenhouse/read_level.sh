#!/bin/bash

#read_loop_scrip="sudo python /home/Per/read_loop.py"

#for i in {1..6}
#do

# Check that default loop exist
route -e | grep default
if [ $? != "0" ]; then
	sudo route add default gw 192.168.2.1 wlan0
else
	#sudo python read_level.py
fi

# Check if process is running
if ! pgrep -f "sudo python /home/Per/read_loop.py" > /dev/null
then
	sudo python /home/Per/read_loop.py &
	echo "$(date): read_loop.py started" >> /home/Per/read_loop.log
fi

#	sleep 10
#done