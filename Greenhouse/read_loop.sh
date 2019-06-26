#!/bin/bash

#read_loop_scrip="sudo python /home/Per/read_loop.py"

#for i in {1..6}
#do

# Check that default root exist
#route -e | grep default > /dev/null
#if [ $? != "0" ]; then
#	echo "$(route -e | grep default)" >> /home/Per/read_loop.log
#	echo "$(date): recreate default route" >> /home/Per/read_loop.log
#	sudo route add default gw 192.168.2.1 wlan0
#fi

if [ "$(/sbin/ip route | awk '/default/ { print $3 }')" !=  "192.168.2.1" ]; then
	echo "$(date): recreate default route" >> /home/Per/read_loop.log
	sudo route add default gw 192.168.2.1 wlan0
fi

# Check if process is running
if ! pgrep -f "sudo python /home/Per/read_loop.py" > /dev/null
then
	sudo python /home/Per/read_loop.py &
	echo "$(date): read_loop.py started" >> /home/Per/read_loop.log
fi

#	sleep 10
#done