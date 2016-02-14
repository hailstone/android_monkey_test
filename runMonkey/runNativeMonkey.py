# _*_ coding:utf-8 _*
'''
Created on 2014-11-5

@author: shoubowang
'''
# from cgi import logfile

import os
import time
import random
import re
import subprocess
import shlex
import multiprocessing

import adbdevice
import deviceMap
import settings
import sharecn
import artifactory

LOCAL_DIR_ANDROID = "/mnt/sdcard"
MONKEY_PATH_ANDROID = "monkey"
LOG_PATH_ANDROID = "%s/MTlog/" % LOCAL_DIR_ANDROID


class RunMonkey():
    def __init__(self, device):
        self.device = device

    def has_logDir(self, LOG_PATH_ANDROID):
        # Create log file
        if not os.path.exists(LOG_PATH_ANDROID):
            self.device.runShellCmd("mkdir %s" % LOG_PATH_ANDROID)

    def start_monkey(self, app, branch, server, version, times, logcat=False):

        self.has_logDir(LOG_PATH_ANDROID)
        device = deviceMap.get_Device()
        # Define the monkey command
        param = []
        param.append("--throttle 450 ")
        param.append("-s {} ".format(random.randint(10, 100000)))
        package = "com.sgiggle.{}{}".format("" if app == "tango" else "mango.", "staging" if not server else server)
        param.append("-p {} ".format(package))
        # param.append("--pkg-whitelist-file /sdcard/whitelist.txt ")
        param.append("--ignore-crashes ")
        param.append("--ignore-timeouts ")
        param.append("--monitor-native-crashes ")
        param.append("--ignore-security-exceptions ")
        param.append("--pct-touch 50 ")
        param.append("--pct-syskeys 0 ")
        param.append("--bugreport ")
        param.append("-v -v -v")

        log_suffix = version + device + "-" + branch + "-" + server + "-" + time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
        logFile = "%s.log" % log_suffix
        fullLogFile = "> %s%s 2>&1" % (LOG_PATH_ANDROID, logFile)

        # start = time.time()
        self.device.runShellCmd("%s %s %s %s" % (MONKEY_PATH_ANDROID, "".join(param), times, fullLogFile), 3, True)
        # processId = self.get_pacakge_pid(package)
        # adb shell am force-stop com.sgiggle.staging
        # adb shell am start -n com.sgiggle.staging/com.sgiggle.production.SplashScreen

        if logcat:
            logFile_logcat = LOG_PATH_ANDROID + "logcat-" + logFile
            print logFile_logcat
            logcat_cmd = "logcat -v time > "
            self.device.runCmd("%s%s" % (logcat_cmd, logFile_logcat), 3, True)
        """
        while True:
            now = time.time()
            if (now - start) > 7200:
                self.device.runShellCmd("am force-stop com.sgiggle.staging")
                time.sleep(3)
                self.device.runShellCmd("am start -n com.sgiggle.staging/com.sgiggle.production.SplashScreen")
                """

    def stop_monkey(self):
        self.device.runShellCmd("kill %s" % self.processId)

    def is_monkey_running(self):
        processList = self.device.list_process()
        for process in processList:
            if process["pid"] == self.processId:
                return True
        return False

    def get_monkey_pid(self):
        Retry = 5
        while Retry > 0:
            processList = self.device.list_process()
            for process in processList:
                if process["processname"] == "com.android.commands.monkey":
                    return process["pid"]
            time.sleep(0.3)
            Retry -= 1
        return None

    def get_pacakge_pid(self, package):
        Retry = 5
        while Retry > 0:
            processList = self.device.list_process()
            for process in processList:
                if process["processname"] == package:
                    return process["pid"]
            time.sleep(0.3)
            Retry -= 1
        return None

    def get_logcat_pid(self):
        Retry = 5
        while Retry > 0:
            processList = self.device.list_process()
            for process in processList:
                if process["processname"] == "logcat":
                    return process["pid"]
            time.sleep(0.3)
            Retry -= 1
        return None

    def stop_logcat(self):
        processID = self.get_logcat_pid()
        self.device.runShellCmd("kill %s" % processID)


def setEvents(msg, default=4500000):
    try:
        times = input(msg)
        if times != "":
            default = int(times)

    except:
        raise ValueError

    finally:
        return str(default)


def stop_video(device):
    pid = device.find_process_by_name("screenrecord")
    if pid == "":
        print "screenrecord is not running, no need to kill process"
        return
    else:
        print("screenrecord PID found: " + str(pid))
        cmd = "adb shell kill -2 " + str(pid)
        print(cmd)
        subprocess.Popen(shlex.split(cmd))
        time.sleep(10)  # video file needs some time to get completed before calling pull_video()


def video_capture(device):
    filePath = "/sdcard/MTVideoLog/"
    filename = ".mp4"
    videoWidth = 480
    videoHeight = 320
    bitRate = 250000
    if not os.path.exists(filePath):
        device.runShellCmd("mkdir %s" % filePath)

    ts = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    filename = "video" + ts + filename

    try:
        stop_video(device)
    except:
        print "error"

    device.runShellCmd("screenrecord {0}{1} --size {2}x{3} --bit-rate {4}".format(filePath, filename, videoWidth, videoHeight, bitRate))


def keep_capture(device):
    while 1:
        video_capture(device)


def runMonkey(app, branch, server, version):
    monkey = RunMonkey(adbdevice.AdbDevice())
    times = setEvents("Type the count of events to start Monkey testing. Press Enter for the default value 1,500,000.\n")
    monkey.start_monkey(app, branch, server, version, times, False)
    print "Tango Monkey is running!"
    print "press ctrl+c to stop"

    while monkey.is_monkey_running:
        try:
            if monkey.get_monkey_pid() == None:
                print 'Monkey finished!'
                break
            time.sleep(0.5)
        except KeyboardInterrupt:
            monkey.stop_monkey()
            print 'Monkey has stopped'
            break


if __name__ == "__main__":
    device = adbdevice.AdbDevice()
    need_auto_upgrade = True
    need_uninstall = False
    video_cap = False

    if need_auto_upgrade:
        # specify the source you want to download from: artifactory or shareCN (shareCN_win,shareCN_linux,shareCN_mac)
        (app, source, branch, server) = ("mango", "shareCN_mac", "N", "staging2")

        if "share" in source:
            downloadURL = sharecn.getDownloadURL(app, settings.urlForDownloading[source], settings.releaseName[branch],
                                                 settings.newServerBuild[app + "_" + server])
            apkFile = sharecn.isReadyForInstall(downloadURL, settings.localPath["current_dir"])
        else:
            downloadURL = artifactory.getDownloadURL(app, settings.releaseName[branch], settings.newServerBuild[app + "_" + server])
            apkFile = artifactory.isReadyForInstall(downloadURL, settings.localPath["current_dir"])

        if apkFile:
            # version = re.findall("\d\.\d{2}\.\d{6}-\d{14}", os.path.basename(apkFile))[0].split("-")[0].rsplit(".", 1)[1]
            ver = re.findall("\d\.\d{2}\.\d{6}-\d{14}", r"{}".format(apkFile))[0]
            version = re.findall("ango-android-\d\.\d{2}\.\d{6}-\d{14}", r"{}".format(apkFile))[0]
            reversion = "{}".format("t" if app == "tango" else "m") + version.replace("-", "_") + "-"

        if need_uninstall:
            device.uninstall_package(apkFile)
        print "Start to install the application..."
        res = device.install_package(apkFile)
        if res:
            print "Installation done."
            process_monkey = multiprocessing.Process(target=runMonkey, args=(app, branch, server, reversion))
            process_monkey.start()
            if video_cap:
                keep_capture(device)
            """
            if video_cap:
                print "start a thread to record screen"
                process_video = multiprocessing.Process(target=keep_capture(device))
                process_video.start()
                time.sleep(3)
                """

    else:
        # Please specify the revision number and server if no need to install the latest build
        # (branch, reversion, server) = ("appcompact_upgrade", "R177591-", "staging")
        print "Not install new Tango application."
        reversion = "mango_android_3.21.190378_20160114212152-"
        process_monkey = multiprocessing.Process(target=runMonkey, args=(app, branch, server, reversion))
        process_monkey.start()
        if video_cap:
            keep_capture(device)
