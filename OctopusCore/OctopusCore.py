# TODO put in a docker container.

from flask import Flask, jsonify, url_for, redirect, request , g, abort, json
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from bson.objectid import ObjectId

import jwt
import string
import random
import bcrypt
import time, datetime

import sendgrid
from sendgrid.helpers.mail import *

# todo undebug
# OCTO "Constants" to tell microservices who to talk to (and how)
API_VERSION = "v0"
CONTAINER_HANDLER = 'local'

OCTOCORE_DOMAIN = '10.0.75.1'
OCTOCORE_PORT = 5000
OCTOCORE_SERVER_SUBMIT_PATH= '/{}/servers/provision/configure'.format(API_VERSION)
OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH= '/{}/servers/provision/initialise'.format(API_VERSION)

# Connect to mongoDB
app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'infrarydev'
app.config['MONGO_URI'] = 'mongodb://gentleseal:eQi2ZdxZLhf4bc5xJ@ds241065.mlab.com:41065/infrarydev'
mongo = PyMongo(app)


def launchContainer(image,cmd,env={},detach=False,addOcto=True):
    if CONTAINER_HANDLER == 'local':
        import docker
        docker = docker.DockerClient(base_url='tcp://127.0.0.1:2375')
        if addOcto:
            env['OCTO_TOKEN']=g.token
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


AUTHPATH = "/{}/auth".format(API_VERSION)


@app.before_request
def authorizeToken():
    if request.path[:len(AUTHPATH)] != AUTHPATH:
        try:
            suppliedAuthHeader = request.headers.get("Authorization")
            if not suppliedAuthHeader:
                raise ValueError('No authorization token supplied.')
            if "Bearer" in suppliedAuthHeader:
                token = suppliedAuthHeader.split(' ')[1] # todo: actually do auth (microservice?)
                try:
                    decodedToken = jwt.decode(token, 'totallysecure', algorithms='HS256')
                except:
                    raise ValueError('Authentication failed.')
                else:
                    g.userId = decodedToken.get('uid')
                    g.token = token
            else:
                raise ValueError('No auth token supplied.')
        except Exception as e:
            return "401 Unauthorized\n{}\n\n".format(e), 401


@app.route("/{}/auth/register".format(API_VERSION),methods=['POST'])
def register():
    requestDict = request.get_json()

    firstName = requestDict.get("firstName")
    lastName = requestDict.get("lastName")
    email = requestDict.get("email")
    password = requestDict.get("password")

    if firstName and isinstance(firstName, basestring) and lastName and isinstance(lastName, basestring)\
            and email and isinstance(email, basestring) and password and isinstance(password, basestring):

        userAlreadyExist = mongo.db.users.find({'email': email}, limit=1).count() > 0 or\
                           mongo.db.tmpUsers.find({'email': email}, limit=1).count() > 0
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

                mongo.db.tmpUsers.insert_one({
                    "firstName": firstName,
                    "lastName": lastName,
                    "email": email,
                    "hash": hashed,
                    "emailKey": emailKey,
                    "createdAt": datetime.datetime.utcnow(),
                })
                return "201 Created\n{}\n\n".format("Verify the email address to finish account creation"), 201

            else:
                return "400 Bad Request\n{}\n\n".format("Sending email failed"), 400

        else:
            return "400 Bad Request\n{}\n\n".format("User already exists"), 400


    else:
        return "400 Bad Request\n{}\n\n".format("Parameters invalid or empty"), 400



@app.route("/{}/auth/verify".format(API_VERSION),methods=['POST'])
def verify():
    requestDict = request.get_json()

    emailKey = requestDict.get("emailKey")

    if emailKey and isinstance(emailKey, basestring) :
        userInfo = mongo.db.tmpUsers.find({'emailKey': emailKey}, limit=1)

        if userInfo.count() == 1:
            tmpUser = userInfo[0]

            # delete from temp
            mongo.db.tmpUsers.remove(
                {'emailKey': emailKey}
            )

            # add to users
            mongo.db.users.insert_one({
                "firstName": tmpUser['firstName'],
                "lastName": tmpUser['lastName'],
                "email": tmpUser['email'],
                "hash": tmpUser['hash'],
                "createdAt": tmpUser['createdAt'],
                "servers": [],
                "provisioning": []
            })

            return "201 Created\n{}\n\n".format("Account created"), 201
        else:
            return "400 Bad Request\n{}\n\n".format("Invalid emailKey"), 400
    else:
        return "400 Bad Request\n{}\n\n".format("Invalid emailKey or emailKey not specified"), 400



@app.route("/{}/auth/login".format(API_VERSION),methods=['POST'])
def login():
    requestDict = request.get_json()

    email = requestDict.get("email")
    password = requestDict.get("password")

    if email and isinstance(email, basestring) and password and isinstance(password, basestring):
        userInfo = mongo.db.users.find({'email': email}, limit=1)
        if userInfo.count() == 1 :
            user = userInfo[0]
            if bcrypt.checkpw(password.encode('utf8'), user["hash"].encode('utf8')):
                expTime = int(time.time()) + 60 * 60  # expire in an hour
                payload = {'exp': expTime, 'uid': str(user["_id"])}
                jwtToken = jwt.encode(payload, 'totallysecure', 'HS256')
                return jwtToken
            else:
                return "400 Bad Request\n{}\n\n".format("Invalid credentials"), 400
        else:
            return "400 Bad Request\n{}\n\n".format("Invalid credentials"), 400
    else:
        return "400 Bad Request\n{}\n\n".format("Invalid credentials format or credentials not specified"), 400


class server(Resource):
    def get(self, provider=None, id=None):
        if id and provider:
            try:
                userInfo = mongo.db.users.find_one({'_id': ObjectId(g.userId)})
                return jsonify([server for server in userInfo["servers"] if server["id"] == id and server['__Infrary__Provider'] == provider][0])
            except:
                return "Incorrect server id or provider", 404
        else:
            return "No server id or provider specified", 404

    def delete(self, provider=None, id=None):
        if id and provider:
            forceDelete = False
            try:
                args = request.get_json()
                if args is not None:
                    if args['force'] == True:
                        forceDelete = True
            except:
                pass # forceDelete False by default
            print forceDelete
            userInfo = mongo.db.users.find_one({'_id': ObjectId(g.userId)})
            if userInfo == None:
                return "Incorrect user id", 404
            else:
                serverList = [server for server in userInfo["servers"] if server["id"] == id and server['__Infrary__Provider'] == provider]

                if forceDelete and len(serverList) == 0:
                    serverList = [server for server in userInfo["provisioning"] if server["id"] == id and server['__Infrary__Provider'] == provider]

                if len(serverList) == 1:

                    server = serverList[0]
                    out = launchContainer('provisioner', 'destroy', {'SERVER_ID': id, 'SERVER_PROVIDER': provider, 'ACCESS_TOKEN': server['__Infrary__AccessToken']})
                    out = int(out[0:3])
                    if out == 204:
                        # delete from servers
                        mongo.db.users.update(
                            {"_id": ObjectId(g.userId)},
                            {"$pull": {"servers": {"__Infrary__ID": id, "__Infrary__Provider": provider}}}
                        )
                        print 'Server destroyed'
                        return 'Server destroyed'

                    elif out == 404:
                        return 'No server found', 404

                    else:
                        return 'An error has occurred', 404
                else:
                    return "Incorrect server id", 404

        else:
            return "No server id specified", 404


@app.route("/{}/servers".format(API_VERSION))
def listServers():

    userInfo = mongo.db.users.find_one_or_404({'_id': ObjectId(g.userId)})
    print userInfo
    if userInfo:
        return jsonify(userInfo["servers"])
    else:
        return "No servers found", 404


@app.route("/{}/servers/provision/create".format(API_VERSION),methods=['POST'])
def createServer():
    args = request.get_json()
    envVars = args["serverProperties"]
    VMConfiguration = args["VMConfiguration"]
    envVars["VMConfiguration"]=json.dumps(VMConfiguration)
    container = launchContainer('provisioner','create',envVars)
    print container
    return container


@app.route("/{}/servers/provision/configure".format(API_VERSION),methods=['POST'])
def configureServer(): #todo Accessable to users ???
    requestDict = request.get_json()
    tempKey = requestDict['__Infrary__TempSSHKey']
    requestDict.pop('__Infrary__TempSSHKey')
    mongo.db.users.update(
        {'_id': ObjectId(g.userId)},
        {'$push': {'provisioning': requestDict}}
    )
    #todo should also include domain etc

    octoConf = json.dumps({"serverHostname": requestDict['__Infrary__IP'], "octoToken" : g.token, "serverProvider" : requestDict['__Infrary__Provider'], "serverID" : requestDict['__Infrary__ID']}).replace('"','\\"') ###ITSINTHEVArgs
    print octoConf
    VMConfiguration = requestDict["__Infrary__VMConfiguration"].replace('"','\\"').replace('\\\\','\\\\\\')
    print VMConfiguration
    vmconfCmdStr= '"'+tempKey+'" '
    vmconfCmdStr += '"'+octoConf+'" '
    vmconfCmdStr += '"'+VMConfiguration+'"'
    print vmconfCmdStr
    launchContainer('vmconf', vmconfCmdStr, detach = True)
    return '',200


@app.route("/{}/servers/provision/initialize".format(API_VERSION),methods=['POST'])
@app.route("/{}/servers/provision/initialise".format(API_VERSION),methods=['POST'])
def initialiseServer():
    requestDict = request.get_json()

    print requestDict

    id = requestDict['__Infrary__ID']
    provider = requestDict['__Infrary__Provider']

    if id and provider:
        try:
            userInfo = mongo.db.users.find_one({'_id': ObjectId(g.userId)})
            curServer = [curServer for curServer in userInfo["provisioning"] if curServer["id"] == id and curServer['__Infrary__Provider'] == provider][0]
        except:
            return "Incorrect server id or provider", 404
    else:
        return "No server id or provider specified", 404

    # delete from provisioning
    mongo.db.users.update(
        {"_id": ObjectId(g.userId)},
        {"$pull": {"provisioning": {"__Infrary__ID": id, "__Infrary__Provider": provider}}}
    )

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
    mongo.db.users.update(
        {'_id': ObjectId(g.userId)},
        {'$push': {'servers': curServer}}
    )

    tmp = server().get(provider, id)

    try:
        if requestDict['__Infrary__SelfDestruct'] == True:
            server().delete(provider, id)
    except:
        pass

    return tmp


class index(Resource):
    def get(self):
        return #todo: redirect to api docs


api = Api(app)
api.add_resource(index, "/", endpoint="index")
api.add_resource(server, "/{}/servers/<string:provider>/<int:id>".format(API_VERSION), endpoint="server")

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0')
