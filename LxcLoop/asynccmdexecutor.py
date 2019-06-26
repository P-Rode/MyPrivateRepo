#
#
#
############################################################################

''' Async command executor, status stored in a queue for later pickup
    Example:
>>> cmd = CmdExecutor("ls -l")
>>> cmd.wait_ok(tmo = 3)

'''

from threading import Thread
from Queue import Queue
from Queue import Empty
import subprocess
# from osaftest.fw.osaflog import log

class CmdExecutor(Thread):
    ''' Class for '''
    def __init__(self, cmd):
        Thread.__init__(self)
        self.queue = Queue()
        self.cmd = cmd
        self.start()
        self.output = None

    def run(self):
        ''' the thread's activity '''
        print("thread %s start cmd: '%s'" % (self.ident, self.cmd))
        try:
            self.output = subprocess.check_output(self.cmd,
                                                  stderr=subprocess.STDOUT,
                                                  shell=True)
        except subprocess.CalledProcessError as err:
            self.output = err.output
            self.queue.put(err.returncode)
        finally:
            self.queue.put(0)
        print("thread %s end cmd: '%s'" % (self.ident, self.cmd))

    def wait(self):
        ''' wait for the command to finish and return the status code '''
        assert self.cmd is not None
        returncode = self.queue.get()
        self.join()
        self.cmd = None
        return returncode

    def wait_ok(self, tmo=None):
        ''' wait for the command to finish and check the status to be OK '''
        assert self.cmd is not None
        if tmo is not None:
            try:
                returncode = self.queue.get(timeout=tmo)
            except Empty:
                assert False, "Timeout exceeded %s" % tmo
        else:
            returncode = self.queue.get()
        self.join()
        if returncode != 0:
            print("cmd failed: %s" % self.cmd)
            print(self.output)
        self.cmd = None
        assert returncode == 0, self.output
