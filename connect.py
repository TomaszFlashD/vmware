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
    serverName = serverName.replace('\"','')
    serverName = serverName.replace(',','')
    serverName = serverName.replace(' ','')
    return serverName

def printDatastores(dataStore):
    print ('{:25}'.format("datastore name") + '{:25}'.format("capacity") + '{:35}'.format("free space"))
    for i in range (0, len(dataStore)):
        if (i == 0) or ( (i % 3) == 0):
           print ('{:25}'.format(dataStore[i])),
        else: 
            dataStoreSize = int(dataStore[i])
            if isTB(dataStoreSize):
                dataStoreSizeStr = str(convertToTB(dataStoreSize)) + " TB"
            else:
                dataStoreSizeStr = str(convertToGB(dataStoreSize)) +" GB"
            if ((i == 2) or (i == 5) or (i == 8 ) or (i ==11)):
                print ('{:25}'.format(str(dataStoreSizeStr)))
            else:
                print ('{:25}'.format(str(dataStoreSizeStr))),
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

def getServerVMs(serverIP, user, password):
    VMsOnServer = connect(serverIP, user, password, "vim-cmd vmsvc/getallvms | awk \'{print $1}\'")
    listVmId = VMsOnServer.split('\n')
    listVmId.pop(0) #remove first item
    listVmId.pop() #remove last item
    print "\n Virtual Machines on server \n"
    for id in listVmId:
        machineName = connect(serverIP, user, password, "vim-cmd vmsvc/get.summary " + id + "| grep name ")
        powerState = connect(serverIP, user, password, "vim-cmd vmsvc/power.getstate " + id)
        machineDataStore = connect(serverIP, user, password, "vim-cmd vmsvc/get.datastores  " + id + "| grep name ")
        machineDataStore = machineDataStore.replace(' ','')
        machineDataStore = machineDataStore.replace('name','')
        machineDataStore = machineDataStore.lstrip()
        machineDataStore = machineDataStore.rstrip()
        machineName = machineName.lstrip()
        machineName = machineName.rstrip()
       
        powerState = powerState.split("\n",2)[1]
        if "on" in powerState:
            print ('{:40}'.format(machineName) + " is: " + powerState + " datastore :" + machineDataStore)
        else:
            print ('{:40}'.format(machineName) + " is: " + powerState + " datastore :" + machineDataStore)
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



