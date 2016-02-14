'''
@author: shwang
'''

import os
import settings
import shutil
import adbdevice

def getDownloadURL(app, root_url, branch, server):
    filePath = False
    branchFleList = []
    url = root_url + branch + "{}{}-android{}".format(os.sep, app, os.sep)
    fileList = os.listdir(url)
    for i in range(len(fileList)):
        if server in fileList[i]:
            branchFleList.append(fileList[i])
            
    latestFile = sorted(branchFleList, reverse=True)[0]
    print "The latest file is {}".format(latestFile)
    if latestFile:
        filePath = url + latestFile
 
    return filePath

def copyFile(filePath, localPath):
    fileName = filePath.rsplit(os.sep, 1)[1]
    shutil.copy(filePath, localPath + fileName)
    if os.path.getsize(localPath + fileName) == os.path.getsize(filePath):
        print "Download {} successfully.".format(fileName)
        return localPath + fileName
    else:
        return False

def isDownloaded(downloadURL, localPath):
    fileName = downloadURL.rsplit(os.sep, 1)[1]
    if os.path.exists(localPath + fileName):
        if os.path.getsize(localPath + fileName) != os.path.getsize(downloadURL):
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
            ret = copyFile(downloadURL, localPath)
            if ret:
                res = ret
                break
            else: 
                retry -= 1
        else:
            break
        
    if not res:    
        print "tried downloading from {} for 3 times, but all failed.".format(downloadURL)        
    
    return res


if __name__ == "__main__":
    device = adbdevice.AdbDevice()
    downloadURL = getDownloadURL(settings.urlForDownloading["shareCN_win"], settings.releaseName["N"], settings.serverBuild["staging2"])
    apkFile = isReadyForInstall(downloadURL, settings.localPath["local_win"])
    need_uninstall = False
    if apkFile:
        if need_uninstall:
            device.uninstall_package(apkFile)
        print "Start to install the application..."     
        res = device.install_package(apkFile)
        if res:
            print "Installation done."

