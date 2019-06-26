#!/bin/bash

cat /mnt/1wire/10.039D55010800/temperature > /var/www/html/ackTopp
cat /mnt/1wire/10.049655010800/temperature > /var/www/html/burner
cat /mnt/1wire/10.3B8F55010800/temperature > /var/www/html/shunt
cat /mnt/1wire/10.3EEF55010800/temperature > /var/www/html/ackBottom
cat /mnt/1wire/10.049655010800/temperature > /var/www/html/burner
cat /mnt/1wire/10.71EE55010800/temperature > /var/www/html/out
cat /mnt/1wire/1D.8ABD0D000000/counter.A > /var/www/html/counter


echo "$(cat /var/log/oneWire.log | grep "Switched on" | tail -1)<br>" > /var/www/html/last_oneWire.log
echo "$(cat /var/log/oneWire.log | grep "Switched off" | tail -1)<br>" >> /var/www/html/last_oneWire.log