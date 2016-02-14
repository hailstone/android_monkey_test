'''
Created on 2014-11-19

@author: shwang
@version: 2.0
@changes: rewrite parse scripts and the expect output for a crash would include four parameters below: 
 - bug summary: "java.lang.IllegalStateException at android.widget.ListView.layoutChildren(ListView.java)(class android.widget.HeaderViewListAdapter)" for example
 - app crash log file: log file name like "app_crashcom.sgiggle.staging_2015-01-16_23_36_49.563_.txt", and None if not exist
 - the count of crash after remove the duplications which will be added in the summary for bug reporting on JIRA
 - the detailed crash track for bug reporting on JIRA
 
@author: shwang
@version: 3.0
@changes: Add support for ANR issue analysis

@author: shwang
@version: 4.0
@changes: Add support for activity summary

@author: shwang
@version: 4.1
@changes: Add support for counting the duration for a single Monkey test thread

@author: shwang
@version: 4.2
@changes: Add a flag to record the status to deal with multiple 'Caused by' in the crash track

@author: shwang
@version: 5.0
@changes: Refactor ANR parser to support fetching ANR log file captured by system
'''

import os

def parse_monkeyLog_crash(filePath):   
    # parse the log file and output all detailed crash tracks into a list
    crashList = []
    if os.path.isfile(filePath):
        fh = open(filePath, "r").readlines()
    else:
        return
    
    for lineNumb, line in enumerate(fh):
        fl = []
        if "// CRASH: com.sgiggle" in line:
            fl.append(line)
            for fline in fh[lineNumb+1:lineNumb+120]:
                if fline.startswith("/") or fline =="\n" or fline.startswith("app_crash"):
                    if not fline.startswith("// CRASH:"):
                        if not fline.startswith("// NOT RESPONDING:"):
                            fl.append(fline)
                    else:
                        break

            crashList.append(fl)
               
    return crashList

def parse_monkeyLog_anr(filePath):
    # parse the log file and output all detailed ANR tracks (max line is 200) into a list
    anrList = []
    if os.path.isfile(filePath):
        fh = open(filePath, "r").readlines()
    else:
        return
    
    for lineNumb, line in enumerate(fh):
        fl = []
        if "ANR in com.sgiggle." in line:
            fl.append(line)
            for fline in fh[lineNumb+1:lineNumb+200]:
                if not fline.startswith(":Sending ") or fline.startswith("app_anr"):
                    #or not fline.startswith(":Switch:")
                    fl.append(fline)
                else:
                    break
                
            anrList.append(fl)
        
    return anrList

def parse_crash(crash):
    # parse the log file and output a list, including summary and logFile ("None" if not available) in each item
    if crash:
        adapter = ""
        err = cause = ""
        attaFile = None
        err_long = ""
        flag = True
        for i in range(len(crash)):
            if "Short Msg:" in crash[i]:
                msg = crash[i]
                err = str(msg).strip().split(":")[1]
                    
            if "Long Msg:" in crash[i]:
                msg = crash[i]
                err_long = str(msg).strip().split(":",1)[1]       
            
            if flag and "Caused by" in crash[i]:
                #err = crash[i]
                if i != len(crash)-1:
                    cause = crash[i+1]
                    cause = parse_cause_nonTango(cause)
                    for j in range(i+1, len(crash)):
                        if "com.sgiggle." in crash[j] and not "app_crashcom" in crash[j]:
                            cause = crash[j]
                            flag = False
                        
                            break
                        if "me.tango" in crash[j]:
                            cause = crash[j]
                            flag = False
                            break
                       
            
            if "// Caused by: java.lang.IllegalStateException" in crash[i]:
                # add special dealing with this kind of crash to get the rooted adapter
                adapter_line = crash[i]
                adapter = parse_adapter(adapter_line)
              
            if "app_crashcom.sgiggle" in crash[i]:
                # get the detailed logFile name if available
                attachment = crash[i]
                attaFile = parse_attachment(attachment)
                break
            
        if err != " Native crash":  
            summary = err + " at " + toString(cause) + adapter
            summary = summary.strip("\n")
        else:
            summary = err_long
        
    return (summary, attaFile)

def parse_anr(anr):
    attaFile = None
    summary_activity = anr[0].strip("\n")
    summary_reason = anr[1].strip("\n")
    if not summary_reason.startswith("Reason:"):
        summary_reason = anr[2].strip("\n")
    summary = summary_activity + "({0})".format(summary_reason)
    
    for i in range(len(anr)):
        if "anr_com.sgiggle" in anr[i]:
            # get the detailed logFile name if available
            attachment = anr[i]
            attaFile = parse_attachment(attachment)
            break
            
    return (summary, attaFile)

def parse_cause_nonTango(cause):
    # add special dealing with those rooted non-Tango activities 
    if ":" in cause:
        new_cause = cause.split(":")[0]
        new_cause += ")"
    else:
        new_cause = cause
    
    return new_cause

def parse_attachment(attachment):
    return attachment.split(":")[0]

def toString(alist):
    astr = str(alist)
    if "by:" in astr:
        astr = astr.split(":")[1].strip()
    if "at " in astr:
        astr = astr.split("at",1)[1].strip()
        
    return astr

def parse_adapter(cause):
    # Special handling to get the adapter for the kind of crash: java.lang.IllegalStateException
    adapter = ""
    if "with Adapter" in cause:
        adapter = cause.split("with Adapter")[1].strip().strip("]")
    
    if "adapter: class com." in cause:
        cls = cause.split("adapter:")[1].strip()
        adapter = "({})".format(cls)
        #adapter.replace("class", "adapter")
    return adapter
    
def get_all_desc_crash(crashList):
    desc = []
    for i in range(len(crashList)):
        (summary, attaFile) = parse_crash(crashList[i])
        desc.append((summary, attaFile, crashList[i]))
    
    return desc

def get_all_desc_anr(anrList):
    desc = []
    for i in range(len(anrList)):
        (summary, attaFile) = parse_anr(anrList[i])
        desc.append((summary, attaFile, anrList[i]))
    
    return desc

def crashList_remove_duplicated(crashList):
    # remove duplications and also return the count for each crash or ANR
    new_crashList = []
    set_crashList = []
    for i in range(len(crashList)):
        set_crashList.append(crashList[i][0])
    
    crashSet = set(set_crashList)
    for item in crashSet:
        for j in range(len(crashList)):
            if item in crashList[j][0]:
                new_crashList.append((item, crashList[j][1], set_crashList.count(item), crashList[j][2]))
                break
        
    return new_crashList

def get_all_crash_track(fp):
    # the interface to get all crash tracks for analysis
    crashList = parse_monkeyLog_crash(fp)
    summaryList = get_all_desc_crash(crashList)
    allCrash = crashList_remove_duplicated(summaryList)

    return allCrash

def get_all_anr_track(fp):
    # the interface to get all ANR tracks for analysis
    anrList = parse_monkeyLog_anr(fp)
    summaryList = get_all_desc_anr(anrList)
    allANR = crashList_remove_duplicated(summaryList)
    
    return allANR

def parse_activities(filePath):
    # parse all allowed activities
    actList = []
    #if os.path.isfile(filePath):
    if os.path.exists(filePath):
        fh = open(filePath, "r").readlines()
    else:
        return
    
    for line in fh:
        if "// Allowing start of Intent" in line:
            if "cmp=" in line:
                #print line
                actList.append(line.split("cmp=")[1].split("/")[1].split("}")[0].strip())
    return actList

def count_activities(actList):
    # get all allowed activities and their counts
    actLists = []
    actSet = set(actList)
    for item in actSet:
        actLists.append((item, actList.count(item)))
        
    sortList = sorted(actLists, key=lambda x:x[1], reverse=True)    
    return sortList

def get_activities(filePath):
    actList = parse_activities(filePath)
    sortList = count_activities(actList)
    return sortList

def get_duration(filePath):   
    # get the actual duration for a monkey test thread
    firstTime = lastTime = 0
    if os.path.isfile(filePath):
        fh = open(filePath, "r").readlines()
    else:
        return
    
    for i in range(len(fh)-1, 0, -1):
        if "//[calendar_time" in fh[i]:
            lastTime = parse_time(fh[i])
            break
            #return lastTime
        
    for j in range(len(fh)):
        if "//[calendar_time" in fh[j]:
            firstTime = parse_time(fh[j])
            break
    print lastTime
    print firstTime
    duration = int(lastTime) - int(firstTime)
    return trans_duration(duration)
    
def trans_duration(ms):
    minute = ms / 60000
    hour = minute / 60
    # 2 minutes is for the costing time on the fist 100 and the final events
    minute = minute % 60 + 2
    
    return (hour, minute)

def parse_time(uptime):
    return uptime.strip().replace("]","").split("system_uptime:")[1]

if __name__ == "__main__":
    logFile = "C:\\Users\\shwang\\tango_android_3.20.182097_20151119190656-HTCs720e-M-staging2-201511201750.log"
    #parse_activities(logFile)
    print get_duration(logFile)
    """
    crashTrack = get_all_crash_track(logFile)
    anrTrack = get_all_anr_track(logFile)
    for i in range(len(crashTrack)):
        print crashTrack[i][0]
    print anrTrack
    """
        
