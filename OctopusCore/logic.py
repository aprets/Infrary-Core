import db

from flask import jsonify
import json

from bson.objectid import ObjectId

import jwt
import string
import random

import sendgrid
from sendgrid.helpers.mail import *

import bcrypt
import time, datetime

from api import CONTAINER_HANDLER, OCTOCORE_DOMAIN, OCTOCORE_PORT, OCTOCORE_SERVER_SUBMIT_PATH, OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH

def launchContainer(image,cmd, octoToken=None, env={},detach=False,addOcto=True):
    if CONTAINER_HANDLER == 'local':
        import docker
        docker = docker.DockerClient(base_url='tcp://127.0.0.1:2375')
        if addOcto:
            env['OCTO_TOKEN']=octoToken
            env['OCTOCORE_DOMAIN'] = OCTOCORE_DOMAIN
            env['OCTOCORE_PORT'] = OCTOCORE_PORT
            env['OCTOCORE_SERVER_SUBMIT_PATH'] = OCTOCORE_SERVER_SUBMIT_PATH
            env['OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH'] = OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH
        name = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(25))
        print cmd, env
        out = docker.containers.run(image,cmd,environment=env,auto_remove=False,name=name,network_mode='host',
                                    detach=detach)
        if not detach:
            container = docker.containers.get(name)
            container.remove()
        return out
    else:
        exit(1)

class user():

    @staticmethod
    def register(self, firstName, lastName, email, password):
        userAlreadyExist = db.existsOnceOrNot({'email': email}, dbName="users") or db.existsOnceOrNot({'email': email},
                                                                                                      dbName="tmpUsers")
        if not userAlreadyExist:
            emailKey = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(72))
            sendgridClient = sendgrid.SendGridAPIClient(
                apikey='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'
            )
            fromEmail = Email("noreply@infrary.tk", "Infrary Bot")
            toEmail = Email(email)
            subject = "Verify your email"
            content = Content("text/plain", "Your emalKey => {}".format(emailKey))
            mail = Mail(fromEmail, subject, toEmail, content)
            response = sendgridClient.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
            print(response.headers)
            if response.status_code == 202:

                # Hash 'n salt
                hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
                print hashed

                db.createDocument({
                    "firstName": firstName,
                    "lastName": lastName,
                    "email": email,
                    "hash": hashed,
                    "emailKey": emailKey,
                    "createdAt": datetime.datetime.utcnow(),
                }, dbName="tmpUsers")

                return "201 Created\n{}\n\n".format("Verify the email address to finish account creation"), 201

            else:
                return "400 Bad Request\n{}\n\n".format("Sending email failed"), 400

        else:
            return "400 Bad Request\n{}\n\n".format("User already exists"), 400

    @staticmethod
    def verify(emailKey):
        tmpUser , doesExist = db.findOneIfExists({'emailKey': emailKey}, dbName="tmpUsers")

        if doesExist:

            db.removeDocument({'emailKey': emailKey}, dbName="tmpUsers")

            tmpUser["servers"] = []
            tmpUser["provisioning"] = []
            tmpUser.pop("emailKey")

            db.createDocument(tmpUser, dbName="users")

            return "201 Created\n{}\n\n".format("Account created"), 201
        else:
            return "400 Bad Request\n{}\n\n".format("Invalid emailKey"), 400

    @staticmethod
    def login(email, password):

        user, doesExist = db.findOneIfExists({'email': email}, dbName="users")

        if doesExist:
            if bcrypt.checkpw(password.encode('utf8'), user["hash"].encode('utf8')):
                expTime = int(time.time()) + 60 * 60  # expire in an hour
                payload = {'exp': expTime, 'uid': str(user["_id"])}
                jwtToken = jwt.encode(payload, 'totallysecure', 'HS256')
                return jwtToken
            else:
                return "400 Bad Request\n{}\n\n".format("Invalid credentials"), 400
        else:
            return "400 Bad Request\n{}\n\n".format("Invalid credentials"), 400


class server():

    @staticmethod
    def get(provider, serverID, userID):
        try:
            user, doesExist = db.findOneIfExists({'_id': ObjectId(userID)}, "users")

            if not doesExist:
                return "System error, please contact support", 500

            for server in user["servers"]:
                if server["id"] == serverID and server['__Infrary__Provider'] == provider:
                    return jsonify(server)

            raise ValueError("invalidServerIDorProvider")

        except:
            return "Incorrect server id or provider", 404

    @staticmethod
    def delete(provider, serverID, forceDelete, userID, octoToken):

        user, doesExist = db.findOneIfExists({'_id': ObjectId(userID)}, "users")

        if not doesExist:
            return "System error, please contact support", 500

        else:

            serverList = [server for server in user["servers"]
                          if server["__Infrary__ID"] == serverID and server['__Infrary__Provider'] == provider]

            if forceDelete and len(serverList) == 0:
                serverList = [server for server in user["provisioning"]
                              if server["id"] == serverID and server['__Infrary__Provider'] == provider]

            if len(serverList) == 1:

                server = serverList[0]

                # todo asyncme
                out = launchContainer('provisioner', 'destroy', octoToken , {'SERVER_ID': serverID, 'SERVER_PROVIDER': provider,
                                                                 'ACCESS_TOKEN': server['__Infrary__AccessToken']})
                out = int(out[0:3])
                if out == 204:
                    # delete from servers

                    db.removeFromListParam({"_id": ObjectId(userID)}, "servers", {"__Infrary__ID": serverID, "__Infrary__Provider": provider}, dbName="users")

                    print 'Server destroyed'
                    return 'Server destroyed'

                elif out == 404:
                    return 'No server found', 404

                else:
                    return 'An error has occurred', 404

            elif len(serverList) == 0:
                return "Incorrect server id", 404

            else:
                return "System error, please contact support", 500

    @staticmethod
    def create(serverProperties, VMConfiguration, octoToken):
        serverProperties["VMConfiguration"] = json.dumps(VMConfiguration)
        container = launchContainer('provisioner', 'create', octoToken, serverProperties)
        print container
        return container

    @staticmethod
    def configure(serverDict, tempKey, serverHostname, serverProvider, serverID, VMConfiguration, userID, octoToken):
        serverDict.pop('__Infrary__TempSSHKey')

        db.addToListParam({'_id': ObjectId(userID)}, "provisioning", serverDict, dbName="users")

        # todo should also include domain etc

        octoConf = json.dumps({"serverHostname": serverHostname, "octoToken": octoToken,
                               "serverProvider": serverProvider,
                               "serverID": serverID}).replace('"', '\\"')  ###ITSINTHEVArgs
        print octoConf
        VMConfiguration = VMConfiguration.replace('"', '\\"').replace('\\\\', '\\\\\\')
        print VMConfiguration
        vmconfCmdStr = '"' + tempKey + '" '
        vmconfCmdStr += '"' + octoConf + '" '
        vmconfCmdStr += '"' + VMConfiguration + '"'
        print vmconfCmdStr
        container = launchContainer('vmconf', vmconfCmdStr, octoToken, detach=True)
        return str(container), 200

    @staticmethod
    def initialise(requestDict, serverID, serverProvider, userID, octoToken):

        user, doesExist = db.findOneIfExists({'_id': ObjectId(userID)}, "users")

        if not doesExist:
            return "System error, please contact support", 500

        curServer = None

        for aServer in user["provisioning"]:
            if aServer["__Infrary__ID"] == serverID and aServer['__Infrary__Provider'] == serverProvider:
                curServer = aServer

        if not curServer:
            return "Incorrect server id or provider", 404


        # delete from provisioning
        db.removeFromListParam({"_id": ObjectId(userID)}, "provisioning", {"__Infrary__ID": serverID, "__Infrary__Provider": serverProvider}, dbName="users")

        try:
            if requestDict['__Infrary__IsMaster'] is True:
                curServer['__Infrary__IsMaster'] = True
                curServer['__Infrary__MasterConf'] = requestDict['__Infrary__MasterConf']
            else:
                curServer['__Infrary__IsMaster'] = False
        except:
            curServer['__Infrary__IsMaster'] = False

        # add to servers
        # todo: check everything? (m/b check for __Infrary__Provider and id)
        db.addToListParam({"_id": ObjectId(userID)}, "servers", curServer, dbName="users")

        tmp = server.get(serverProvider, serverID, userID)

        try:
            if requestDict['__Infrary__SelfDestruct']:
                server.delete(serverProvider, serverID, True, userID, octoToken)
        except:
            pass

        return tmp

class servers():

    @staticmethod
    def list(userID):
        user, doesExist = db.findOneIfExists({'_id': ObjectId(g.userId)}, "users")

        if not doesExist:
            return "System error, please contact support", 500

        return jsonify(user["servers"])
