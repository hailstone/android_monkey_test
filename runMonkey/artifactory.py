'''
@author: shwang
'''
import urllib
import os
import time
import re
import adbdevice
import settings

def getURL(app, root_url, branch):
    # For Tango: http://artifactory.tango.corp/tango-release/nebbiolo/tango-android/
    # For Mango: http://artifactory.tango.corp/mango-current/nebbiolo/mango-android/
    newURL = root_url + branch + "/{}-android/".format(app)
    return newURL

def getDownloadURL(app, branch, server):
    root_url = settings.urlForDownloading["artifactory_{}".format(app)]
    url = getURL(app, root_url, branch)
    content = urllib.urlopen(url).read()
    result_list = re.findall("\d\.\d{2}\.\d{6}-\d{14}", content)
    server_android_list = list(set(result_list))
    fileList = sorted(server_android_list, reverse=True)

    for i in range(len(fileList)):
        fullFileName = app + "-android-" + fileList[i] + server
        newURL = url + fileList[i] + "/" + fullFileName
        content = urllib.urlopen(newURL)
        if content.getcode() != 404:
            return newURL
        
    return False
 
def downloadAPP(downloadURL, localPath):
    fileName = downloadURL.rsplit("/", 1)[1]
    
    try:
        begin_time = time.ctime()
        print "Begin to download {} at {}".format(fileName, begin_time)
        # urllib.urlretrieve(download_url, local_dir + os.sep + filename, url_call_back)
        # no need to callback for now
        urllib.urlretrieve(downloadURL, localPath + fileName)
        print "Finish downloading {} at {}".format(fileName, time.ctime())
        
    except:
        print "exception happened"
        return False
        
    finally:
        target_build_size = get_length_from_server(downloadURL)
        if fileName in os.listdir(localPath):
            build_size = os.path.getsize(localPath + fileName)
            print "the build_size is:", build_size
            if build_size < target_build_size:
                if build_size < 5 * 1000:
                    print "build doesn't exist"
                    return False
                else:
                    print "download error, need to download {} again.".format(fileName)
                    os.remove(localPath + fileName) 
                return False
            else:
                print "Download successfully"
                return localPath + fileName     
        

def get_length_from_server(downloadURL):
    page = urllib.urlopen(downloadURL)
    # the Content-Length part is something like: 'Content-Length: 27107189'
    result_list = re.findall("Content-Length: \d+", str(page.headers))
    if len(result_list) != 1:
        print "get the length of %r failed, return 0 as the result" % downloadURL
        return 0
    else:
        length = "".join(result_list).split(":")[1].strip()
        return int(length)
    
def isDownloaded(downloadURL, localPath):
    print downloadURL
    fileName = downloadURL.rsplit("/", 1)[1]
    if os.path.exists(localPath + fileName):
        if os.path.getsize(localPath + fileName) != get_length_from_server(downloadURL):
            print "Download unfinished. Need download again."
            os.remove(localPath + fileName)
            return False
        else:
            print "Already downloaded in the directory {}".format(localPath)
            return localPath + fileName
    else:
        print "Not download yet."
        return False
    
def isReadyForInstall(downloadURL, localPath):
    res = isDownloaded(downloadURL, localPath)
    retry = 3
    while retry > 0:
        if not res:
            ret = downloadAPP(downloadURL, localPath)
            if ret:
                res = ret
                break
            else: 
                retry -= 1
        else:
            break
    if not res:    
        print "tried downloading from {} for 5 times, but all failed.".format(downloadURL)        
    
    return res
    
if __name__ == "__main__":
    device = adbdevice.AdbDevice()
    downloadURL = getDownloadURL("tango", settings.releaseName["N"], settings.newServerBuild["tango_staging2"])
    print downloadURL
    apkFile = isReadyForInstall(downloadURL, settings.localPath["current_dir"])
    need_uninstall = False
    if apkFile:
        if need_uninstall:
            device.uninstall_package(apkFile)
        print "apk file is ready. start to install it now..."    
        device.install_package(apkFile)
    