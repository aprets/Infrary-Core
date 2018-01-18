# TODO put in a docker container.
from google.appengine.ext import vendor

# Add any libraries installed in the "lib" folder.
vendor.add('lib')

import jwt
from flask import Flask, request, g
from flask_pymongo import PyMongo
from flask_cors import CORS

# import os
# import sys
# ROOT_PATH = os.path.dirname(__file__)
# sys.path.append(os.path.join(ROOT_PATH, '..'))
from constants import *

# Connect to mongoDB
app = Flask(__name__)
CORS(app)
app.config['MONGO_DBNAME'] = DB_NAME
app.config['MONGO_URI'] = DB_URI
flask_pymongo = PyMongo(app)
# noinspection PyPep8
import logic


@app.before_request
def do_auth():
    if request.method not in ["OPTIONS"]:
        if request.path[:len(AUTHPATH)] != AUTHPATH:
            try:
                supplied_auth_header = request.headers.get("Authorization")
                if not supplied_auth_header:
                    raise ValueError('No authorization token supplied.')
                if "Bearer" in supplied_auth_header:
                    token = supplied_auth_header.split(' ')[1]  # todo: actually do auth (microservice?)
                    try:
                        decoded_token = jwt.decode(token, SECRET_TOKEN_ENC_KEY, algorithms='HS256')
                    except jwt.InvalidTokenError:
                        raise ValueError('Authentication failed.')
                    else:
                        g.user_id = decoded_token.get(TOKEN_USER_ID_KEY)
                        g.token = token
                else:
                    raise ValueError('No auth token supplied.')
            except Exception as e:
                return "Unauthorized: {}".format(e), 401


@app.route("/{}/auth/register".format(API_VERSION), methods=['POST'])
def register():
    request_dict = request.get_json()

    if not isinstance(request_dict, dict):
        return "Bad request format", 400

    first_name = request_dict.get(FIRST_NAME_KEY)
    last_name = request_dict.get(LAST_NAME_KEY)
    email = request_dict.get(EMAIL_KEY)
    password = request_dict.get(PASSWORD_KEY)

    if first_name and isinstance(first_name, basestring) and last_name and isinstance(last_name, basestring) \
            and email and isinstance(email, basestring) and password and isinstance(password, basestring):
        return logic.User.register(first_name, last_name, email, password)

    else:
        return "Parameters invalid or empty", 400


@app.route("/{}/auth/verify".format(API_VERSION), methods=['POST'])
def verify():
    request_dict = request.get_json()

    if not isinstance(request_dict, dict):
        return "Bad request format", 400

    email_key = request_dict.get(EMAIL_KEY_KEY)

    if email_key and isinstance(email_key, basestring):
        return logic.User.verify(email_key)
    else:
        return "Invalid emailKey or emailKey not specified", 400


@app.route("/{}/auth/login".format(API_VERSION), methods=['POST'])
def login():
    request_dict = request.get_json()

    if not isinstance(request_dict, dict):
        return "Bad request format", 400

    email = request_dict.get(EMAIL_KEY)
    password = request_dict.get(PASSWORD_KEY)

    if email and isinstance(email, basestring) and password and isinstance(password, basestring):
        return logic.User.login(email, password)
    else:
        return "Invalid credentials format or credentials not specified", 400


@app.route("/{}/servers/<string:server_provider>/<int:server_id>".format(API_VERSION), methods=["GET"])
def get_server(server_provider, server_id):
    return logic.Server.get(server_provider, server_id, g.user_id)


@app.route("/{}/servers/<string:server_provider>/<int:server_id>".format(API_VERSION), methods=["POST"])
def set_server(server_provider, server_id):

    request_dict = request.get_json()

    if not isinstance(request_dict, dict):
        return "Bad request format", 400

    action = request_dict.get(ACTION_KEY)

    if action and isinstance(action, basestring):
        if action == SET_STATUS_ACTION:
            status = request_dict.get(STATUS_KEY)
            if status and isinstance(status, basestring):
                return logic.Server.update_status(server_provider, server_id, g.user_id, status)
        else:
            return "Status invalid or empty", 400

    else:
        return "Action invalid or empty", 400


@app.route("/{}/servers/<string:server_provider>/<int:server_id>".format(API_VERSION), methods=["DELETE"])
def delete_server(server_provider, server_id):
    force_delete = False
    try:
        args = request.get_json()
        if args is not None:
            if args[FORCE_KEY]:
                force_delete = True
    except (TypeError, ValueError, KeyError):
        pass  # forceDelete False by default

    print force_delete  # todo

    return logic.Server.delete(server_provider, server_id, force_delete, g.user_id, g.token)


@app.route("/{}/servers".format(API_VERSION))
def list_servers():
    return logic.Servers.list(g.user_id)


@app.route("/{}/servers/provision/create".format(API_VERSION), methods=['POST'])
def create_server():
    request_dict = request.get_json()

    if not isinstance(request_dict, dict):
        return "Bad request format", 400

    server_properties = request_dict.get(SERVER_PROPERTIES_KEY)
    vm_configuration = request_dict.get(VM_CONFIGURATION_KEY)

    # todo more checks here

    if server_properties and isinstance(server_properties, dict) and vm_configuration \
            and isinstance(vm_configuration, dict):
        return logic.Server.create(server_properties, vm_configuration, g.token)
    else:
        return "Parameters invalid or empty", 400


@app.route("/{}/servers/provision/configure".format(API_VERSION), methods=['POST'])
@app.route("/{}/servers/provision/conf".format(API_VERSION), methods=['POST'])
def configure_server():  # todo Accessible to users ???
    request_dict = request.get_json()
    print request_dict

    if not isinstance(request_dict, dict):
        return "Bad request format", 400

    temp_key = request_dict.get(TEMP_SSH_KEY_EXP_KEY)
    server_hostname = request_dict.get(IP_EXP_KEY)
    server_provider = request_dict.get(PROVIDER_EXP_KEY)
    server_id = request_dict.get(ID_EXP_KEY)
    vm_configuration = request_dict.get(VM_CONFIGURATION_EXP_KEY)

    print type(server_id), type(vm_configuration)

    # todo more checks here too :(

    if temp_key and isinstance(temp_key, basestring) \
            and server_hostname and isinstance(server_hostname, basestring) \
            and server_provider and isinstance(server_provider, basestring) \
            and server_id and isinstance(server_id, (int, long)) \
            and vm_configuration and isinstance(vm_configuration, basestring):

        return logic.Server.configure(request_dict, temp_key, server_hostname, server_provider,
                                      server_id, vm_configuration, g.user_id, g.token)

    else:
        return "Parameters invalid or empty", 400


@app.route("/{}/servers/provision/initialize".format(API_VERSION), methods=['POST'])
@app.route("/{}/servers/provision/initialise".format(API_VERSION), methods=['POST'])
@app.route("/{}/servers/provision/init".format(API_VERSION), methods=['POST'])
def initialise_server():
    request_dict = request.get_json()

    if not isinstance(request_dict, dict):
        return "Bad request format", 400

    server_provider = request_dict.get(PROVIDER_EXP_KEY)
    server_id = request_dict.get(ID_EXP_KEY)
    is_master = request_dict.get(IS_MASTER_EXP_KEY)  # optional
    do_self_destruct = request_dict.get(SELF_DESTRUCT_EXP_KEY)  # optional
    master_conf = request_dict.get(MASTERCONF_EXP_KEY)  # optional

    try:
        if is_master is True:
            is_master = True
            if not isinstance(master_conf[MASTERCONF_HOST_KEY], basestring) \
                    or not isinstance(master_conf[MASTERCONF_USER_KEY], basestring) \
                    or not isinstance(master_conf[MASTERCONF_PASSWORD_KEY], basestring) \
                    or not isinstance(master_conf[MASTERCONF_SECRET_KEY], basestring):
                raise ValueError("something wrong")
        else:
            is_master = False
    except (TypeError, ValueError):
        is_master = False

    # todo more checks here too :((

    if server_provider and isinstance(server_provider, basestring) and server_id and isinstance(server_id, (int, long)):
        return logic.Server.initialise(server_id, server_provider, g.user_id, g.token, is_master, do_self_destruct,
                                       master_conf)
    else:
        return "Parameters invalid or empty", 400


@app.route("/{}/servers/{}/meta".format(API_VERSION, DIGITAL_OCEAN_PROVIDER_CODE), methods=['GET'])
def do_meta():
    request_dict = request.args
    print request_dict

    if not isinstance(request_dict, dict):
        return "Bad request format", 400

    token = request_dict.get(TOKEN_KEY)

    if token and isinstance(token, basestring):
        return logic.Do.get_metadata(token)
    else:
        return "Bad request format", 400




@app.route("/".format(API_VERSION))
def index():
    return  # todo: redirect to api docs


if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0')
