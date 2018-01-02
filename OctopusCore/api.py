# TODO put in a docker container.
import jwt
from flask import Flask, request, g
from flask_pymongo import PyMongo
from flask_cors import CORS

# todo undebug
# OCTO "Constants" to tell microservices who to talk to (and how)
API_VERSION = "v0"
CONTAINER_HANDLER = 'local'

OCTOCORE_DOMAIN = '10.0.75.1'
OCTOCORE_PORT = 5000
OCTOCORE_SERVER_SUBMIT_PATH = '/{}/servers/provision/configure'.format(API_VERSION)
OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH = '/{}/servers/provision/initialise'.format(API_VERSION)

# Connect to mongoDB
app = Flask(__name__)
CORS(app)
app.config['MONGO_DBNAME'] = 'infrarydev'
app.config['MONGO_URI'] = 'mongodb://gentleseal:eQi2ZdxZLhf4bc5xJ@ds241065.mlab.com:41065/infrarydev'
flask_pymongo = PyMongo(app)

AUTHPATH = "/{}/auth".format(API_VERSION)

# noinspection PyPep8
import logic


@app.before_request
def do_auth():
    if request.method not in ["OPTIONS"]:
        if request.path[:len(AUTHPATH)] != AUTHPATH:
            print request.headers
            try:
                supplied_auth_header = request.headers.get("Authorization")
                if not supplied_auth_header:
                    raise ValueError('No authorization token supplied.')
                if "Bearer" in supplied_auth_header:
                    token = supplied_auth_header.split(' ')[1]  # todo: actually do auth (microservice?)
                    try:
                        decoded_token = jwt.decode(token, 'totallysecure', algorithms='HS256')
                    except jwt.InvalidTokenError:
                        raise ValueError('Authentication failed.')
                    else:
                        g.user_id = decoded_token.get('uid')
                        g.token = token
                else:
                    raise ValueError('No auth token supplied.')
            except Exception as e:
                return "401 Unauthorized\n{}\n\n".format(e), 401


@app.route("/{}/auth/register".format(API_VERSION), methods=['POST'])
def register():
    request_dict = request.get_json()

    if not isinstance(request_dict, dict):
        return "400 Bad Request\n{}\n\n".format("Bad request format"), 400

    first_name = request_dict.get("firstName")
    last_name = request_dict.get("lastName")
    email = request_dict.get("email")
    password = request_dict.get("password")

    if first_name and isinstance(first_name, basestring) and last_name and isinstance(last_name, basestring) \
            and email and isinstance(email, basestring) and password and isinstance(password, basestring):
        return logic.User.register(first_name, last_name, email, password)

    else:
        return "400 Bad Request\n{}\n\n".format("Parameters invalid or empty"), 400


@app.route("/{}/auth/verify".format(API_VERSION), methods=['POST'])
def verify():
    request_dict = request.get_json()

    if not isinstance(request_dict, dict):
        return "400 Bad Request\n{}\n\n".format("Bad request format"), 400

    email_key = request_dict.get("emailKey")

    if email_key and isinstance(email_key, basestring):
        return logic.User.verify(email_key)
    else:
        return "400 Bad Request\n{}\n\n".format("Invalid emailKey or emailKey not specified"), 400


@app.route("/{}/auth/login".format(API_VERSION), methods=['POST'])
def login():
    request_dict = request.get_json()

    if not isinstance(request_dict, dict):
        return "400 Bad Request\n{}\n\n".format("Bad request format"), 400

    email = request_dict.get("email")
    password = request_dict.get("password")

    if email and isinstance(email, basestring) and password and isinstance(password, basestring):
        return logic.User.login(email, password)
    else:
        return "400 Bad Request\n{}\n\n".format("Invalid credentials format or credentials not specified"), 400


@app.route("/{}/servers/<string:provider>/<int:server_id>".format(API_VERSION), methods=["GET"])
def get_server(provider=None, server_id=None):
    if server_id and provider:
        return logic.Server.get(provider, server_id, g.user_id)
    else:
        return "No server id or provider specified", 404


@app.route("/{}/servers/<string:provider>/<int:server_id>".format(API_VERSION), methods=["DELETE"])
def delete_server(provider=None, server_id=None):
    if server_id and provider:
        force_delete = False
        try:
            args = request.get_json()
            if args is not None:
                if args['force']:
                    force_delete = True
        except (TypeError, ValueError):
            pass  # forceDelete False by default

        print force_delete  # todo

        return logic.Server.delete(provider, server_id, force_delete, g.user_id, g.token)

    else:
        return "No server id specified", 404


@app.route("/{}/servers".format(API_VERSION))
def list_servers():
    return logic.Servers.list(g.user_id)


@app.route("/{}/servers/provision/create".format(API_VERSION), methods=['POST'])
def create_server():
    request_dict = request.get_json()

    if not isinstance(request_dict, dict):
        return "400 Bad Request\n{}\n\n".format("Bad request format"), 400

    server_properties = request_dict.get("serverProperties")
    vm_configuration = request_dict.get("VMConfiguration")

    # todo more checks here

    if server_properties and isinstance(server_properties, dict) and vm_configuration \
            and isinstance(vm_configuration, dict):
        return logic.Server.create(server_properties, vm_configuration, g.token)
    else:
        return "400 Bad Request\n{}\n\n".format("Parameters invalid or empty"), 400


@app.route("/{}/servers/provision/configure".format(API_VERSION), methods=['POST'])
def configure_server():  # todo Accessible to users ???
    request_dict = request.get_json()
    print request_dict

    if not isinstance(request_dict, dict):
        return "400 Bad Request\n{}\n\n".format("Bad request format"), 400

    temp_key = request_dict.get('__Infrary__TempSSHKey')
    server_hostname = request_dict.get('__Infrary__IP')
    server_provider = request_dict.get('__Infrary__Provider')
    server_id = request_dict.get('__Infrary__ID')
    vm_configuration = request_dict.get("__Infrary__VMConfiguration")

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
        return "400 Bad Request\n{}\n\n".format("Parameters invalid or empty"), 400


@app.route("/{}/servers/provision/initialize".format(API_VERSION), methods=['POST'])
@app.route("/{}/servers/provision/initialise".format(API_VERSION), methods=['POST'])
def initialise_server():
    request_dict = request.get_json()

    if not isinstance(request_dict, dict):
        return "400 Bad Request\n{}\n\n".format("Bad request format"), 400

    server_provider = request_dict.get('__Infrary__Provider')
    server_id = request_dict.get('__Infrary__ID')
    is_master = request_dict.get('__Infrary__IsMaster')  # optional
    do_self_destruct = request_dict.get('__Infrary__SelfDestruct')  # optional
    master_conf = request_dict.get('__Infrary__MasterConf')  # optional

    try:
        if is_master is True:
            is_master = True
            if not isinstance(master_conf['host'], basestring) \
                    or not isinstance(master_conf['user'], basestring) \
                    or not isinstance(master_conf['pass'], basestring) \
                    or not isinstance(master_conf['keySecret'], basestring):
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
        return "400 Bad Request\n{}\n\n".format("Parameters invalid or empty"), 400


@app.route("/".format(API_VERSION))
def index():
    return  # todo: redirect to api docs


if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0')
