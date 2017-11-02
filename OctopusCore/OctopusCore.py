# TODO put in a docker container.

from flask import Flask, jsonify, url_for, redirect, request , g, abort
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'infrarydev'
app.config['MONGO_URI'] = 'mongodb://gentleseal:eQi2ZdxZLhf4bc5xJ@ds241065.mlab.com:41065/infrarydev'
mongo = PyMongo(app)


APP_URL = "http://127.0.0.1:5000"
API_VERSION = "v0"


@app.before_request
def authorize_token():
    try:
        suppliedAuthHeader = request.headers.get("Authorization")
        if not suppliedAuthHeader:
            raise ValueError('No authorization token supplied.')
        if "Bearer" in suppliedAuthHeader:
            token = suppliedAuthHeader.split(' ')[1]
            if token != 'aTotallySecretToken':  # todo: actually do auth (microservice?)
                raise ValueError('Authorization failed.')
            else:
                g.userId = '59f60945f36d28236307ef2c'
        else:
            raise ValueError('No authorization token supplied.')
    except Exception as e:
        return "401 Unauthorized\n{}\n\n".format(e), 401

class server(Resource):
    def get(self, id=None):
        if id:
            try:
                userInfo = mongo.db.users.find_one({"servers.id": id})
                return jsonify([server for server in userInfo["servers"] if [server["id"] == id]][0])
            except:
                return "Incorrect server id", 404
        else:
            return "No server id specified", 404


class serverList(Resource):
    def get(self):

        userInfo = mongo.db.users.find_one_or_404({'_id': ObjectId(g.userId)})
        print userInfo
        if userInfo:
            return jsonify(userInfo["servers"])
        else:
            return "No servers found", 404

    def put(self): # todo: check everything? (m/b check for __Infrary__Provider and id)
        mongo.db.users.update(
            {'_id': ObjectId(g.userId)},
            {'$push': {'servers': request.get_json()}}
        )
        return self.get()



class index(Resource):
    def get(self):
        return #todo: redirect to api docs


api = Api(app)
api.add_resource(index, "/", endpoint="index")
api.add_resource(serverList, "/{}/servers".format(API_VERSION), endpoint="servers")
api.add_resource(server, "/{}/servers/<int:id>".format(API_VERSION), endpoint="server")

if __name__ == "__main__":
    app.run(debug=True)
