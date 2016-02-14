# -*- coding: utf-8 -*-
import time
import subprocess
import thread
import sys
import logging


# from log import logger

class AdbDevice():
    def __init__(self, Type=None, serialNumber=None):
        self.adbType = self.getadbType(Type, serialNumber)
        self._NeedQuote = None
        self._isRooted = None

    def getadbType(self, Type, serialNumber):
        adbType = "adb "
        if serialNumber:
            adbType += "-s %s " % serialNumber
        elif Type:
            adbType += Type + " "
        return adbType

    def timer(self, process, TimeOut):
        num = 0
        while process.poll() == None and num < TimeOut * 10:
            num += 1
            time.sleep(0.1)
        if process.poll() == None:
            # os.system("taskkill /T /F /PID %d"%process.pid)
            # print process.pid
            logging.log(logging.WARN, u"%d process timeout" % process.pid)
        thread.exit_thread()

    def runShellCmd(self, Cmd, TimeOut=3, returnSub=False):
        #		print Cmd
        return self.runCmd("shell \"%s\" " % Cmd, TimeOut, returnSub)

    def _check_need_quote(self):
        cmd = "su -c ls -l /data/data"
        result = self.runShellCmd(cmd)
        if result == None:
            return
        for line in result:
            if 'com.android.phone' in line:
                self._NeedQuote = False
        if self._NeedQuote == None:
            self._NeedQuote = True

    def is_rooted(self):
        result = str(self.runShellCmd('id'))
        return result.find('uid=0(root)') >= 0

    def runRootShellCmd(self, Cmd, TimeOut=3, returnSub=False):
        if self._isRooted == None:
            self._isRooted = self.is_rooted()
        if self._isRooted:
            return self.runShellCmd(Cmd, TimeOut, returnSub)
        if self._NeedQuote == None:
            self._check_need_quote()
        if self._NeedQuote:
            return self.runShellCmd("""su -c '%s'""" % Cmd, TimeOut, returnSub)
        else:
            #			print Cmd
            return self.runShellCmd("""su -c %s""" % Cmd, TimeOut, returnSub)

    def runCmd(self, Cmd, TimeOut=5, returnSub=False, Retry=3):
        while Retry > 0:
            try:
                return self.runCmdOnce(Cmd, TimeOut, returnSub)
            except RuntimeError:
                pass
            Retry -= 1

    def runCmdOnce(self, Cmd, TimeOut=3, returnSub=False):
        #  		print "runCmdOnce is running"
        process = subprocess.Popen(self.adbType + Cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if not returnSub:
            thread.start_new_thread(self.timer, (process, TimeOut))
            # output,Error=process.communicate()
            res = process.stdout.read()
            process.wait()
            if process.poll() != 0:
                error = process.stderr.read()
                logging.log(logging.WARN, error)
                logging.log(logging.WARN, u"adb execution error or timeout")
                logging.log(logging.WARN, self.adbType + Cmd)
                if "killing" in error:
                    logging.log(logging.WARN, "adb shell does not work")
                    sys.exit(1)
                if ("device not found" in res) or ("device not found" in error) or ("offline" in error) or ("offline" in error):
                    logging.log(logging.WARN, "device is not connected")
                # sys.exit(1)
                if "Android Debug Bridge version" in (res or error):
                    logging.log(logging.WARN, "adb command error")
                    sys.exit(1)
                if "more than one" in (res or error):
                    logging.log(logging.WARN, "several devices connected. please use -s parameters")
                    sys.exit(1)
                raise RuntimeError("adb execution error or timeout:" + self.adbType + Cmd)
            res = res.replace("\r\n", "\n").splitlines()
            # 			print res
            if len(res) == 0:
                return None
            return res
        else:
            return process

    def list_process(self):
        '''fetch the process list
        '''
        processList = []
        result = self.runShellCmd("/system/bin/ps")
        for line in result[1:]:
            # 			logging.log(logging.ERROR, line)
            line = line.split()
            processList.append({"processname": line[-1], "pid": line[1]})
        return processList

    def getProcessPId(self, ProcessName):
        processList = self.list_process()
        # 		logger.debug(processList)
        PidList = []
        for process in processList:
            if process["processname"] == ProcessName:
                PidList.append(process["pid"])
                # 		print "####################################################"
                # 		logging.log(logging.WARN,PidList)
        return PidList

    def killProcess(self, pid=None, processname=None):
        if pid:
            self.runRootShellCmd("kill %s" % pid)
        elif processname:
            pidList = self.getProcessPId(processname)
            for pid in pidList:
                self.runRootShellCmd("kill %s" % pid)
        else:
            raise RuntimeError('killProcess error')

    def killMonkey(self, pid=None):
        if pid:
            self.runShellCmd("kill %s" % pid)
        else:
            raise RuntimeError("killProcess error")

    def get_state(self):
        res = self.runCmd(self.adbType + "get-state")
        if not res:
            logging.log(logging.WARN, "adb connection interrupted")
            return
        return res.readline()[0]

    def wait_for_device(self, timeOut=120):
        if not self.runCmd(self.adbType + "wait-for-device", timeOut):
            print "adb wait timeout"

    def install_package(self, path, TimeOut=120):
        res = self.runCmd("install -r \"%s\"" % path, TimeOut)
        if res == None or "Failure" in res[1]:
            logging.log(logging.WARN, "Failed to install application.")
            return False
        logging.log(logging.WARN, "Install:%s" % path)
        return True

    def uninstall_package(self, package, TimeOut=30):
        if self.runCmd("uninstall %s" % package, TimeOut) == None:
            logging.log(logging.WARN, "Failed to uninstall application.")
            return False
        logging.log(logging.WARN, "Uninstall:%s" % package)
        return True


if __name__ == "__main__":
    adbDevice = AdbDevice()
    adbDevice.killMonkey(int(adbDevice.getProcessPId("com.android.commands.monkey")[0]))