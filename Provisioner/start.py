from do import *
from main import *
import os
import json

# serverProvider = os.environ['SERVER_PROVIDER']

#debug
serverProvider = 'DO'
OCTOCORE_DOMAIN = '127.0.0.1' # TODO move to Dockerfile/Pass info in differently
OCTOCORE_PORT = 5000
OCTOCORE_SERVER_SUBMIT_PATH= '/v0/servers'
OCTOCORE_TOKEN = 'aTotallySecretToken'

if serverProvider == "DO":
    # accessToken = os.environ['ACCESS_TOKEN']
    # serverName = os.environ['SERVER_NAME']
    # serverSize = os.environ['SERVER_SIZE']
    # serverImage = os.environ['SERVER_IMAGE']
    # serverLocation = os.environ['SERVER_LOCATION']

    #debug
    accessToken = 'a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6'
    serverName = "Infrary"
    serverSize = "512mb"
    serverImage = "ubuntu-14-04-x64"
    serverLocation = "lon1"

    server = doDroplet(accessToken=accessToken,name=serverName, image={'slug':serverImage},region={'slug':serverLocation},size={'slug':serverSize})
elif serverProvider == "VT":
    apiKey = os.environ['API_KEY']
    DCID = os.environ['DCID']
    VPSPLANID = os.environ['VPSPLANID']
    OSID = os.environ['OSID']
    #server = doDroplet(accessToken=accessToken,name=serverName, image={'slug':serverImage},region={'slug':serverLocation},size={'slug':serverSize})
else:
    print ("Unknown server provider!")

print "Starting the provisioning process..."
status,message = server.provision()
if status is True:
    print "Server ID {} provisioned successfully!".format(str(server.id))
    try:
        serverPropertyDict = {}
        for k,v in vars(server).items():
           if k[0] != '_':
               serverPropertyDict[k] = v
        serverPropertyDict['__Infrary__Provider'] = serverProvider
        headers = {'Authorization': 'Bearer ' + OCTOCORE_TOKEN, 'Content-Type': 'application/json'}
        HTTPClient = HTTPClient(headers, OCTOCORE_DOMAIN, OCTOCORE_PORT, False)
        HTTPClient.put(OCTOCORE_SERVER_SUBMIT_PATH, json.dumps(serverPropertyDict))
        print "Great success!"
    except:
        print ("Unable to submit data to OctoCore") # TODO use production name
    finally:
        # print json.dumps(server, default=lambda o: o.__dict__)
        # debug
        print "\n\n\n\nDebug stuff:\n"
        print "Server:"
        print server
        print "Destroying the server..."
        print "Response:\n", server.destroy()


else:
    print "There was a critical error provisioning the server!"