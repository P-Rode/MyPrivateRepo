#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
import RPi.GPIO as GPIO ## Import GPIO library
import time
import argparse

GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(7, GPIO.OUT)  ## Setup GPIO Pin 7 to OUT
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Botten GPIO-18, Sockerbit-12
GPIO.setwarnings(False)

# *****************************************************************************
'''
------------------------------------------------------
        Main

------------------------------------------------------
'''

# Parse argument to python script
PARSER = argparse.ArgumentParser(description='This is temperature log script')


PARSER.add_argument('-d', '--DeBug', type=int, choices=[0, 1, 2],
                    help='This parameter could be used ' +
                    'when debug is wanted. ' +
                    'Debug level could change between ' +
                    '0, 1, 2 and 3:\n' +
                    '0 = Debug is off' +
                    '1 = loop 5 times, sleep 3 sec',
                    default=0,
                    required=False)

PARSER.add_argument('-t', '--time', help='Time to open watering (minutes)',
					# action='store_true',
					default=10,
                    required=False)

PARSER.add_argument('-o', '--open', help='Open watering', action='store_true',
                    required=False)

PARSER.add_argument('-c', '--close', help='Close watering', action='store_true',
                    required=False)

args = PARSER.parse_args()
debug_level = args.DeBug
open_water = args.open
close_water = args.close

# *****************************************************************************
watering_time = float(args.time)

if debug_level == 0:
	loop = 1
	watering_time = watering_time * 60
elif debug_level == 1:
	loop = 5
	watering_time = 3
	print "loop = %s" % (loop)
	print "watering_time = %s" % (watering_time)

if open_water:
	if GPIO.input(18): # Don't open if level is finished
		GPIO.output(7,True) ## Turn on GPIO pin 7
		#if watering_time != 10:
		#    print "Don't combine -o and -t"
		#    sys.exit(1) 
elif close_water:
	GPIO.output(7,False) ## Turn off GPIO pin 7
else:
	for _ in range(loop):
        if GPIO.input(18): # Don't open if level is finished
    		print "Set gpio 7 high"
    		GPIO.output(7,True) ## Turn on GPIO pin 7

    		time.sleep(watering_time)

    		print "Set gpio 7 low"
    		GPIO.output(7,False) ## Turn on GPIO pin 7
    		if loop > 1:
    			time.sleep(watering_time)
