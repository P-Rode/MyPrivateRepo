#!/bin/bash

# http://xmodulo.com/check-internet-speed-command-line-linux.html
# wget https://raw.github.com/sivel/speedtest-cli/master/speedtest_cli.py
# chmod a+rx speedtest_cli.py
# sudo mv speedtest_cli.py /usr/local/bin/speedtest-cli
# sudo chown root:root /usr/local/bin/speedtest-cli

# 2017-01-03
# The file speedtest_cli.py has been deprecated in favor of speedtest.py
# and is available for download at:
#
# https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py
# wget https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py
# chmod a+rx speedtest.py
# sudo mv speedtest.py /usr/local/bin/speedtest
# sudo chown root:root /usr/local/bin/speedtest



echo "*************************************************" >> /home/pi/SpeedTest.log
echo $(date) >> /home/pi/SpeedTest.log
echo "*************************************************" >> /home/pi/SpeedTest.log

wget -q http://c.speedtest.net/speedtest-servers-static.php
wget -q http://c.speedtest.net/speedtest-servers-static
/usr/local/bin/speedtest >> /home/pi/SpeedTest.log

rm /home/pi/speedtest-servers-static.php*
rm /home/pi/speedtest-servers-static*

# crontab -e
# crontab -l
# 0 0-23/1 * * * /home/pi/internetSpeed.sh
