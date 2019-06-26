#!/bin/bash

# Crontab:
# 0,15,30,45 * * * * /home/Per/MyPrivateRepo/TemperatureNuConfig/RasberryPi/temperaturNuCronJobb_RasberryPi.sh
# TIME: 09:32:48 , DATE: 20 Feb ,Temp: -11.69

#if [ 3 -gt $(ps -ef | grep temperaturNuCronJobb_RasberryPi.sh | wc -l) ]
#then
#    logger "Start temperaturNuCronJobb_RasberryPi.sh"
#	/home/Per/MyPrivateRepo/TemperatureNuConfig/RasberryPi/temperaturNuCronJobb_RasberryPi.sh
#fi

echo "TIME: $(date +"%H:%M:%S") , DATE: $(date +"%d %b") ,Temp: $(cat /mnt/1wire/10.71EE55010800/temperature)" > /var/www/html/index.lighttpd.html
