#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from __future__ import print_function

import RPi.GPIO as GPIO
import time
import subprocess
import logging


GPIO.setmode(GPIO.BCM)

GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Toppen GPIO-14, Sockerbit-8
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP) # 1/4 kvar GPIO-15, Sockerbit-10
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Botten GPIO-18, Sockerbit-12

water_full_sent = False
water_low_sent = False
water_finished_sent = False

TIME_FORMAT = '%Y-%b-%d  %H:%M.%S'

def send_mail(mailSubject, mailMessage, password):
    '''
    Send a mail according to following example:
    https://docs.python.org/2/library/email-examples.html
    '''

    mailSender = 'per.rodenvall@gmail.com'
    mailReceiver = 'per.rodenvall@gmail.com'

    msg = MIMEMultipart()
    msg['From'] = mailSender
    msg['To'] = mailReceiver
    msg['Subject'] = mailSubject

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    msg.attach(MIMEText(mailMessage, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(mailSender, password)
    text = msg.as_string()
    server.sendmail(mailSender, mailReceiver, text)
    server.quit()


def send_log_to_output_message(outputMsg, debug_level=0):
    '''
    A method that send message to standard output and to logfile
    '''

    # Have to make sure that outputMsg is s string
    outputMsg = str(outputMsg)

    logging.info(str(time.strftime(TIME_FORMAT)) + ': ' + outputMsg)

    if debug_level > 2:
        print (outputMsg)
        logging.debug(str(time.strftime(TIME_FORMAT)) + ': ' + outputMsg)

def check_password():
    '''
    Check for AuthPass in /etc/ssmtp/ssmtp.conf
    Return password
    '''
    with open("/etc/ssmtp/ssmtp.conf") as openfile:
        for line in openfile:
            for passLine in line.split():
                if "AuthPass=" in passLine:
                    return passLine.split('=')[-1]

def system_resource_printout():

    p = subprocess.Popen(["vmstat"], stdout=subprocess.PIPE)
    output, err = p.communicate()
    send_log_to_output_message("Output from vmstat: %s %s" % (output, err))

    p = subprocess.Popen(["df"], stdout=subprocess.PIPE)
    output, err = p.communicate()
    send_log_to_output_message("Output from df: %s %s" % (output, err))

    p = subprocess.Popen(["free", "-m"], stdout=subprocess.PIPE)
    output, err = p.communicate()
    send_log_to_output_message("Output from free -m: %s %s" % (output, err))

def execute_command(bash_com):
    process = subprocess.Popen(bash_com.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

def send_WaterFull():
    # Event name: Info-WaterFull
    # Notification: Info: Water full
    global water_full_sent

    if not water_full_sent:
        print ("send_WaterFull")
        write_to_logfile("send_WaterFull")
        execute_command("curl -X POST https://maker.ifttt.com/trigger/{Info-WaterFull}/with/key/koGp0BdT9BKhl5aOow8Sp")
        water_full_sent = True

def send_WaterLow():
    # Event name: Warning-WaterLow
    # Notification: Warning: Low water!
    global water_low_sent

    if not water_low_sent:
        print ("send_WaterLow")
        write_to_logfile("send_WaterLow")
        execute_command("curl -X POST https://maker.ifttt.com/trigger/{Warning-WaterLow}/with/key/koGp0BdT9BKhl5aOow8Sp")
        water_low_sent = True

def send_WaterFinished():
    # Event name: Allert-WaterFinished
    # Notification: Allert: Water finished!
    global water_finished_sent

    if not water_finished_sent:

        if top_input_state:
            write_to_logfile("ERROR: Top could not be true when finish is false")

        if half_input_state:
            write_to_logfile("ERROR: Half level could not be true when finish is false")

        print ("send_WaterFinished")
        write_to_logfile("send_WaterFinished")
        execute_command("curl -X POST https://maker.ifttt.com/trigger/{Allert-WaterFinished}/with/key/koGp0BdT9BKhl5aOow8Sp")

        water_finished_sent = True
        water_full_sent = True
        water_low_sent = True

def write_to_logfile(log_content):
    # Send string to logfile with
    # date and time

    logfile = 'read_loop.log'

    f = open(logfile, 'a')
    f.write("%s: %s\n" % (str(time.strftime(TIME_FORMAT)), str(log_content)))
    f.close()

#def check_valid-vallues(top, middle, bottom):
#    if not top and (middle or bottom):
#       print "Some water level indicator is faulty"

'''
 # Make sure that passwortd is defined
password = check_password()
if password:
    # Mailpassword ok
    outputMsg = "Mail password fetched"
    if debug_level >= 1:
        logging.info(outputMsg)
        print outputMsg
    else:
        logging.info(outputMsg)
else:
    outputMsg = "ERROR: Password is not defined"
    logging.debug(outputMsg)
    print outputMsg
    sys.exit()
 '''
 
'''
MAIN

To get curl to work, default route had to be added...
sudo route add default gw 192.168.2.1 wlan0
'''
#for lp in range(100):
while True:
    # print "**************************"

    #top_input_state_old = top_input_state

    top_input_state = GPIO.input(14)
    half_input_state = GPIO.input(15)
    bottom_input_state = GPIO.input(18)

    if top_input_state == True:
        send_WaterFull()

        # If water is full that mean that no
        # notifications are sent
        water_low_sent = False
        water_finished_sent = False
    else:
        water_full_sent = False

    if half_input_state == False:
        send_WaterLow()
    else:
        water_low_sent = False

    if bottom_input_state == False:
        send_WaterFinished()
    else:
        water_finished_sent = False

    time.sleep(15)