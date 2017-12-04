from do import *
from main import *
import os
import json
import sys

# crypto stuff
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


# serverProvider = os.environ['SERVER_PROVIDER']

#todo debug
OCTOCORE_DOMAIN = os.environ['OCTOCORE_DOMAIN']
OCTOCORE_PORT = os.environ['OCTOCORE_PORT']
OCTOCORE_SERVER_SUBMIT_PATH= os.environ['OCTOCORE_SERVER_SUBMIT_PATH']


serverProvider = os.environ['SERVER_PROVIDER']

if sys.argv[1] == 'create':

    tmpKeyObject = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)
    tmpPemKeyEnc = tmpKeyObject.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.TraditionalOpenSSL,encryption_algorithm=serialization.NoEncryption())
    tmpPemKeyStr = tmpPemKeyEnc.decode('utf-8')
    tmpPubOSSKeyEnc = tmpKeyObject.public_key().public_bytes(serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH)
    tmpPubOSSKeyStr = tmpPubOSSKeyEnc.decode('utf-8')

    if serverProvider == "DO":

        accessToken = os.environ['ACCESS_TOKEN']
        serverName = os.environ['SERVER_NAME']
        serverSize = os.environ['SERVER_SIZE']
        serverImage = os.environ['SERVER_IMAGE']
        serverLocation = os.environ['SERVER_LOCATION']
        sshKey = os.environ['SSH_KEY']
        octoToken = os.environ['OCTO_TOKEN']
        print octoToken

        server = doDroplet(accessToken=accessToken, name=serverName, image={'slug':serverImage}, region={'slug':serverLocation}, size={'slug':serverSize}, sshKeys= [tmpPubOSSKeyStr,sshKey])

    # TODO VT SUPPORT DISABLED UNTIL FUTURE VERSIONS
    # elif serverProvider == "VT":
    #     apiKey = os.environ['API_KEY']
    #     DCID = os.environ['DCID']
    #     VPSPLANID = os.environ['VPSPLANID']
    #     OSID = os.environ['OSID']
    #     server = doDroplet(accessToken=accessToken,name=serverName, image={'slug':serverImage},region={'slug':serverLocation},size={'slug':serverSize})
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
            serverPropertyDict['__Infrary__ID'] = server.id
            serverPropertyDict['__Infrary__IP'] = server.networks[u'v4'][0][u'ip_address']
            serverPropertyDict['__Infrary__VMConfiguration'] = os.environ['VMConfiguration']
            serverPropertyDict['__Infrary__SSHKeyFingerprint'] = server.SSHFingerprints[1]
            serverPropertyDict['__Infrary__TempSSHKey'] = tmpPemKeyStr
            serverPropertyDict['__Infrary__AccessToken'] = accessToken
            headers = {'Authorization': 'Bearer ' + octoToken, 'Content-Type': 'application/json'}
            HTTPClient = HTTPClient(headers, OCTOCORE_DOMAIN, OCTOCORE_PORT, False)
            HTTPClient.post(OCTOCORE_SERVER_SUBMIT_PATH, json.dumps(serverPropertyDict))
            print "Great success!"
        except Exception as e:
            print ("Unable to submit data to OctoCore"), e # TODO use production name
            print "Destroying the server..."
            print "Response:\n", server.destroy()
        finally:
            # print json.dumps(server, default=lambda o: o.__dict__)
            # debug
            print "\n\n\n\nDebug stuff:\n"
            print "Server:"
            print server

    else:
        print "There was a critical error provisioning the server!"
        try:
            print "Destroying the server..."
            print "Response:\n", server.destroy()
        except:
            pass

elif sys.argv[1] == 'destroy':

    if serverProvider == "DO":
        accessToken = os.environ['ACCESS_TOKEN']
        serverId = os.environ['SERVER_ID']
        octoToken = os.environ['OCTO_TOKEN']

        server = doDroplet(accessToken=accessToken, id=serverId)
        response = server.destroy()
        print response.status