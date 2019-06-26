import subprocess
import itertools
import sys
import traceback
import datetime
import time
import xmlrpclib
import errno
from asynccmdexecutor import CmdExecutor
from socket import error as socket_error

def lxcstate(nodeName):
    """ return the current state for this node """
    state = ""
    try:
        state = subprocess.check_output(["sudo", "lxc-info", "-n",
                                        nodeName, "-s"])
        state = ''.join(state).split()[1]
    except subprocess.CalledProcessError as err:
#         log.error("failed to get state of lxc node rc: %s, out: %s"
#                   % (err.returncode, err.output))
        print "error 1"
        raise
    return state

def start(nodeName, sync=True):
    ''' start a node '''
    # print("Starting node %s" % nodeName)
    if lxcstate(nodeName) == "STOPPED":
        cmd = "sudo lxc-start -d -n %s </dev/null" % nodeName
        subprocess.call(cmd, shell=True)
    else:
        raise RuntimeError("LXC container %s is not in STOPPED state"
                           % nodeName)
    wait_lxcstate(nodeName, "RUNNING", timeout='1m')

    if sync:
        sync(nodeName)

def wait_lxcstate(nodeName, state, timeout='0s'):
    """ wait for this lxc node to have the 'state'. Uses linux timeout.
    read 'man timeout' for how to set the timeout lenght, 0s means wait
    infinite amout of seconds"""
    try:
        subprocess.check_call(["sudo", "timeout", timeout, "lxc-wait",
                               "-n", nodeName, "-s", state])
    except subprocess.CalledProcessError as err:
        if err.returncode is 124:
#             log.error("timeout was reached while waiting for " +
#                       "state to become %s using lxc-wait, rc=124" % state)
            print "error 2"
        else:
#             log.error("lxc-wait returned non zero while waiting for " +
#                       "state to become %s, rc: %s, out: %s" %
#                       (state, err.returncode, err.output))
            print "error 3"
        raise

def stop(nodeName):
    ''' stop/shutdown a node '''
    # TODO(hafe) rename to shutdown
    # print("Stopping node %s" % nodeName)

    if lxcstate(nodeName) == "STOPPED":
        return

    # self.hosted_sus_disconnect()

    # Stop services "manually". This is needed because the ordering between
    # the init scripts and the upstart job for syslog does not seem to
    # work at shutdown.
    # TODO(hafe): investigate why and fix, add upstart job for opensaf?

    # First stop immxmlrpcd since it depends on opensaf
    # self.lxc_cmd("/etc/init.d/immxmlrpc stop")

    # Then stop opensaf
    # self.lxc_cmd("/etc/init.d/opensafd stop")

    # ---Then kill what remains of the container
    poweroff(nodeName)

def poweroff(nodeName):
    ''' stop a container and its processes, wait for STOPPED state '''
    #print("Poweroff node %s" % self.name)

    # first stop osafamfwd preventing it from rebooting the node
    # when lxc-stop randomly kills processes in the container
    lxc_cmd(nodeName, "pkill -STOP osafamfwd")

    # if lxc-stop hangs, command will timeout after 30 sec
    cmd = "sudo timeout 30 lxc-stop -k -n %s" % nodeName

    # Normally the container is already terminated at this point so
    # ignore the annoying "XX-X is not running" on stderr
    # In lxc v1 lxc-stop returns an error when stopping an already stopped
    # container so ignore the return code using call
    # (instead of check_call)
    devnull = open("/dev/null")
    subprocess.call(cmd, shell=True, stderr=devnull)

    # Sometimes the lxc-stop fails (container restarts)
    # We check if the container are still running,
    # if so we issue lxc-stop again
    if lxcstate(nodeName) == "RUNNING":
#         print("lxc-stop did not work, try once more for %s"
#                   % self.name)
        subprocess.call(cmd, shell=True, stderr=devnull)

    wait_lxcstate(nodeName, "STOPPED", timeout='1m')

def lxc_cmd(nodeName, cmd, check_rc=False, timeout=180, debug=False,
            runas_user="root"):
    '''Run command inside container using lxc-attach.
    Check returncode and returns a tuple with the return code and
    output from command

        string: cmd
            # Command to be executed

        boolean: check_rc = False/[True]
            # Check or ignore the returncode from command

        integer: timeout = 180
            # Timeout when command fail

        boolean: debug = False/[True]
            # Printout debug information

        string: runas_user = root/[user defined]
            # Run command as root or some other userdefined user
    '''

    print "**** uabrode lxc_cmd nodeName = ", nodeName
    print "**** uabrode lxc_cmd cmd = ", cmd
    print "**** uabrode lxc_cmd check_rc = ", check_rc

    if lxcstate(nodeName) == "RUNNING":
        if debug:
            # print("lxc_cmd: node:%s '%s'" % (self.name, cmd))
            print "error 4"

        cmd = "timeout %u sudo lxc-attach -n %s -- su - %s -c \'%s\';"\
              % (timeout, nodeName, runas_user, cmd)
        localcmd = cmd + " exit $?"
        ret = 0

        if not check_rc:
            try:
                output = subprocess.check_output(localcmd, shell=True)

            except subprocess.CalledProcessError as err:
                ret = err.returncode
                output = err.output

                if ret > 128:
#                     print("If returncode > 128, this mean that some" +
#                               " subshell has failed, not the actual" +
#                               " binary test. Fault could be ignored." +
#                               "Please see \"Test Result\" from binary " +
#                               "test. Failed: 0 mean that it's passed")
                    print "error 5 (ret > 128). Node = " + nodeName
                    traceback.print_exc(file=sys.stdout)
                    sys.exit(0)

                # timeout commands returns 124 at timeout
                if ret == 124:
#                     log.error(self.name + ": TIMEOUT for cmd: '%s'" % cmd)
                    print "error 6"

            if debug:
#                 print("localcmd: %s" % localcmd)
#                 print("%s: output: %s" % (self.name, output))
                print "error 7"
        else:
            try:
                output = subprocess.check_output(localcmd, shell=True,
                                                 stderr=subprocess.STDOUT)

                if len(output) > 0 and debug is True:
#                     print("localcmd: %s" % localcmd)
#                     print("%s: output: %s" % (self.name, output))
                    print "error 8"
            except subprocess.CalledProcessError as err:
                ret = err.returncode
                output = err.output

                if ret > 128:
#                     print("If returncode > 128, this mean that some" +
#                               " subshell has failed, not the actual" +
#                               " binary test. Fault could be ignored." +
#                               "Please see \"Test Result\" from binary " +
#                               "test. Failed: 0 mean that it's passed")
                    print "error 9"

                # timeout commands returns 124 at timeout
                if ret == 124:
#                     log.error(self.name + ": TIMEOUT for cmd: '%s'" % cmd)
                    print "error 10"
                else:
#                     log.error(self.name + ": return code %d \
#                     from cmd : %s, %s"
#                               % (ret, cmd, err.output))
                    print "error 11"
                raise
        return ret, output
    else:
#         print("Node %s not running, command (%s) not sent."
#                   % (self.name, cmd))
        print "error 12"

def disturbanceWaitForSync(function, *args):
    '''
    This method sends a command and waits for "Cold sync complete"

    obj: testcase         # Testcase from running test
    obj: function         # Command to be executed (without parentheses)
    obj: *args            # Parameter to command above

    '''

    # This is a preparation for next test step, where we need sync message
    # after cluster restart
    log_banner(nodes, "Wait for entry in sylog")
    # syncReady = syslogListener("NO Cold sync complete", nodes)
    syncReady = syslogListener("(CRON) STARTUP (fork ok)", nodes)

    function(*args)
    # sleep(1)

    # Wait and see that expected sync message has been received in syslog
    syncReady.wait_ok(20)

def syslogListener(searchPattern, nodes, node=None, timeout=120):
    '''
    This method is used to create a listener for a searchPattern in
    syslog for a specific node. Method return a pointer to a object.
    If node is omitted search in all syslog files would be done

    String searchPattern (example "NO Sync starting")
    String node (example "SC-1")

    Example how to use:

    Create listener
    opensafStarted = \
        self.cluster.syslogListener("services successfully started")

    Check that message was received in syslog (search in all syslogs)
    opensafStarted.wait_ok(tmo=timeout)
    '''
    # lxcPath = os.environ.get('LXC_PATH')
    lxcPath = "/var/lib/lxc"

    print("Prepare listener, \"%s\"" % searchPattern)

    if node:
        cmd = "sudo timeout %d tail -n 1 -f %s/%s/rootfs/var/log/syslog\
         | (grep -m 1 \"%s\"; pkill -P $$ sudo)"\
         % (timeout, lxcPath, node, searchPattern)
    else:
        # Create a "follow" variable that include all syslogs in cluster
        follow = ""
        for node in nodes:
            follow += "-f %s/%s/rootfs/var/log/syslog "\
                % (lxcPath, node)
        cmd = "sudo timeout %d tail -n 1 %s | (grep -m 1 \"%s\"; pkill -P $$\
        sudo)" % (timeout, follow, searchPattern)
    return CmdExecutor(cmd)

def log_banner(nodes, msg, debuglog=True): 
    ''' syslog to all nodes in the cluster (which needs to be started) '''
    if debuglog is True:
        print(msg)

    for node in nodes:
        if lxcstate(node) == "RUNNING":
            print "**** uabrode:log_banner ", datetime.datetime.now()
#            time.sleep(1)
#             print "**** uabrode:log_banner after sleep ", datetime.datetime.now()
            # cmd = "sudo lxc-attach -n %s -- logger -t osaftest \"%s\"" % (node, msg)
            cmd = "logger -t osaftest \"%s\"" % (msg)
            # cmd = "echo TEST"
            rc, outp = lxc_cmd(node, cmd, check_rc=True)
            print "**** uabrode after lxc_cmd", datetime.datetime.now()
            print "**** uabrode command = ", cmd
            print "**** uabrode returncode = ", rc
            assert rc == 0, "ReturnCode of the %s command: %s" % (localcmd, rc)
            # subprocess.call(cmd.split())

def sync(nodeName):
    ''' sync a node '''
    print ("Syncing node %s" % nodeName)
    wait_lxcstate(nodeName, "RUNNING", timeout='0s')

#         proxy = xmlrpclib.ServerProxy('http://%s:%u' % (
#             self.ip, self.imm_xmlrpc_port))
    proxy = xmlrpclib.ServerProxy('http://%s:%s' % (
        "10.0.3.101", "9000"))

    synced = False
    # wait for the IMM XML RPC server to respond
    # before it is up we get connection refused exceptions
    for i in range(60):
        try:
            proxy.ping()
        except socket_error as serr:
            if serr.errno != errno.ECONNREFUSED:
                # some other error, re-raise
                raise serr
            # connection refused, sleep and try again
            time.sleep(1)
        else:
            synced = True
            break

    # sanity check that the loop eventually made it
    assert synced


#-----------------------------------------------------------------------

nodes = ["SC-1", "SC-2", "SC-3", "SC-4", "SC-5"]
# nodes = ["SC-1"]
loopNr = 0

for nodeName in nodes:
    # Make sure all lxc:s are stopped before start
    stop(nodeName)

for _ in itertools.repeat(None, 300):
    loopNr += 1
    print "----------------------"
    print "   Loop nr " + str(loopNr)
    print "----------------------"

    print " >>>>>>>>>>>> Start nodes >>>>>>>>>>>>"
    for nodeName in nodes:
        listenerThread = syslogListener(">>>>_nodeStarted_>>>>", nodes)
        # disturbanceWaitForSync
        print "**** uabrode, listenerThread created: ", datetime.datetime.now()
        start(nodeName)
        # sync(nodeName)
        print "**** uabrode, node is synced: ", datetime.datetime.now()
        # Check that lxc is started
        print "**** uabrode, node started: ", datetime.datetime.now()
        wait_lxcstate(nodeName, "RUNNING", "10")
#         time.sleep(2)
        print "**** uabrode, lxc-state = RUNNING: ", datetime.datetime.now()
#         log_banner([nodeName], ">>>> dummy >>>>", debuglog=False)
        log_banner([nodeName], ">>>>_nodeStarted_>>>>", debuglog=False)

        # Many lxc-state look like it might trigger the fault
        for _ in itertools.repeat(None, 10):
            print "State of " + nodeName + " is " + lxcstate(nodeName)

        print "**** uabrode, before Thread.wait_ok", datetime.datetime.now()
        listenerThread.wait_ok(20)

#         stop_cmd = "sleep 1 && sudo lxc-stop -n %s && sudo lxc-stop -n %s" \
#             % (stoppedSc_standby, stoppedSc_active)
#         dist_cmd = common.sendSubprocessCommand
#         common.disturbanceWaitForSync(self, dist_cmd, stop_cmd)

    print " <<<<<<<<<<<< Stop nodes <<<<<<<<<<<<"
    for nodeName in nodes:
        log_banner([nodeName], ">>>>_nodeStopped_>>>>", debuglog=False)
        stop(nodeName)
        # Many lxc-state look like it might trigger the fault
        for _ in itertools.repeat(None, 10):
            print "State of " + nodeName + " is " + lxcstate(nodeName)
