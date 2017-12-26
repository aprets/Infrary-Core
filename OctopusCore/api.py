# TODO put in a docker container.

from flask import Flask, jsonify, url_for, redirect, request , g, abort, json
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from bson.objectid import ObjectId

import collections
import jwt
import string
import random

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
flask_pymongo = PyMongo(app)

import logic




AUTHPATH = "/{}/auth".format(API_VERSION)


@app.before_request
def doAuth():
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
        return logic.user.register(firstName,lastName,email,password)

    else:
        return "400 Bad Request\n{}\n\n".format("Parameters invalid or empty"), 400



@app.route("/{}/auth/verify".format(API_VERSION),methods=['POST'])
def verify():
    requestDict = request.get_json()

    emailKey = requestDict.get("emailKey")

    if emailKey and isinstance(emailKey, basestring):
        return logic.user.verify(emailKey)
    else:
        return "400 Bad Request\n{}\n\n".format("Invalid emailKey or emailKey not specified"), 400



@app.route("/{}/auth/login".format(API_VERSION),methods=['POST'])
def login():
    requestDict = request.get_json()

    email = requestDict.get("email")
    password = requestDict.get("password")

    if email and isinstance(email, basestring) and password and isinstance(password, basestring):
        return logic.user.login(email, password)
    else:
        return "400 Bad Request\n{}\n\n".format("Invalid credentials format or credentials not specified"), 400


class server(Resource):
    def get(self, provider=None, id=None):
        if id and provider:
            return logic.server.get(provider, id, g.userId)
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
                pass  # forceDelete False by default

            print forceDelete  # todo

            return logic.server.delete(provider, id, forceDelete, g.userId, g.token)

        else:
            return "No server id specified", 404


@app.route("/{}/servers".format(API_VERSION))
def listServers():
    return logic.servers.list(g.userId)


@app.route("/{}/servers/provision/create".format(API_VERSION),methods=['POST'])
def createServer():
    requestDict = request.get_json()

    serverProperties = requestDict.get("serverProperties")
    VMConfiguration = requestDict.get("VMConfiguration")

    # todo more checks here

    if serverProperties and isinstance(serverProperties, dict) and VMConfiguration \
            and isinstance(VMConfiguration, dict):
        return logic.server.create(serverProperties, VMConfiguration, g.token)
    else:
        return "400 Bad Request\n{}\n\n".format("Parameters invalid or empty"), 400


@app.route("/{}/servers/provision/configure".format(API_VERSION),methods=['POST'])
def configureServer(): #todo Accessable to users ???
    requestDict = request.get_json()
    print requestDict
    tempKey = requestDict.get('__Infrary__TempSSHKey')
    serverHostname = requestDict.get('__Infrary__IP')
    serverProvider = requestDict.get('__Infrary__Provider')
    serverID = requestDict.get('__Infrary__ID')
    VMConfiguration = requestDict.get("__Infrary__VMConfiguration")

    print type(serverID),type(VMConfiguration)

    # todo more checks here too :(

    if tempKey and isinstance(tempKey, basestring) \
            and serverHostname and isinstance(serverHostname, basestring) \
            and serverProvider and isinstance(serverProvider, basestring) \
            and serverID and isinstance(serverID, (int, long)) \
            and VMConfiguration and isinstance(VMConfiguration, basestring):

        return logic.server.configure(requestDict, tempKey, serverHostname, serverProvider,
                                      serverID, VMConfiguration, g.userId, g.token)

    else:
        return "400 Bad Request\n{}\n\n".format("Parameters invalid or empty"), 400



@app.route("/{}/servers/provision/initialize".format(API_VERSION),methods=['POST'])
@app.route("/{}/servers/provision/initialise".format(API_VERSION),methods=['POST'])
def initialiseServer():
    requestDict = request.get_json()

    serverProvider = requestDict.get('__Infrary__Provider')
    serverID = requestDict.get('__Infrary__ID')

    # todo more checks here too :((

    if serverProvider and isinstance(serverProvider, basestring) and serverID and isinstance(serverID, (int, long)):
        return logic.server.initialise(requestDict, serverID, serverProvider, g.userId, g.token)
    else:
        return "400 Bad Request\n{}\n\n".format("Parameters invalid or empty"), 400


class index(Resource):
    def get(self):
        return #todo: redirect to api docs


api = Api(app)
api.add_resource(index, "/", endpoint="index")
api.add_resource(server, "/{}/servers/<string:provider>/<int:id>".format(API_VERSION), endpoint="server")

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0')
