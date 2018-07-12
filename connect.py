#!/usr/bin/env python
import sys, paramiko #to install paramiko do sudo pip install paramiko

#if len(sys.argv) < 3:
#    print ("args missing")
#    sys.exit(1)

def connect(serverIP, username, password, command):

    port = 22
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy)
    client.connect(serverIP, port=port, username=username, password=password)
    stdin, stdout, stderr = client.exec_command(command)
    value = stdout.read()
    client.close()
    return value

def convertToGB (size):
    
    return size/1024/1024/1024

def convertToTB (size):

    return size/1024/1024/1024/1024

def isTB (size):
    if (size < 1000000000000):
        zmienna = False
    else:
        zmienna = True
    return zmienna

def getServerName (serverIP, user, password):
    serverName = connect(serverIP, user, password, 'vim-cmd hostsvc/hostsummary | grep name | grep nomachine')
    serverName = serverName.replace('name = ','')
    serverName = clearFromTrashes(serverName)
    return serverName

def printDatastores(datastores):
    
    print ('{:25}'.format("datastore name") + '{:25}'.format("capacity") + '{:35}'.format("free space"))
    for i in range (0, len(datastores)):
        if (i == 0) or ( (i % 3) == 0):
           print ('{:25}'.format(datastores[i])),
        else: 
            datastoreSize = int(datastores[i])
            if isTB(datastoreSize):
                datastoreSizeStr = str(convertToTB(datastoreSize)) + " TB"
            else:
                dataStoresizeStr = str(convertToGB(datastoreSize)) +" GB"
            if ((i == 2) or (i == 5) or (i == 8 ) or (i ==11)):
                print ('{:25}'.format(str(datastoreSizeStr)))
            else:
                print ('{:25}'.format(str(datastoreSizeStr))),
    return    

def splitDatastores(datastores):

    serverDatastoresList =[]
    for i in range (0, len(datastores)):
        if (i == 0) or ( (i % 3) == 0):
           datastoreName = dataStore[i],
        else: 
            datastoreSize = int(datastore[i])
            if isTB(datasatoreSize):
                datastoreSizeStr = str(convertToTB(datastoreSize)) + " TB"
            else:
                dataStoresizeStr = str(convertToGB(datastoreSize)) +" GB"
            if ((i == 2) or (i == 5) or (i == 8 ) or (i ==11)):
                print ('{:25}'.format(str(datastoreSizeStr)))
            else:
                print ('{:25}'.format(str(datastoreSizeStr))),
    return

def getServerDatastores(serverIP, user, password):
    dataStore = connect(serverIP, user, password, 'vim-cmd hostsvc/datastore/listsummary | grep \"name\|capacity\|freeSpace\"')
    dataStoreName = dataStore.replace(' ','')
    dataStoreName = dataStoreName.replace(',','')
    dataStoreName = dataStoreName.replace('name=','')
    dataStoreName = dataStoreName.replace('capacity=','')
    dataStoreName = dataStoreName.replace('freeSpace=','')
    dataStoreName = dataStoreName.replace('None','')
    dataStoreName = dataStoreName.splitlines()
    printDatastores(dataStoreName)

    return

def getVMPath(serverIP, user, password, id):
   

    vmDataPath = connect(serverIP, user, password, 'vim-cmd vmsvc/get.config ' + id + '|grep vmfs |grep value')

    return vmDataPath

def clearFromTrashes(string):

    string = string.replace('"','')
    string = string.replace(',','')
    string = string.replace(' ','')
    string = string.replace('=','')
    string = string.lstrip()
    string = string.rstrip()
    return string

def clearFromTrashesWithoutSpaces(string):

    string = string.replace('"','')
    string = string.replace(',','')
    string = string.replace('=','')
    string = string.lstrip()
    string = string.rstrip()
    return string

def getVMSize(serverIP, user, password, vmDataPath):
    vmSize = connect(serverIP, user, password, 'du -h "' + vmDataPath + '"' + "|awk \'{print $1}'" )
    return vmSize

def getServerVMs(serverIP, user, password):

    vmList = []
    VMsOnServer = connect(serverIP, user, password, "vim-cmd vmsvc/getallvms | awk \'{print $1}\'")
    listVmId = VMsOnServer.split('\n')
    listVmId.pop(0) #remove first item
    listVmId.pop() #remove last item
    print "\n Virtual Machines on server \n"
    print ('{:30}'.format("VM Name") + '{:10}'.format("Power") + '{:80}'.format("VM path") + '{:10}'.format("VM Size GB"))
    for id in listVmId:
        machineName = connect(serverIP, user, password, "vim-cmd vmsvc/get.summary " + id + "| grep name ")
        powerState = connect(serverIP, user, password, "vim-cmd vmsvc/power.getstate " + id)
        machineDataPath = getVMPath(serverIP, user, password, id)
	machineDataPath = machineDataPath.replace('value','')
        machineDataPath = machineDataPath.rsplit('/',1)[0]
        machineDataPath = machineDataPath + "/"
 	machineDataPath = clearFromTrashesWithoutSpaces(machineDataPath)
        vmSize = getVMSize(serverIP, user, password, machineDataPath)
        machineName = machineName.replace('name = ','')
        machineName = clearFromTrashes(machineName)
        powerState = powerState.replace('Powered ','')      
        powerState = powerState.split("\n",2)[1]
        vmList.append([machineName,powerState,machineDataPath,vmSize]) 
        if "on" in powerState:
            print ('{:30}'.format(machineName) + " " + '\033[92m' '{:10}'.format(powerState) + '\033[0m' " " + '{:80}'.format(machineDataPath) + '{:10}'.format(vmSize))
        else:
            print ('{:30}'.format(machineName) + " " + '\033[91m' '{:11}'.format(powerState) + '\033[0m' " " + '{:80}'.format(machineDataPath) + '{:10}'.format(vmSize))
  #  for i in range(len(vmList)):
#	print(vmList[i])
    return


def openConfigFile():
    fname = "/home/skrypty/vmware.cfg"
    with open(fname) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content

def readConfigFile(config):
    config = str(config)
    config = config.replace("[",'')
    config = config.replace("]",'')
    config = config.replace("'",'')
    config = config.replace(",",'')
    return config

def howManyServers(configFile):
    i = 0
    lines = str(configFile)
    for word in lines.split():
          i = i + 1
    return i/3

content = openConfigFile()
content = readConfigFile(content)
wordIndex = 0
for i in range(0,(howManyServers(content))):
    serverIP = content.split()[wordIndex]
    wordIndex += 1
    user = content.split()[wordIndex]
    wordIndex += 1
    password = content.split()[wordIndex]
    wordIndex += 1
    print ("Server = " + getServerName(serverIP, user, password))
    print (getServerDatastores(serverIP, user, password))
    print (getServerVMs(serverIP, user, password))



