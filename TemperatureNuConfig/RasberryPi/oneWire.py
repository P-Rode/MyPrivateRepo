#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
import os.path
import argparse
import time
import logging
import itertools
import subprocess
import smtplib

# Currently unused import
# import os
# import base64
# import smtplib
# import xml.etree.ElementTree as ET
# import xml.etree.cElementTree as ET

from email.MIMEMultipart import MIMEMultipart
from datetime import datetime
from email.MIMEText import MIMEText
from cookielib import logger
from email.mime.text import MIMEText

global __dryRun__, debug_level, __BURNER_ON_CHECK__, __OFF_TIME_CHECK__,\
    __PELLETS_COUNTER_CHECK__, __MAX_TIME_OFF_SENT__

MY_NAME = os.path.basename(__file__)

# All temperature givers
GIVER_PATH = "/mnt/1wire/"
GIVER = {}
GIVER["AckTopp"] = "10.039D55010800/temperature"
GIVER["Burner"] = "10.049655010800/temperature"
GIVER["Shunt"] = "10.3B8F55010800/temperature"
GIVER["AckBottom"] = "10.3EEF55010800/temperature"
GIVER["Out"] = "10.71EE55010800/temperature"
GIVER["?_2"] = "05.4AEC29CDBAAB"
GIVER["Counter"] = "1D.8ABD0D000000/counter.A"
GIVER["?_4"] = "81.966034000000"

# Create lists with 12 positions for each giver
ACK_TOPP_LIST = [None]*12
ACK_BOTTOM_LIST = [None]*12
BURNER_LIST = [None]*12
SHUNT_LIST = [None]*12
OUT_LIST = [None]*12
TIME_LIST = [None]*12
PELLETS_COUNTER_LIST = [None]*12

# A list with all giver lists
ALL_GIVERS_LIST = [TIME_LIST, ACK_TOPP_LIST, ACK_BOTTOM_LIST, BURNER_LIST,
                   SHUNT_LIST, OUT_LIST]

'''
How many rpms per kg pellets?

Empiriskt =>
39varv => 4,76kg
'''
TURNS_PER_KG_PELLETS = 8.19

password = None

# Set initial values
temp_count = 0
loop_count = 0
pellets_on_counter = 0
pellets_off_counter = 0

# This boolean is used the first time script is started to set initial values
INITIAL_READING = True

# These variables are used to only send mail once
__OFF_TIME_CHECK__ = True
__PELLETS_COUNTER_CHECK__ = True
__MAX_TIME_OFF_SENT__ = False

TIME_FORMAT = '%Y-%b-%d  %H:%M.%S'

'''
Max nr of durations on 10 minutes time period
This is used to indicate if we are out of pellets
'''
MAX_PELLETS_ROTATIONS_IN_CYCLE = 10

'''
Create a list with two times stored
Two times is selected because we want to compare between
two burner cykles
'''
ON_TIME_LIST = [None]*2
OFF_TIME_LIST = [None]*2

# This is used when debugging
__dryRun__ = False
debug_level = 0

androidDebug = False
if androidDebug:
    __dryRun__ = True
    debug_level = 0

'''
I noted that burning started at 44 degree C in normal condition. This mean
that temperature will go down more before heating has started again.
'''
LOW_TEMP_EMAIL_LIMIT = 30
LOW_TEMP_MESSAGE_SENT = False

# When temperature on burner is detected as off
BURNER_OFF_TEMPERATURE_LIMIT = 37

# Logging is not done in syslog. We have our own log file
LOG_FILE = ('/var/log/%s' % MY_NAME).replace('.py', '.log')
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
if debug_level > 0:
    print 'Debug logfile %s' % LOG_FILE

# =========================================================================


def check_if_program_is_running(CMD_LINE):

    import psutil
    # sudo apt-get install build-essential python-dev python-pip
    # sudo pip install psutil
    # sudo python -c "import psutil"

    for p in psutil.process_iter():
        try:
            if p.cmdline() == CMD_LINE:
                print "%s process was running" % CMD_LINE[0]
                return True
        except psutil.Error:
            pass
    return False


def check_giver(giver):
    '''
    Check giver and return value
    '''

    # Check if file exist
    if os.path.isfile(GIVER_PATH + GIVER[giver]):
        # Check content of file and return
        return file_get_contents(GIVER_PATH + GIVER[giver])
        # return path(GIVER_PATH + GIVER[giver] + '/temperature').bytes()
        # subprocess.call(["cat", GIVER_PATH + GIVER['AckTopp'] + temperature])
    else:
        print "Patch to giver %s (%s) does not exists"\
            % (giver, GIVER_PATH + GIVER[giver])


def file_get_contents(filename):
    ''' Docstring '''
    # http://stackoverflow.com/questions/3642080/using-python-with-statement-with-try-except-block
    # with Timeout(5.0) as timeout_ctx:
    try:
        # By using predefined clean-up, we don't have to close file
        with open(filename, "r") as file_obj:
            fileContent = file_obj.readline()
    except IOError:
        logging.error("Failed to open file, %s" % filename)
        # return ... error
    return fileContent


def write_to_xml():
    '''
    int: rpm         # Nr of rpm
    str: action      # Aktion could be stop or start
    str: time        # Time when action occurred

    https://www.youtube.com/watch?v=OAfeQuNhcps
    '''
    from xml.etree.ElementTree import ElementTree
    from xml.etree.ElementTree import Element
    # import xml.etree.ElementTree as etree

    root = Element('Action')
    tree = ElementTree(root)
    skruv = Element('Skruv')
    root.append(skruv)
#    return skruv


# def send_to_xmlfile(skruv, action, time, rpm):
    skruv.text = str('786234876')
    root.set('start', '13:26:65')

    skruv.text = str('5467490')
    root.set('start', '13:35:65')
    # print etree.tostring(root)
    tree.write(open(r'/tmp/oneWire.xml', 'w'))


def send_value_to_xml_file(GiverList, Giver):
    ''' Send value to xml file '''
    print "In send_value_to_xml_file procedure"

#     for i in range(0, 6):
#         print "Sent [%d] %s => %s" % (i, Giver, str(GiverList[i]))

#     for i in range(len(ACK_TOPP_LIST)):
#         print TIME_LIST[i]
#         print "------------"
#         print ACK_TOPP_LIST[i]
#         print ACK_BOTTOM_LIST[i]
#         print BURNER_LIST[i]
#         print SHUNT_LIST[i]
#         print OUT_LIST[i]
#         print


def remove_all_elements():
    '''
    Every 60th minute 6 values are saved on file. At that
    time values are removed from temp list
    '''

    print "Remove"
    for dummyLoop in range(len(ACK_TOPP_LIST)):
        ACK_TOPP_LIST.pop()
        ACK_BOTTOM_LIST.pop()
        BURNER_LIST.pop()
        SHUNT_LIST.pop()
        OUT_LIST.pop()

    return True


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


def build_mail_message():
    '''
    This method is is used to collect mailmessage... maby a clas or a string
    '''


def send_log_to_output_message(outputMsg, debug_level=0):
    '''
    A method that send message to standard output and to logfile
    '''
    # Have to make sure that outputMsg is s string
    outputMsg = str(outputMsg)

    logging.info(str(time.strftime(TIME_FORMAT)) + ': ' + outputMsg)

    if debug_level > 2:
        print outputMsg
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


def time_delta(from_time, to_time):
    '''
    Return time difference between from_time and to_time
    '''

    return datetime.strptime(to_time,
                             TIME_FORMAT) - datetime.strptime(from_time,
                                                              TIME_FORMAT)


def check_burner_on(BURNER_LIST, PELLETS_COUNTER_LIST, debug_level=0):
    '''
    Return True if burner is on
    '''

    # No idea to check temperature if BURNER_LIST[2] is still default None
    if BURNER_LIST[2]:
        if debug_level > 1:
            print "**** check_burner_on"
            print "     Burner[0]    Burner[1]    Burner[2]"
            print "     %s        %s         %s"\
                % (str(BURNER_LIST[0]),
                   str(BURNER_LIST[1]),
                   str(BURNER_LIST[2]))

            print "     BURNER_LIST[0]-BURNER_LIST[2] = %d"\
                % (BURNER_LIST[0]-BURNER_LIST[2])
            print "     Counter[0]    Counter[1]    Counter[2]"
            print "     %s       %s       %s"\
                % (PELLETS_COUNTER_LIST[0],
                   PELLETS_COUNTER_LIST[1],
                   PELLETS_COUNTER_LIST[2])

        # Could not just compare BURNER_LIST[0] and BURNER_LIST[1].
        # Temperature might go down even though burner is on.
        # Therfore check if diff is greater than 6 between 0 and 2.
        if ((BURNER_LIST[0] >= BURNER_OFF_TEMPERATURE_LIMIT) and
                ((BURNER_LIST[0]-BURNER_LIST[2]) >= -5)) or BURNER_LIST[0] > 38:
            # Burner is on
            if debug_level > 1:
                print "    check_burner_on, return=True"
            return True
        else:
            # Burner is off
            if debug_level > 1:
                print "    check_burner_on, return=False"
            return False


def burner_is_off():
    '''This method set global booleans that is changed at burner off'''

    global __BURNER_ON_CHECK__, __OFF_TIME_CHECK__, __PELLETS_COUNTER_CHECK__

    __BURNER_ON_CHECK__ = True
    __PELLETS_COUNTER_CHECK__ = False
    __OFF_TIME_CHECK__ = True


def burner_is_on():
    '''This method set global booleans that is changed at burner on'''

    global __BURNER_ON_CHECK__, __OFF_TIME_CHECK__, __PELLETS_COUNTER_CHECK__,\
        __MAX_TIME_OFF_SENT__

    __BURNER_ON_CHECK__ = False
    __PELLETS_COUNTER_CHECK__ = True
    __OFF_TIME_CHECK__ = False

    if __MAX_TIME_OFF_SENT__:
        outputMsg = ("Alarm ceasing: MAX_TIME_OFF_minutes")
        send_mail('*** 1-wire ceasing ***', outputMsg, password)
        __MAX_TIME_OFF_SENT__ = False


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


# =========================================================================


'''
------------------------------------------------------
        Main

    * Start 1-wire if needed
    * Initial burner
    * Start infinit loop
        * Read or set values for each giver
        * Low limit check in acktank
        * Check if burner is switched on
        * Check if burner is switched off
        * The time that has elapsed sins last burner
        * Unusually high pellet consumption
        * Store readings in xml file
        * sleep 10 minutes
------------------------------------------------------
'''

# Parse argument to python script
PARSER = argparse.ArgumentParser(description='This is temperature log script')

PARSER.add_argument('-d', '--DeBug', type=int, choices=[0, 1, 2],
                    help='This parameter could be used ' +
                    'when debug is wanted.' +
                    'Debug level could change between ' +
                    '0, 1, 2 and 3:' +
                    '0 = Debug is off' +
                    '1 = No email' +
                    '2 = Email and extra printouts',
                    default=0,
                    required=False)
PARSER.add_argument('-e', '--dryrun', help='This parameter could ' +
                    'be used when dryrun without ' +
                    'temperature equipment installed', action='store_true',
                    required=False)
PARSER.add_argument('-p', '--password', help='Google email password',
                    action='store_true', required=False)
PARSER.add_argument('-b', '--burner', help='If used, burner is on',
                    action='store_true', required=False)
PARSER.add_argument('-r', '--remote_debug', help='Eclipse remote debugger',
                    action='store_true', required=False)

args = PARSER.parse_args()
burnerArg = args.burner
debug_level = args.DeBug

# *****************************************************************************

# append pydev remote debugger
if args.remote_debug:

    #     # Check id PYTHONPATH exists
    #     if os.path.isfile('PYTHONPATH'):
    #         sys.path.append('/home/Per/python/pysrc')
    #     else:
    #         os.environ['PYTHONPATH'] = '/home/Per/python/pysrc'

    # import sys
    sys.path.append(r'/home/Per/python/pysrc')
    # import pydevd;pydevd.settrace()

    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        # with the addon script.module.pydevd, only use `import pydevd`
        import pydevd
        # stdoutToServer and stderrToServer redirect stdout and
        # stderr to eclipse console
        pydevd.settrace('192.168.2.101',
                        port=5678,
                        stdoutToServer=True,
                        stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " +
                         "You must add org.python.pydev.debug.pysrc to " +
                         "your PYTHONPATH.")
        sys.exit(1)

#         REMOTE_DBG = True
#         # append pydev remote debugger
#         if REMOTE_DBG:
#             # Append path to local pysrc file
<<<<<<< HEAD
#             import sys; sys.path.append(r'/home/uabrode/temp/pysrc')
=======
#             import sys; sys.path.append(r'/home/P-Rode/temp/pysrc')
>>>>>>> branch 'master' of https://github.com/uabrode/MyPrivateRepo.git
#             # Make pydev debugger works for auto reload.
#             # Note pydevd module need to be copied in
#             # XBMC\system\python\Lib\pysrc
#             try:
#                 import pydevd
#                 # stdoutToServer and stderrToServer redirect stdout and
#                 # stderr to eclipse console
#                 pydevd.settrace(host='147.214.199.120',
#                                 port=5678,
#                                 stdoutToServer=True,
#                                 stderrToServer=True)
#             except ImportError:
#                 sys.stderr.write("Error: " +
#                                  "You must add org.python.pydev.debug.pysrc" +
#                                  " to your PYTHONPATH.")
#                 assert True, "Import of pydevd failed"

# *****************************************************************************

# dryRun = args.dryRun


# https://infohost.nmt.edu/tcc/help/pubs/python/web/argparse-add_argument.html
# dryRun = args.dryrun
if debug_level >= 2:
    print "dryrun = %s" % __dryRun__
    print "debug_level = %s" % debug_level

# Startup 1-wire if not running
OWNFS_COMMAND = ['/usr/lib/owfs/owfs', '-c', '/etc/owfs.conf', '-u',
                 '--allow_other', '/mnt/1wire/', '--Celsius']
if not check_if_program_is_running(OWNFS_COMMAND):
    logging.info('owfs is not started. 1-wire process will be started')
    subprocess.call(OWNFS_COMMAND)

if debug_level >= 1:
    print '%s : %s script started, pid=%s'\
        % (str(time.strftime(TIME_FORMAT)), MY_NAME, os.getpid())
logging.info('%s : OneWire script started, pid=%s'
             % (str(time.strftime(TIME_FORMAT)), os.getpid()))


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

# Initialiting of program
initialGiver = []
pellets_on_counter = int(check_giver("Counter"))
pellets_off_counter = int(check_giver("Counter"))

# Initial time values. Two instances should be enough.
ON_TIME_LIST.insert(0, time.strftime(TIME_FORMAT))
OFF_TIME_LIST.insert(0, time.strftime(TIME_FORMAT))

write_to_xml

print ">>>>>>> Burner initial start!! <<<<<<<<"
for _ in itertools.repeat(None, 3):
    initialGiver.append(round(float(check_giver("Burner")), 2))
    print "**** Initial burner giver = %s degree" % initialGiver[-1]
    if initialGiver[-1] > BURNER_OFF_TEMPERATURE_LIMIT:
        # Pellets burner is on
        burner_is_on()
        pellets_on_counter = int(check_giver("Counter"))
    else:
        # Pellets burner is off
        burner_is_off()
        pellets_off_counter = int(check_giver("Counter"))
    time.sleep(120)

if initialGiver[2] + initialGiver[0] > 75:
    burner_is_on()
    pellets_on_counter = int(check_giver("Counter"))

# If argument is used this overrule __BURNER_ON_CHECK__
if burnerArg:
    burner_is_on()

print "    __BURNER_ON_CHECK__ = %s, Pellets initial onCounter = %s,\
    offCounter = %s"\
    % (str(__BURNER_ON_CHECK__), str(pellets_on_counter),
       str(pellets_off_counter))

outputMsg = "**** Burner is off is %s, counter is %s"\
    % (str(__BURNER_ON_CHECK__), str(pellets_on_counter))
logging.info(outputMsg)

if debug_level >= 1:
    print outputMsg

# Send mail at initial start
msg = "Burner script %s (%s) has inittial started. %s"\
    % (MY_NAME, os.getpid(), str(time.strftime(TIME_FORMAT)))
send_mail("Burner script has started", msg, password)

print ">>>>>>> Burner init ready!! <<<<<<<<"

'''
Start endless loop
'''
while True:
    loop_count += 1
    temp_count += 1

    # system_resource_printout()

    '''
    Read or set values for each giver
    '''
    if __dryRun__:
        # Set some dummy values if dryrun is set
        TIME_LIST.insert(0, time.strftime(TIME_FORMAT))
        ACK_TOPP_LIST.insert(0, 60)
        ACK_BOTTOM_LIST.insert(0, 50)
        BURNER_LIST.insert(0, 30)
        SHUNT_LIST.insert(0, 35)
        OUT_LIST.insert(0, 5)
    else:
        TIME_LIST.insert(0, time.strftime(TIME_FORMAT))
        ACK_TOPP_LIST.insert(0, round(float(check_giver("AckTopp")), 2))
        ACK_BOTTOM_LIST.insert(0, round(float(check_giver("AckBottom")), 2))
        BURNER_LIST.insert(0, round(float(check_giver("Burner")), 2))
        SHUNT_LIST.insert(0, round(float(check_giver("Shunt")), 2))
        OUT_LIST.insert(0, round(float(check_giver("Out")), 2))
        PELLETS_COUNTER_LIST.insert(0, int(check_giver("Counter")))

    if debug_level >= 1:
        print '-----------------------------------'
        print "loop_count = %s" % (loop_count)
        print str(time.strftime(TIME_FORMAT))
        print "Out    Burner  AckBottom  AckTopp"
        print "%s   %s    %s     %s" % (OUT_LIST[0],
                                        BURNER_LIST[0],
                                        ACK_BOTTOM_LIST[0],
                                        ACK_TOPP_LIST[0])
        print '-----------------------------------'

    ''''
    Low limit check in acktank

    Make sure that temperature in acktank has not passed low-limit
    '''
    if ACK_TOPP_LIST[0] <= LOW_TEMP_EMAIL_LIMIT:
        outputMsg = \
            "*** Pellets burner: AckTopp lowlimit exceeded " +
            "(%s < %s) ***" % (ACK_TOPP_LIST[0], LOW_TEMP_EMAIL_LIMIT)
        send_log_to_output_message(outputMsg, debug_level)

        # Only send message once
        if LOW_TEMP_MESSAGE_SENT is False:
            send_mail('*** 1-wire alert ***', outputMsg, password)
            LOW_TEMP_MESSAGE_SENT = True
    else:
        LOW_TEMP_MESSAGE_SENT = False

    '''
    Check if burner is switched on

    Remember the time and send log message
    '''
    if BURNER_LIST[2]:
        if check_burner_on(BURNER_LIST, PELLETS_COUNTER_LIST, debug_level):
            print "**** Burner is switched on"
            # This code should only be executed once when burner is stared
            if __BURNER_ON_CHECK__:
                burner_is_on()
                ON_TIME_LIST.insert(0, TIME_LIST[2])
                pellets_on_counter = PELLETS_COUNTER_LIST[2]
                # offTime = time.strftime(TIME_FORMAT)
                outputMsg = "*** Pellets burner: Switched on: " +
                "%s, Start counter: %s, Delta time(%s-%s): %s"\
                    % (str(TIME_LIST[2]),
                       str(pellets_off_counter),
                       str(OFF_TIME_LIST[0]),
                       str(ON_TIME_LIST[0]),
                       str(time_delta(OFF_TIME_LIST[0], ON_TIME_LIST[0])))
                if debug_level >= 2:
                    send_mail('*** 1-wire info ***', outputMsg, password)
                send_log_to_output_message(outputMsg, debug_level)

    '''
    Check if burner is switched off

    Remember the time and send log message
    '''
    if BURNER_LIST[2]:
        if not check_burner_on(BURNER_LIST,
                               PELLETS_COUNTER_LIST, debug_level):
            print "**** Burner is switched off"
            # This code should only be executed once when burner is stopped
            if __BURNER_ON_CHECK__ is False:
                burner_is_off()
                OFF_TIME_LIST.insert(0, TIME_LIST[2])
                pellets_off_counter = PELLETS_COUNTER_LIST[2]

                send_log_to_output_message('pellets_off_counter ' +
                                           '= ' + str(pellets_off_counter),
                                           debug_level=3)
                send_log_to_output_message('pellets_on_counter ' +
                                           '= ' + str(pellets_on_counter),
                                           debug_level=3)
                send_log_to_output_message('TURNS_PER_KG_PELLETS' +
                                           ' = ' + str(TURNS_PER_KG_PELLETS),
                                           debug_level=3)

                # Check div by 0
                try:
                    _pellets_per_count_ = ((pellets_off_counter -
                                            pellets_on_counter) /
                                           TURNS_PER_KG_PELLETS)
                except ZeroDivisionError:
                    _pellets_per_count_ = 0

                send_log_to_output_message('_pellets_per_count_' +
                                           ' = ' + str(_pellets_per_count_),
                                           debug_level=3)

                outputMsg = "*** Pellets burner: Switched off " +
                    "(%s), Delta counter(%s-%s): %s, Delta kg: %s Delta time: %s"\
                    % (str(TIME_LIST[2]),
                       str(pellets_off_counter),
                       str(pellets_on_counter),
                       str(pellets_off_counter - pellets_on_counter),
                       str(round(_pellets_per_count_, 1)),
                       time_delta(ON_TIME_LIST[0], OFF_TIME_LIST[0]))
                if debug_level >= 2:
                    send_mail('*** 1-wire info ***', outputMsg, password)
                send_log_to_output_message(outputMsg, debug_level)

    '''
    The time that has elapsed sins last burner

    This is created to check how long time it is between burner
    was swtitched off.
    This could be a early indication if sometrhing is going wrong.
    '''

    # We could not compare times unless we ha two readings
    # One burner off and one on must exist, that's the reason why
    # a list with two enrtries exists
    if __OFF_TIME_CHECK__:
        if OFF_TIME_LIST[0]:
            timeDelta = time_delta(OFF_TIME_LIST[0], TIME_LIST[0])

            # Read current temp, round and typecast to int
            current_out_temperature = int(round(float(OUT_LIST[0]), 0))

            # Default value
            MAX_TIME_OFF_minutes = 12*60

            if current_out_temperature < -11:
                MAX_TIME_OFF_minutes = 3*60
            elif current_out_temperature < -4:
                MAX_TIME_OFF_minutes = 6.5*60
            elif current_out_temperature < -1:
                MAX_TIME_OFF_minutes = 7.5*60
            elif current_out_temperature < -2:
                MAX_TIME_OFF_minutes = 8.5*60
            elif current_out_temperature < 5:
                MAX_TIME_OFF_minutes = 9.5*60
            elif current_out_temperature < 7:
                MAX_TIME_OFF_minutes = 11.5*60
            elif current_out_temperature >= 10 and\
                    current_out_temperature <= 12:
                MAX_TIME_OFF_minutes = 15*60

            print (MAX_TIME_OFF_minutes)

            # MAX_TIME_OFF_minutes is in minutes but compare is done in secconds

            if timeDelta.seconds > MAX_TIME_OFF_minutes*60:
                __OFF_TIME_CHECK__ = False
                __MAX_TIME_OFF_SENT__ = True
                outputMsg = ("MAX_TIME_OFF_minutes (%s min) excceded. "
                             "Current time_delta: %s."
                             % (MAX_TIME_OFF_minutes, (timeDelta.seconds)/60))
                send_mail('*** 1-wire alert ***', outputMsg, password)
                send_log_to_output_message(outputMsg, debug_level)

    '''
    Unusually high pellet consumption

    One indication that something is wrong is that pellets counter has increased
    a lot. The reason for this is that pellets is not filled and bulk is empty.

    If counter switch stay with switch in on. The counter will increase
    unreasable. Therefore diff > 100 is ignored
    '''
    if __PELLETS_COUNTER_CHECK__:
        __PELLETS_COUNTER_CHECK__ = False
        if PELLETS_COUNTER_LIST[1]:
            diff = PELLETS_COUNTER_LIST[1]-PELLETS_COUNTER_LIST[0]
            if diff >= MAX_PELLETS_ROTATIONS_IN_CYCLE:
                if diff < 100:
                    outputMsg = "*** Pellets burner: Max number" +\
                        "rpms (%s) has exceeded %s. This " +\
                        "could indicate that pellets is finished."\
                        % (str(MAX_PELLETS_ROTATIONS_IN_CYCLE),
                           str(PELLETS_COUNTER_LIST[1]-PELLETS_COUNTER_LIST[0]))
                    send_mail('*** 1-wire alert ***', outputMsg, password)
                    send_log_to_output_message(outputMsg, debug_level)

    '''
    Store readings in xml file

    This is created to prepare fore storage of all burner vallues in an xml.
    The intention is to store 6 values e.g. efery hour.
    Every 6 count (6*10min) we store values on file
    '''
    if temp_count >= 6:
        temp_count = 0

        if debug_level >= 2:
            print "send_value_to_xml_file"

            send_value_to_xml_file(TIME_LIST, "Time")
            send_value_to_xml_file(ACK_TOPP_LIST, "AckTop")
            send_value_to_xml_file(ACK_BOTTOM_LIST, "AckBottom")
            send_value_to_xml_file(BURNER_LIST, "Burner")
            send_value_to_xml_file(SHUNT_LIST, "Shunt")
            send_value_to_xml_file(OUT_LIST, "Out")


#         for i in range(len(ACK_TOPP_LIST)):
#             print TIME_LIST[i]
#             print "------------"
#             print ACK_TOPP_LIST[i]
#             print ACK_BOTTOM_LIST[i]
#             print BURNER_LIST[i]
#             print SHUNT_LIST[i]
#             print OUT_LIST[i]
#             print
#
#         root = ET.Element("root")
#         doc = ET.SubElement(root, "doc")
#
#         ET.SubElement(doc, ACK_TOPP_LIST[1],
#            name=ACK_BOTTOM_LIST[1]).text = BURNER_LIST[1]
#
#         ET.SubElement(doc, ACK_TOPP_LIST[2],
#            name=ACK_BOTTOM_LIST[2]).text = BURNER_LIST[2]
#
#         tree = ET.ElementTree(root)
#         tree.write("filename.xml")

        # send_value_to_xml_file
#         assert remove_all_elements(), "Failed to remove element"

    '''
    This is the timer that tell script how often it should read all givers
    '''
    if __dryRun__:
        sleepTimer = 4
    else:
        sleepTimer = 600

    # sleepTimer = 600
    if debug_level >= 1:
        print "Sleep %d" % sleepTimer
    time.sleep(sleepTimer)
#     if cond:
#         break

'''
This is a teardown printout message, to be able to know if script is terminated
in a controlled way
'''
outputMsg = "*** Pellets burner: Script is terminating!!! ***"
send_mail('*** 1-wire alert ***', outputMsg, password)
send_log_to_output_message(outputMsg, debug_level)
