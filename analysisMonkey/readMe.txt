1. Fulfill your Jira account in jira_tango.py
	a. user name
	b. password
	c. the issue search condition in the function get_allbugs if necessary

2. Connect device under test to PC via adb

3. Check the environment environment_init() in runAnalysis.py:
	# (env, milestone, server) = environment_init("K", "K", "staging")
	a. env: the release against which you run monkey testing
	b. milestone: the release on which you want to report the found issues
	c. server: the server of the build on which you run your monkey testing before
	
4. Check the issue for data summary function in runAnalysis.py:
	"""	print "Start to update test summary report..."
        #J: issue_to_report = jira.issue("CHN-11760")
        issue_to_report = jira.issue("CHN-12284")
        summary_issue = str(issue_to_report.fields.description).split("\n")
        desc = update_device(summary_issue, get_device(logFile), actList, all_issue, new_issue, issue_number_total)
        issue_to_report.update(description="".join(desc))
        print "Data uploading done..."
    """
    a. create a template for your monkey testing per a given release; or
    b. comment the code block if you do not need this function
    
5. (Optional) Modify the directory to store the log files pulled from device under test in pullMonkeyLog.py if you want to specify one:
	a. It's the current directory by default  
	b. Change the path if you want to, like LogFilePath_PC = "C:\\Users\shwang\\"    
    
6. Run the script runAnalysis.py. The general process includes:
	a. Initiate JIRA connection;
	b. Fetch related existing issues on Jira;
	c. Find the latest log file in the given directory on device (the default is /sdcard/MTlog/);
	d. Pull the log file from device to PC;
	e. Parse the pulled log file to output two lists: crashList, ANRList;
	f. Remove the duplications and return two new lists for the upcoming issue handling, includes four parameters in each element:
		1. summary: bug summary 
		2. crashLog: the log path if bug reporting function is on. the default is None.
		3. count of this crash
		4. detailed crash track
	g. Crash and ANR handling on Jira
		1. File new issue if not existing
		2. Update bug if existing
	h. Data summary 
		1. J release: CHN-11760 (completed)
		2. K release: CHN-12284 (completed)
		3. L release: CHN-13505 (ongoing)
		
		
        
	
	 