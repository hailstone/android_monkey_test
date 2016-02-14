'''

@author: shwang
'''
import os
import time

# LogFilePath_PC = os.getcwd()
LogFilePath_PC = os.path.normpath("/Users/hailstone01/Coding/android_monkey3")


def getLogs(logPath):
    ret = os.popen("adb shell ls {}".format(logPath)).readlines()
    targetFile = 0
    line = 0
    for i in range(len(ret)):
        timestamp = get_timestamp(ret[i])
        # print timestamp
        if int(timestamp) > targetFile:
            targetFile = int(timestamp)
            line = i

    return ret[line].strip()


def get_timestamp(fn):
    fh = fn.strip("\n").strip()
    timestamp = fh.split("-")[-1].split(".")[0]

    return timestamp


def adbPull(logPath, logFile, filePath_PC=LogFilePath_PC):
    if os.path.exists(filePath_PC):
        # os.popen("adb pull {0}{1} {2}\\{3}".format(logPath, logFile, filePath_PC, logFile))
        os.popen("adb pull {0}{1} {2}{3}{4}".format(logPath, logFile, filePath_PC, os.path.sep, logFile))

    else:
        print "The path you typed is not existed. Please try again after you create it."


def getLatestLogFile(logPath, filePath_PC=LogFilePath_PC):
    logFile = getLogs(logPath)
    adbPull(logPath, logFile)
    time.sleep(5)
    # if os.path.exists("{}\\{}".format(filePath_PC, logFile)):
    if not os.path.exists("{}{}{}".format(filePath_PC, os.path.sep, logFile)):
        os.popen('adb shell su -c "chmod 777 {}"'.format(logPath + os.sep + logFile))
        adbPull(logPath, logFile)
        time.sleep(5)

    if os.path.exists("{}{}{}".format(filePath_PC, os.path.sep, logFile)):
        print "log file pull done at {}{}{}".format(filePath_PC, os.path.sep, logFile)
        # return "{}\\{}".format(filePath_PC, logFile)
        return "{}{}{}".format(filePath_PC, os.path.sep, logFile)
    else:
        print "failed to pull log file"


def getLatestLogFile2(logPath, filePath_PC=LogFilePath_PC):
    logFile = getLogs(logPath)
    adbPull(logPath, logFile)
    time.sleep(5)
    # if os.path.exists("{}\\{}".format(filePath_PC, logFile)):
    if os.path.exists("{}{}{}".format(filePath_PC, os.path.sep, logFile)):
        print "log file pull done at {}{}{}".format(filePath_PC, os.path.sep, logFile)
        # return "{}\\{}".format(filePath_PC, logFile)
        return "{}{}{}".format(filePath_PC, os.path.sep, logFile)
    else:
        print "failed to pull log file"


if __name__ == "__main__":
    logPath = "/data/local/tmp/MTlog/"
    print getLatestLogFile(logPath)
