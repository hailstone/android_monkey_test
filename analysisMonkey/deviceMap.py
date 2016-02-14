'''
Created on 2014-12-26
Updated on 2016-1-14

@author: shwang
'''
import os

devices = {"HC34PW101233": "HTCs720e",
           "f84697d2": "SamsungS5",
           "5D57288A": "MiPad",
           "82724f82": "SamsungS2ATT",
           "4df1cc3727489f55": "SamsungNote2",
           "1701c443": "SamsungNote4",
           "0019502b1c10ae": "SamsungNoteI",
           "e7ae94bf": "Homgmi1S",
           "f9871e93": "SamsungS2TM",
           "23d7c686": "MiNote",
           "08b0c6ad2581bfa9": "Nexus5",
           "32044b59aa4c7173": "SamsungT700",
           "CB5A1ZKDXQ": "SonyXperiaZ2",
           "7eac292": "OnePlus",
           "HT4ABJT06089": "Nexus9",
           "016B7FFD1601201C": "Nexus",
           "BY2QUX14AU046007": "HonorL01",
           "4d00d6223a3570d5": "SamsungNoteII",
           "4df109d22ae0af0b": "SamsungNote2",
           "23d7c686": "MiNote"}

DEVICE_INFO = {"HC34PW101233": ["HTC_One_X", "HTC S720e", "ARMv7 Processor 9 rev 0 (v7l)", "971M", "1280*720", "Android 4.1.1"],
               "f84697d2": ["SamsungS5", "SM-G9008", "ARMv7 Processor 9 rev 1 (v7l)", "1704M", "1920*1280", "Android 5.0"],
               "82724f82": "SamsungS2ATT",
               "4df1cc3727489f55": "SamsungNote2",
               "1701c443": "SamsungNote4",
               "0019502b1c10ae": ["SamsungNoteI", "GT-N700", "ARMv7 Processor rev 1 (v7l)", "862M", "1280*800", "Android 4.1.2"],
               "e7ae94bf": "Homgmi1S",
               "f9871e93": "SamsungS2TM",
               "23d7c686": "MiNote",
               "08b0c6ad2581bfa9": "Nexus5",
               "32044b59aa4c7173": "SamsungT700",
               "CB5A1ZKDXQ": ["SonyXperiaZ2", "L50u", "ARMv7 Processor rev 1 (v7l)", "2789M", "1776*1080", "Android 5.1.1"],
               "7eac292": ["OnePlus", "A0001", "ARMv7 Processor rev 1 (v7l)", "2819M", "1920*1280", "Android 4.3"],
               "HT4ABJT06089": "Nexus9",
               "016B7FFD1601201C": "Nexus",
               "BY2QUX14AU046007": "HonorL01",
               "ZX1G22HD4M": ["Nexus6", "Motorola Nexus 6", "ARMv7 Processor rev 0 (v7l)", "2968M", "2392*1440", "Android 6.0.1"],
               "4d00d6223a3570d5": ["SamsungNoteII", "GT-N7102", "ARMv7 Processor rev 0 (v7l)", "1784M", "1280*720", "Android 4.3"],
               "4df109d22ae0af0b": ["SamsungNote2", "GT-N7100", "ARMv7 Processor rev 0 (v7l)", "1784M", "1280*720", "Android 4.3"],
               "LGD85721e0c317": ["Lg-g3", "LG-D857", "ARMv7 Processor rev 1 (v7l)", "2862M", "2392*1440", "Android 5.0.1"],
               "23d7c686": ["hongmi note", "HM NOTE 1LTE", "ARMv7 Processor rev 3 (v7l)", "1866M", "1280*720", "Android 4.4.4"]}


def get_Device():
    ret = os.popen("adb devices").readlines()
    if len(ret) == 1:
        print "No device detected"
    else:
        serial = ret[1].strip().split("device")[0].strip()

    return serial


def get_Device_info(serial):
    return DEVICE_INFO[serial]

    """
        if serial in devices.keys():
            return devices[serial]
        else:
            return serial
    """


def get_devices():
    ret = os.popen("adb devices").readlines()
    if len(ret) == 1:
        print "No device detected"
    else:
        print "Totally {0} device{1} detected.".format(len(ret) - 2, "s" if len(ret) > 3 else "")
        for i in range(1, len(ret)):
            serial = ret[i].strip().split("device")[0].strip()
            if serial:
                if serial in devices.keys():
                    print devices[serial] + " is connected successfully"
                else:
                    print "Unknown device " + serial + " is connected"


def deviceMap(serial):
    deviceMap = {"21d2e4b1": "Mi2",
                 "21d2e4b1": "SamsungS6"
                 }
    if serial in deviceMap.keys():
        return devices[serial]
    else:
        return serial
