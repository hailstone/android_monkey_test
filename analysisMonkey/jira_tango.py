
'''
Created on 2014-11-25

@author: admin
'''
from jira.client import JIRA


class jira_tango():
    
    def __init__(self):
        self.jira = self.init_jira_connection()
    
    def init_jira_connection(self):
        try:
            # Type your user name and password to access Jira here
            jira = JIRA(server="http://jira.tango.corp", basic_auth=("hli", "Sgiggle123"))
            
            """
            httppost.setHeader("X-Atlassian-Token", "nocheck");
            httppost.setHeader("Authorization", "Basic "+auth);
            """
            if jira:
                return jira
        except:
            return False
    
    def get_allbugs(self):
        """Change the account accordingly before try getting related issues"""
        #all_bugs = []
        jira = self.init_jira_connection()
        if jira:
            # Fetch all issues reported by shwang and hli with "Android-Crash" included in summary
            all_bugs_a = jira.search_issues("reporter in (shwang, hli) and summary ~ Android-Crash and created < '2015/12/2' ORDER BY createdDate DESC", maxResults=1000)
            all_bugs_b = jira.search_issues("reporter in (shwang, hli) and summary ~ Android-Crash and created >= '2015/12/2' ORDER BY createdDate DESC", maxResults=1000)
        
            return all_bugs_b + all_bugs_a
        
        
    def appScope(self, bugID):  
        try:
            jira = JIRA(server="http://jira.tango.corp", basic_auth=("shwang", "WINDriver1004"))
            jira.issue(bugID).fields.customfield_11616
            return True
        except:
            return False
        
    def get_allbugs_info(self):
        # return the bug summary and bug id
        all_bugs_info = []
        
        all_bugs = self.get_allbugs()
        for bug in all_bugs:
            bug_summary = bug.fields.summary
            bug_key = bug.key
            all_bugs_info.append((bug_summary,bug_key))
        
        return all_bugs_info
     
    def has_bug(self, bugSummary, bugInfo):
        bugSummary = bugSummary[:len(bugSummary)-1]
        bugInfo = self.get_allbugs_info()       
        for i in range(len(bugInfo)):
            if bugSummary in bugInfo[i][0]:
                return bugInfo[i][1]
            
        return False
        
    def get_bug_status(self, bugID):    
        jira = self.init_jira_connection()
        
        issue = jira.issue(bugID)
        return  issue.fields.status
    
    def get_bug_resolution(self, bugID):
        jira = self.init_jira_connection()
        issue = jira.issue(bugID)
        return issue.fields.resolution
    
    def get_bug_desc(self, bugID):
        jira = self.init_jira_connection()
        
        issue = jira.issue(bugID)
        return  issue.fields.description
    
    def get_last_comments(self, bugID):
        jira = self.init_jira_connection()
        issue = jira.issue(bugID)
        comments = issue.fields.comment.comments
        last_comment = comments[-1]
        print type(last_comment)
        print last_comment

    def close_issue(self):
        all_my_bugs = self.get_allbugs()
        for bug in all_my_bugs:
            if "[Android-Crash]" in bug.fields.summary and self.get_bug_status(bug.key):
                duration = 0
        return duration
    
    def update_device(self, desc, device, acts):
        
        for i in range(len(desc)):
            for j in range(len(acts)):
                if acts[j][0] in desc[i]:
                    desc[i] = desc[i].strip("\r")
                    act_count = desc[i].split(":")[0]
                    act_count = int(act_count) + acts[j][1]
                #count_update = int(act_count) + 1827
                    act_percent = "20%"
                    desc[i] = str(act_count) + ":" + act_percent + ":" + desc[i].split(":")[2]
                
            if "Devices under test" in desc[i]:
                desc[i] = desc[i].strip("\r")
                deviceList = desc[i].split(":")[1].split(",")
                if device not in deviceList:
                    desc[i] = "\n" + desc[i] +"{},".format(device)
                
            else:
                desc[i] = "\n" + desc[i]
                
        return desc
    
if __name__ == "__main__":
    jira = jira_tango()
    print len(jira.get_allbugs())

    
    #issue.update(summary = "[Android-Crash] [2 Times] [SamsungNote2] java.lang.Throwable at /system/lib/libMali.so.0xd3cc(Native Method)", customfield_11616 = {"value":"Messenger (Tango)"})
    #issue.update(fields={'summary': '[Android-Crash] [1 Time] [SamsungNote2] java.lang.Throwable at /system/lib/libMali.so.0xd3cc(Native Method)'})
    #res = jira.get_bug_resolution("CHN-12849")
    #print str(res)
    
