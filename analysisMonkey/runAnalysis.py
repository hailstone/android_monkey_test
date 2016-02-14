'''
Created on 2014-11-25
Updated 3.0 on 2015-01-06
Updated 4.0 on 2015-02-06
Updated 4.1 on 2015-05-06
Updated 4.2 on 2015-06-30
Updated 4.3 on 2015-07-09

@author: shwang
@version: 3.0
@changes: rewrite scripts in:
 - get the new parsed monkey crash by four parameters (summary, crashLog, count of crash, crash track)
 - package all related log files by zip 
 
@author: shwang
@version: 4.0
@changes: Add support to file ANR issue

@author: shwang
@version: 4.1
@changes: 
- Add environment initiate function
- Add data reporting function

@author: shwang
@version: 4.2
@changes: 
- Add data reporting function: the duration for a Monkey thread
- Update ignore issue list

@author: shwang
@version: 4.3
@changes: 
- Unused IGNORE_ISSUE and use its resolution by instead to deal with closed issues
'''

# import parse_mtLog
import os
import time

import parse_mtLog2
from jira_tango import jira_tango
import pullMonkeyLog
import deviceMap


def get_revison(fp):
    # fetch the revision number from the log file
    return os.path.basename(fp).split("-")[0]


def get_serial(fp):
    # fetch the serial from the log file
    return os.path.basename(fp).split("-")[1]


def get_device(fp):
    # fetch the device name from the log file
    serial = os.path.basename(fp).split("-")[1]
    deviveName = deviceMap.get_Device_info(serial)[0]
    return deviveName


def get_branch(fp):
    # fetch the branch name from the log fine
    return os.path.basename(fp).split("-")[2]


def get_server(fp):
    # fetch the server name from the log fine
    return os.path.basename(fp).split("-")[3]


def get_timestamp(fp):
    # fetch the time stamp from the log fine
    return os.path.basename(fp).split("-")[4]


def tar_log(fh):
    # used for Mac system only
    gz = fh.replace(".log", ".gz")
    os.popen("tar -czf {} {}".format(gz, fh))
    if os.path.exists(gz):
        return gz
    return False


def zip_log(fp, appCrash=None):
    # used for Windows system
    import zipfile

    if appCrash is None:
        lzip = fp.replace(".log", ".zip")
    else:
        appCrash += ""
        lzip = appCrash.replace(".txt", ".zip")

    fz = zipfile.ZipFile(lzip, "w", zipfile.ZIP_DEFLATED)
    fz.write(fp)
    if appCrash is not None:
        if os.path.getsize(appCrash) != 0:
            fz.write(appCrash)
        else:
            print "Ignore the app crash log due to the size is 0."
    fz.close()
    return fz


def get_projects(jira):
    projects = jira.projects()
    return projects


def track_to_str(track):
    tracklist = ""
    for i in range(len(track)):
        tracklist += track[i]

    return tracklist


def focus_issues(bugID):
    # To list all issues that needs more attentions

    FOUCS_ISSUES = []

    if bugID is FOUCS_ISSUES:
        return True

    return False


def upload_attachment(issue, attachment):
    with open(attachment, "r") as fh:
        issue.add_attachment(fh)


def create_new_issue(jira, bug_summary, bug_track, logFile, app):
    # create a new issue on Jira
    # check the metadata via http://jira.tango.corp/rest/api/2/issue/ABC-123
    tag = "{} {} {}".format(env, server, get_revison(logFile))
    testInfo = combine_test_information(get_serial(logFile), tag)
    bug_track = testInfo + bug_track
    # print bug_track
    bug_track = "{noformat}\n" + bug_track + "\n{noformat}"
    if "java.lang.Throwable" not in bug_summary or "com.sgiggle." in bug_summary:
        appendix = "[Actual result]\nThe crash below was detected during Android monkey testing. Please checek the detailed information below."
        bug_track = appendix + bug_track

        new_issue = jira.create_issue(project={'key': 'CHN'}, summary=bug_summary,
                                      description=bug_track, issuetype={'name': 'Defect'}, assignee={'name': 'shwang'},
                                      environment=tag, customfield_10310={"value": "All android"},
                                      customfield_11616={"value": "Messenger (Tango)" if app == "tango" else "Social"},
                                      customfield_10313={"value": "{}".format(milestone)})
        time.sleep(3)

        if new_issue:
            print "new issue {} created successfully".format(bug_summary)
            return new_issue

    else:
        print "Native crash without Tango libraries below detected."
        print bug_summary
        appendix = "[Actual result]\nThe crash below was detected during Android monkey testing. Please checek the detailed information below."
        bug_track = appendix + bug_track
        tag = "{} {} {}".format(env, server, get_revison(logFile))
        new_issue = jira.create_issue(project={'key': 'CHN'}, summary=bug_summary,
                                      description=bug_track, issuetype={'name': 'Defect'}, assignee={'name': 'shwang'},
                                      environment=tag, customfield_10310={"value": "All android"},
                                      customfield_11616={"value": "Messenger (Tango)" if app == "tango" else "Social"},
                                      customfield_10313={"value": "{}".format(milestone)})
        time.sleep(3)

        if new_issue:
            print "new issue {} created successfully".format(bug_summary)
            return new_issue

            # jira.add_attachment(new_issue, attachment=tar_logfile)


def reopen_bug(jira, bugID, logFile):
    # Reopen a closed issue on Jira
    issue_tango = jira.issue(bugID)
    if not appScope(jira, bugID):
        jira.transition_issue(issue_tango, "3", assignee={'name': 'shwang'},
                              comment="Comments from autoMonkey: Reproducible on {} at {} {} {}. Reopen it now.".format(get_device(logFile),
                                                                                                                        env, server,
                                                                                                                        get_revison(
                                                                                                                            logFile)))
    else:
        jira.transition_issue(issue_tango, "3", assignee={'name': 'shwang'}, customfield_11616={"value": "Messenger (Tango)"},
                              comment="Comments from autoMonkey: Reproducible on {} at {} {} {}. Reopen it now.".format(get_device(logFile),
                                                                                                                        env, server,
                                                                                                                        get_revison(
                                                                                                                            logFile)))
    print "{} reopened successfully".format(bugID)


def get_current_app(issue):
    title = issue.fields.summary

    if "[Tango]" in title:
        app = "[Tango]"
    elif "[Mango]" in title:
        app = "[Mango]"
    elif "[Tango&Mango]" in title:
        app = "[Tango&Mango]"
    else:
        app = None

    return app


def set_current_app(app, issue):
    current = get_current_app(issue)
    if current:
        if app.capitalize() in current:
            return current
        else:
            return "[Tango&Mango]"
    else:
        return "[{}]".format(app.capitalize())


def title_times_add(issue, times, app):
    title = issue.fields.summary
    title_with_times = title.replace("[Android-Crash]", "[Android-Crash] [{} Times]".format(times + 1))
    # title_with_app = title_with_times.replace("[Android-Crash]", "[{}] [Android-Crash]".format(set_current_app(app, issue)))
    if get_current_app(issue):
        title_with_app = title_with_times.replace(get_current_app(issue), set_current_app(app, issue))
    else:
        title_with_app = title_with_times.replace("[Android-Crash]", "{} [Android-Crash]".format(set_current_app(app, issue)))

    if not appScope(jira, bugID):
        issue.update(summary=title_with_app)
    else:
        issue.update(summary=title_with_app, customfield_11616={"value": "{}".format(appScope(jira, bugID))})


def get_current_times(issue):
    title = issue.fields.summary
    # times = title.split("Time")[0].split("]")[1].split("[")[1]
    times = title.split("Time")[0].rsplit("[", 1)[1].strip()
    return int(times)


def title_times_update(issue, times, app):
    title = issue.fields.summary
    times_current = get_current_times(issue)
    times_new = times_current + times
    if "Time]" in title:
        title_with_new_times = title.replace("[{} Time".format(times_current), "[{} Times".format(times_new))
    else:
        title_with_new_times = title.replace("[{} Time".format(times_current), "[{} Time".format(times_new))

    if get_current_app(issue):
        title_with_app = title_with_new_times.replace(get_current_app(issue), set_current_app(app, issue))
    else:
        title_with_app = title_with_new_times.replace("[Android-Crash]", "{} [Android-Crash]".format(set_current_app(app, issue)))

    if not appScope(jira, bugID):
        issue.update(summary=title_with_app)
    else:
        issue.update(summary=title_with_app, customfield_11616={"value": "{}".format(appScope(jira, bugID))})


def bug_update_times(issue, times, app):
    # To update the reproducible times for a reported issue on Jira
    if "Time" not in issue.fields.summary:
        title_times_add(issue, times, app)
    else:
        title_times_update(issue, times, app)


def get_issue_total(crashTrack):
    summ = 0
    for i in range(len(crashTrack)):
        summ += crashTrack[i][2]

    return summ


def appScope(jira, bugID):
    try:
        scope = jira.issue(bugID).fields.customfield_11616
        return scope

    except:
        return False


def pullCrashLog(fn):
    # LogFilePath_PC = os.getcwd()
    LogFilePath_PC = "C:\\Users\shwang\\"
    if fn is not None:
        fp = "{}{}{}".format(LogFilePath_PC, os.path.sep, fn)
        os.popen("adb pull /sdcard/{} {}".format(fn, fp))
        if os.path.exists(fp):
            size = os.path.getsize(fp)
            print "app crash log file {} pull done".format(fp)
            print "app crash log file size: {}".format(size)
            return fp
            # zip_log(fp)
    else:
        print "no app crash log file"
        return None


def environment_init(env, milestone, server, ticket):
    # To initiate the environment:
    MILESTONE = {"Tr": "Trunk",
                 "I": "Irouleguy",
                 "J": "Jura",
                 "K": "Kabinett",
                 "L": "Lambrusco",
                 "LP": "Lambrusco+",
                 "M": "Muscadelle",
                 "N": "Nebbiolo"
                 }

    BRANCH = {"Tr": "Trunk",
              "I": "Irouleguy",
              "J": "Jura",
              "K": "Kabinett",
              "L": "Lambrusco",
              "LP": "Lambrusco+",
              "M": "Muscadelle",
              "Appcompact": "Appcompact",
              "": None,
              "N": "Nebbiolo",
              }

    SERVER = {"t2dev": "t2dev",
              "staging": "staging",
              "staging2": "staging2",
              "production": "production",
              "labdev": "labdev",
              "int1": "int1",
              "int3": "int3"
              }

    TICKET = {"J": "CHN-11760",
              "K": "CHN-12284",
              "L": "CHN-13505",
              "LP": "CHN-13505",
              "M": "CHN-14376",
              "N_tango": "CHN-14377",
              "N_mango": "CHN-15409",
              "O_tango": "CHN-143770",
              "O_mango": "CHN-154090",
              False: False
              }

    ENV = MILESTONE[env]
    MILESTONE = MILESTONE[milestone]
    SERVER = SERVER[server]
    TIECKT = TICKET[ticket]

    return (ENV, MILESTONE, SERVER, TIECKT)


def combine_test_information(serial, softVer):
    deviceInfo = deviceMap.get_Device_info(serial)
    # ["SamsungNoteII","GT-N7102","ARMv7 Processor rev 0 (v7l)","1784M","1280*720","Android 4.3"]
    content = "[Test Information]"
    softVersion = "\n1. Software  Version: {}".format(softVer)
    dut = "\n2. Device   CodeName: {}".format(deviceInfo[0])
    brand = "\n3. Device     Module: {}".format(deviceInfo[1])
    cpu = "\n4. Device        CPU: {}".format(deviceInfo[2])
    memory = "\n5. Device     Memory: {}".format(deviceInfo[3])
    res = "\n6. Device Resolution: {}".format(deviceInfo[4])
    sysVer = "\n7. Android   Version: {}".format(deviceInfo[5])

    return content + softVersion + dut + brand + cpu + memory + res + sysVer


def get_logSource(log, logPath=None):
    logSource = {"root": "/data/local/tmp/MTlog/",
                 "notRoot": "/sdcard/MTlog/",
                 "other": "{}".format(logPath)}
    return logSource[log]


def update_description(issue, desc):
    issue.update(description=desc)


def get_count_acts_pre(desc):
    count = 1
    for i in range(len(desc)):
        if "Times for all activities" in desc[i]:
            count = desc[i].split(":")[1]
            return int(count)


def get_count_acts_now(acts):
    count = 0
    for i in range(len(acts)):
        count += acts[i][1]
    return count


def display_percentage(num):
    return "{}%".format(num)


def update_device(desc, device, acts, bugList, NewIssueList, crashTimes, duration, revision):
    # To update the summary for a given release cycle from a Monkey thread
    count_pre = get_count_acts_pre(desc)
    # newLine = []
    for i in range(len(desc)):
        for j in range(len(acts)):
            count_acts_total = get_count_acts_now(acts) + count_pre
            if acts[j][0].split(".")[-1] in desc[i]:
                # print acts[j][0]
                if acts[j][0].split(".")[-1] == desc[i].strip("\r").split(":")[2].split(".")[-1]:
                    desc[i] = desc[i].strip("\r")
                    act_count = desc[i].split(":")[0].strip("*")
                    act_count = int(act_count) + acts[j][1]
                    percent = round(100.0 * act_count / count_acts_total, 3)
                    count_show = "{:*>10}".format(str(act_count))
                    percent_show = "{:*>7}".format(display_percentage(percent))
                    # desc[i] = str(act_count) + ":" + display_percentage(percent) + ":" + acts[j][0]
                    desc[i] = count_show + ":" + percent_show + ":" + acts[j][0]
                    # else:
                    # line = "\n" + "{:*>10}".format(str(acts[j][1])) + ":" + "{:*>7}".format(display_percentage(round(100.0*acts[j][1]/count_acts_total, 3))) + ":" + acts[j][0]
                    # desc[i] = "\n" + desc[i] + newLine
                    # newLine.append(line)

        if "Devices under test" in desc[i]:
            desc[i] = desc[i].strip("\r")
            # deviceList = desc[i].split(":")[1].split(",")
            # print deviceList
            if device not in desc[i]:
                # print device
                desc[i] = "\n" + desc[i] + "{},".format(device)

        elif "Test Duration" in desc[i]:
            desc[i] = desc[i].strip("\r")
            # Test Duration:(0)Hours(0)Minutes
            hs = int(desc[i].split(":")[1].split(")Hours")[0].replace("(", ""))
            ms = int(desc[i].split(":")[1].split(")Minutes")[0].split("Hours(")[1])
            hs += duration[0]
            ms += duration[1]
            if ms > 59:
                hs += 1
                ms -= 60
            desc[i] = "\nTest Duration:({0})Hours({1})Minutes".format(hs, ms)


        elif "Test Revision" in desc[i]:
            if revision not in desc[i]:
                desc[i] = desc[i].strip("\r")
                desc[i] = "\n" + desc[i] + "{},".format(revision)

        elif "Times for all activities" in desc[i]:
            desc[i] = desc[i].strip("\r")
            count = int(desc[i].split(":")[1])
            count += get_count_acts_now(acts)
            desc[i] = "\nTimes for all activities:{}".format(count)

        elif "All Crash or ANR detected:" in desc[i]:
            desc[i] = desc[i].strip("\r")
            issue = ""
            for j in range(len(bugList)):
                if bugList[j] not in desc[i]:
                    issue += "{},".format(bugList[j])
            desc[i] = "\n" + desc[i] + issue

        elif "New Issues Filed:" in desc[i]:
            desc[i] = desc[i].strip("\r")
            issue = ""
            for j in range(len(NewIssueList)):
                if NewIssueList[j] not in desc[i]:
                    issue += "{},".format(NewIssueList[j])
            desc[i] = "\n" + desc[i] + issue

        elif "Crash Times in Total:" in desc[i]:
            desc[i] = desc[i].strip("\r")
            count = int(desc[i].split(":")[1])
            count += crashTimes
            desc[i] = "\nCrash Times in Total:{}".format(count)

        elif "Execution Times:" in desc[i]:
            desc[i] = desc[i].strip("\r")
            count = int(desc[i].split(":")[1])
            count += 1
            desc[i] = "\nExecution Times:{}".format(count)

        else:
            desc[i] = "\n" + desc[i]

    return desc


if __name__ == "__main__":
    print "*** Connecting JIRA ***"
    tango = jira_tango()
    jira = tango.init_jira_connection()
    print "*** Log Handing Module ***"
    logPath = "/sdcard/MTlog/"
    # logPath = "/data/local/tmp/MTlog/"
    print "...... Start to pull the log file from mobile device"
    logFile = pullMonkeyLog.getLatestLogFile(logPath)
    # logFile = "C:\\Users\\shwang\\tango_android_3.20.181848_20151118164159-4d00d6223a3570d5-M-staging2-201511191258.log"
    if os.path.exists(logFile):
        fp = os.path.basename(logFile)

        if "tango" in fp:
            app = "tango"
        else:
            app = "mango"

        (env, milestone, server, issue_data_reporting) = environment_init(get_branch(fp), "N",
                                                                          get_server(fp), "N" + "_" + app)

        print "...... Start to analyze the log file ..."
        crashTrack = parse_mtLog2.get_all_crash_track(logFile)
        anr_Track = parse_mtLog2.get_all_anr_track(logFile)
        if len(anr_Track) > 0:
            crashTrack += anr_Track
        else:
            print "...... No ANR detected. Checking whether crash detected or not..."
        issue_number_total = 0
        new_issue = []
        all_issue = []
        wontFix_issue = []

        if crashTrack:
            print "*** Crash Handling Module ***"
            print "...... Crash detected. Start to fetch the bugs list on Jira ..."
            all_bugInfo = tango.get_allbugs_info()
            print len(all_bugInfo)
            print "...... {} different crash or ANR error detected".format(len(crashTrack))
            zip_log(logFile)

            for i in range(len(crashTrack)):
                print "\n...... Start to deal with the issue: {}/{}".format(i + 1, len(crashTrack))
                time.sleep(3)
                # Get all necessary components for crash handling
                bug_summary = crashTrack[i][0]
                if len(bug_summary) > 192:
                    bug_summary = bug_summary[0:191]
                appCrashLog = crashTrack[i][1]
                times = crashTrack[i][2]
                bugID = tango.has_bug(bug_summary, all_bugInfo)
                print bugID
                if bugID and bugID != "":
                    all_issue.append(bugID)
                    # Deal with those crashes existing in JIRA by its status
                    issue_tango = jira.issue(bugID)
                    bugStatus = tango.get_bug_status(bugID)
                    status = str(bugStatus)
                    if status == "Open" or status == "In Progress":
                        print "Issue {} with {} status detected: {} time{}".format(bugID, status, times, "s" if int(times) > 1 else "")
                        if focus_issues(bugID):
                            print "Focus issue {} found with its log file {}".format(bugID, appCrashLog)
                        bug_update_times(issue_tango, times, app)
                        jira.add_comment(issue_tango, "Comments from autoMonkey: Update summary by adding \
                        {} time{} reproducible at {} {} {} on {}".format(times, "s" if int(times) > 1 else "", env, server,
                                                                         get_revison(logFile), get_device(logFile)))

                    elif status == "Reopened":
                        print "Issue {} with reopen status detected: {} time{}".format(bugID, times, "s" if int(times) > 1 else "")
                        if focus_issues(bugID):
                            print "Focus issue {} found with its log file {}".format(bugID, appCrashLog)
                        bug_update_times(issue_tango, times, app)
                        jira.add_comment(issue_tango, "Comments from autoMonkey: Update summary by adding \
                        {} time{} reproducible at {} {} {} on {}".format(times, "s" if int(times) > 1 else "", env, server,
                                                                         get_revison(logFile), get_device(logFile)))

                    elif status == "Closed":
                        print "Closed issue {} detected. Checking its resolution...".format(bugID)
                        res = str(tango.get_bug_resolution(bugID))
                        if res in ["Cannot Reproduce", "Fixed"]:
                            reopen_bug(jira, bugID, logFile)
                            bug_update_times(issue_tango, times, app)
                            fp = pullCrashLog(appCrashLog)
                            if fp is not None:
                                zip_log(logFile, fp)
                            else:
                                print "no bug report log"
                        else:
                            wontFix_issue.append(bugID)
                            print "issue {} with {} resolution is found. ignore this issue.".format(bugID, res)

                    elif status == "Resolved":
                        res = str(tango.get_bug_resolution(bugID))
                        print "Issue {} with the status Resolved as {} detected: {} time{}".format(bugID, res, times,
                                                                                                   "s" if int(times) > 1 else "")
                        if focus_issues(bugID):
                            print "Focus issue {} found with its log file {}".format(bugID, appCrashLog)
                        else:
                            print appCrashLog

                        bug_update_times(issue_tango, times, app)
                        jira.add_comment(issue_tango, "Comments from autoMonkey: Still reproducible on \
                        {} at {} {} {} for {} time{}".format(get_device(logFile), env, server, get_revison(logFile), times,
                                                             "s" if int(times) > 1 else ""))

                    else:
                        print (bugID, status)

                else:
                    # Deal with those crashes not existing in JIRA
                    print "new issue found. Starting to file it on JIRA..."
                    bug_summary = "[{}ango] [Android-Crash] [{} Time{}] [{}]".format("T" if app == "tango" else "M", times,
                                                                                     "s" if int(times) > 1 else "",
                                                                                     get_device(logFile)) + bug_summary
                    bug_track = track_to_str(crashTrack[i][3])
                    # print bug_track
                    newIssue = create_new_issue(jira, bug_summary, bug_track, logFile, app)
                    # zip all log files
                    fp = pullCrashLog(appCrashLog)
                    zip_log(logFile, fp)
                    print "Package all related log files done as {}".format(appCrashLog)
                    if newIssue:
                        new_issue.append(str(newIssue.key))
                        all_issue.append(str(newIssue.key))
                        # print "-------------------------"
                        # time.sleep(1200)

            # Crash summary for a general overview    
            issue_number = len(crashTrack)
            issue_number_total = get_issue_total(crashTrack)
            new_issue_number = len(new_issue)

            print "Log analysis done. Totally {} crash{} found in this log file".format(issue_number_total,
                                                                                        "es" if issue_number_total > 1 else "")
            print "Remove duplications done. Totally {} different issue{} found.".format(issue_number, "s" if issue_number > 1 else "")
            if new_issue_number >= 1:
                print "{} new issue{} below filed successfully:".format(new_issue_number, "s" if new_issue_number > 1 else "")
                for i in range(new_issue_number):
                    print new_issue[i]
            else:
                print "No new issue filed."
        else:
            print "WOW...No crash detected."

        # if issue_data_reporting:
        if False:
            print "*** Data uploading Module ***"
            print "Start to update test summary report..."

            issue_to_report = jira.issue(issue_data_reporting)
            if str(tango.get_bug_status(issue_data_reporting)) == "Closed":
                jira.transition_issue(issue_to_report, "3", assignee={'name': 'shwang'})
                time.sleep(2)
            actList = parse_mtLog2.get_activities(logFile)
            duration = parse_mtLog2.get_duration(logFile)
            summary_issue = str(issue_to_report.fields.description).split("\n")
            device = get_device(logFile)
            revision = get_revison(logFile)
            desc = update_device(summary_issue, device, actList, all_issue, new_issue, issue_number_total, duration, revision)
            issue_to_report.update(description="".join(desc))
            print "Data uploading done. Monkey analysis done."

        else:
            print "Monkey analysis done without data uploading"

    else:
        print "No such log file. Please check the file path you typed."
