from main import *
import os
import json
import sys
import paramiko
import select
import StringIO

#todo debug
OCTOCORE_DOMAIN = os.environ['OCTOCORE_DOMAIN']
OCTOCORE_PORT = os.environ['OCTOCORE_PORT']
OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH= os.environ['OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH']

for arg in sys.argv:
    print arg

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

    print commandList , octoConf

    counter = 0
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


        finally:
            SSHClient.close()
    # todo
    serverPropertyDict= {}
    serverPropertyDict['__Infrary__Provider'] = octoConf["serverProvider"]
    serverPropertyDict['__Infrary__ID'] = octoConf["serverID"]
    headers = {'Authorization': 'Bearer ' + octoConf['octoToken'], 'Content-Type': 'application/json'}
    HTTPClient = HTTPClient(headers, OCTOCORE_DOMAIN, OCTOCORE_PORT, False)
    HTTPClient.post(OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH, json.dumps(serverPropertyDict))



else:
    print "Not enough args supplied!"
