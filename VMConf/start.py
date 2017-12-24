from main import *
import os
import time
import sys
import paramiko
import select
import string
import random
import json
import StringIO

#todo debug
OCTOCORE_DOMAIN = os.environ['OCTOCORE_DOMAIN']
OCTOCORE_PORT = os.environ['OCTOCORE_PORT']
OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH= os.environ['OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH']

#todo undebug
for arg in sys.argv:
    print arg

def rancherInit():

    # Create API Key for future use

    rancherKeySecret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(50))
    headers = {'Content-Type': 'application/json'}
    anHTTPClient = HTTPClient(headers, octoConf['serverHostname'], 8080, False)
    body = json.dumps({"description":"Do Not Delete Infrary API KEY","name":"Infrary API KEY","publicValue":"InfraryAPIKey","secretValue":rancherKeySecret})
    rancherResponse = anHTTPClient.post('/v2-beta/apiKeys', body)
    if rancherResponse.status != 201:
        return False,rancherResponse.body
    import base64
    authStr = base64.b64encode('InfraryAPIKey:{}'.format(rancherKeySecret))
    headers['Authorization'] = 'Basic {}'.format(authStr)
    # Init a new Client with API key in headers
    anHTTPClient = HTTPClient(headers, octoConf['serverHostname'], 8080, False)

    # Enable auth

    rancherUser = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
    rancherPass = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(50))
    body = json.dumps({"enabled":True,"name":"Infrary User","password":rancherPass,"username":rancherUser})
    rancherResponse = anHTTPClient.post('/v2-beta/localauthconfig', body)
    if rancherResponse.status != 201:
        return False, rancherResponse.body
    else:
        rancherConfDict = {'host': '{}:8080'.format(octoConf['serverHostname']), 'user' : rancherUser, 'pass' : rancherPass, 'keySecret' : rancherKeySecret}
        return True, rancherConfDict

def rancherInstall():

    counter = 1
    isRancherAlive = False
    while not isRancherAlive:
        if counter == 15:
            return False,'Rancher not responding'
        print 'Attempting to connect to Rancher (Attempt {})'.format(str(counter))
        counter += 1
        try:
            headers = {'Content-Type': 'application/json'}
            anHTTPClient = HTTPClient(headers, octoConf['serverHostname'], 8080, False)
            rancherResponse = anHTTPClient.get('/')
            if rancherResponse.status == 200:
                isRancherAlive = True
                print "Rancher is up!"
        except Exception as e:
            print e, e.message, e.args
            time.sleep(10)

    return rancherInit()


if len(sys.argv) == 4 and '' not in [sys.argv[1],sys.argv[2],sys.argv[3]]:

    keyStr = sys.argv[1].replace('\\n','\n')

    print keyStr

    SSHKey = paramiko.RSAKey.from_private_key(StringIO.StringIO(keyStr))

    try:
        octoConf = json.loads(sys.argv[2])
    except Exception as e:
        #todo undebug
        print "An error has occurred parsing the octoConf"
        print e
        exit(1)

    try:
        print sys.argv[3]
        VMConfiguration = json.loads(sys.argv[3])
        print VMConfiguration
        commandList = VMConfiguration["cmdList"]
    except Exception as e:
        #todo undebug
        print "An error has occurred parsing the command list"
        print e
        exit(1)

    print commandList , octoConf , VMConfiguration

    isMaster = False
    try:
        if VMConfiguration['isMaster'] is True:
            isMaster = True
    except:
        pass


    try:
        if VMConfiguration['selfDestruct'] is True:
            selfDestruct = True
        else:
            selfDestruct = False
    except:
        selfDestruct = False

    counter = 1
    connected = False
    while not connected:
        print "Attempting to connect... (Attempt {})".format(str(counter))
        counter += 1

        if counter >= 5:
            connected = True

        try:

            SSHClient = paramiko.SSHClient()
            SSHClient.set_missing_host_key_policy(paramiko.WarningPolicy)
            SSHClient.connect(octoConf['serverHostname'],22,'root',pkey=SSHKey)
            connected = True
            for command in commandList:

                stdin, stdout, stderr = SSHClient.exec_command(command)

                # Wait for the command to terminate
                while not stdout.channel.exit_status_ready():
                    # Only print data if there is data to read in the channel
                    if stdout.channel.recv_ready():
                        rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                        if len(rl) > 0:
                            # Print data from stdout
                            print stdout.channel.recv(1024),
                    if stderr.channel.recv_ready():
                        rl, wl, xl = select.select([stderr.channel], [], [], 0.0)
                        if len(rl) > 0:
                            # Print data from stderr
                            print stderr.channel.recv(1024),

        except Exception as e:
            print e,e.message,e.args
            selfDestruct = True


        finally:
            SSHClient.close()

    try:

        if isMaster:
            result,data = rancherInstall()
            if result is True:
                masterConf = data
            else:
                selfDestruct = True
                #todo report to octocore
                print "Error configuring Rancher server"
        else:
            pass
            # todo make slave

    except Exception as e:
        print e, e.message, e.args
        selfDestruct = True

    submitDict= {}

    submitDict['__Infrary__SelfDestruct'] = selfDestruct
    submitDict['__Infrary__IsMaster'] = isMaster
    if isMaster:
        submitDict['__Infrary__MasterConf'] = masterConf
    submitDict['__Infrary__Provider'] = octoConf["serverProvider"]
    submitDict['__Infrary__ID'] = octoConf["serverID"]
    headers = {'Authorization': 'Bearer ' + octoConf['octoToken'], 'Content-Type': 'application/json'}
    anHTTPClient = HTTPClient(headers, OCTOCORE_DOMAIN, OCTOCORE_PORT, False)
    anHTTPClient.post(OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH, json.dumps(submitDict))



else:
    print "Not enough args supplied!"
