#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import subprocess


GPIO.setmode(GPIO.BCM)

GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Toppen GPIO-14, Sockerbit-8
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP) # 1/4 kvar GPIO-15, Sockerbit-10
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Botten GPIO-18, Sockerbit-12

def execute_command(bash_com):
<<<<<<< HEAD
	print "uabrode in loop"
	process = subprocess.Popen(bash_com.split(), stdout=subprocess.PIPE)
	#process = subprocess.Popen(bash_com.split(), shell=True)
	# process = subprocess.Popen(bash_com, shell=True)
	# process = subprocess.call(bash_com, shell=True)
	output, error = process.communicate()
	#print "bash_com = %s" % (bash_com)
	#print "output = %s" % (output)
	#print "error = %s" % (error)

def new_execute_command(bash_com):
	out = subprocess.check_output(bash_com, stderr=subprocess.STDOUT, shell=True)
	#print "stderr = %s" % (stderr)
	print "uabrodeout: %s" %(out.split('\t')[0])
=======
	print "P-Rode in loop"
	process = subprocess.Popen(bash_com.split(), stdout=subprocess.PIPE)
	#process = subprocess.Popen(bash_com.split(), shell=True)
	# process = subprocess.Popen(bash_com, shell=True)
	# process = subprocess.call(bash_com, shell=True)
	output, error = process.communicate()
	#print "bash_com = %s" % (bash_com)
	#print "output = %s" % (output)
	#print "error = %s" % (error)

def new_execute_command(bash_com):
	out = subprocess.check_output(bash_com, stderr=subprocess.STDOUT, shell=True)
	#print "stderr = %s" % (stderr)
	print "P-Rodeout: %s" %(out.split('\t')[0])
>>>>>>> branch 'master' of https://github.com/uabrode/MyPrivateRepo.git

print "**************************"
top_input_state = GPIO.input(14)
water_low_sent = GPIO.input(15)
water_finished_sent = GPIO.input(18)
print "**************************"

print "top_input_state %s" % (top_input_state)
#if top_input_state == False:
#	print "send notification top_input_state"
#	execute_command("curl -X POST https://maker.ifttt.com/trigger/{Info-WaterFull}/with/key/koGp0BdT9BKhl5aOow8Sp")

print "water_low_sent %s" % (water_low_sent)
#if water_low_sent == False:
#	print "send notification water_low_sent"
#	execute_command("curl -X POST https://maker.ifttt.com/trigger/{Warning-WaterLow}/with/key/koGp0BdT9BKhl5aOow8Sp")

print "water_finished_sent %s" % (water_finished_sent)
#if water_finished_sent == False:
#	print "send notification water_finished_sent"
#	execute_command("curl -X POST https://maker.ifttt.com/trigger/{Allert-WaterFinished}/with/key/koGp0BdT9BKhl5aOow8Sp")

