# TODO put in a docker container.

from flask import Flask, jsonify, url_for, redirect, request , g, abort, json
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from bson.objectid import ObjectId

import jwt
import string
import random

# Connect to mongoDB
app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'infrarydev'
app.config['MONGO_URI'] = 'mongodb://gentleseal:eQi2ZdxZLhf4bc5xJ@ds241065.mlab.com:41065/infrarydev'
mongo = PyMongo(app)

# todo undebug
# OCTO "Constants" to tell microservices who to talk to (and how)
OCTOCORE_DOMAIN = '10.0.75.1'
OCTOCORE_PORT = 5000
OCTOCORE_SERVER_SUBMIT_PATH= '/v0/servers/provision/configure'
OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH= '/v0/servers/provision/initialise'

API_VERSION = "v0"
CONTAINER_HANDLER = 'local'

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
        out = docker.containers.run(image,cmd,environment=env,auto_remove=detach,name=name,network_mode='host', detach=detach)
        if not detach:
            container = docker.containers.get(name)
            container.remove()
        return out
    else:
        exit(1)

@app.before_request
def authorizeToken():
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
            try:
                userInfo = mongo.db.users.find_one({'_id': ObjectId(g.userId)})
                if userInfo == None:
                    return "Incorrect user id", 404
                else:
                    serverList = [server for server in userInfo["servers"] if server["id"] == id and server['__Infrary__Provider'] == provider]

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
            except Exception as e :
                return "An error has occured:" + e.message , 404
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
    cmdList = requestDict["__Infrary__VMConfiguration"].replace('"','\\"')
    print cmdList
    vmconfCmdStr= '"'+tempKey+'" '
    vmconfCmdStr += '"'+octoConf+'" '
    vmconfCmdStr += '"'+cmdList+'"'
    print vmconfCmdStr
    launchContainer('vmconf', vmconfCmdStr, detach = True)
    return '',200

@app.route("/{}/servers/provision/initialize".format(API_VERSION),methods=['POST'])
@app.route("/{}/servers/provision/initialise".format(API_VERSION),methods=['POST'])
def initialiseServer():
    requestDict = request.get_json()
    id = requestDict['__Infrary__ID']
    provider = requestDict['__Infrary__Provider']

    curServer = None

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

    # add to servers
    # todo: check everything? (m/b check for __Infrary__Provider and id)
    mongo.db.users.update(
        {'_id': ObjectId(g.userId)},
        {'$push': {'servers': curServer}}
    )

    tmp = server().get(provider, id)
    server().delete(provider, id)
    return tmp




class index(Resource):
    def get(self):
        return #todo: redirect to api docs


api = Api(app)
api.add_resource(index, "/", endpoint="index")
api.add_resource(server, "/{}/servers/<string:provider>/<int:id>".format(API_VERSION), endpoint="server")

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0')
