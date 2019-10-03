# coding=utf-8
"""
Handles direct communication with flask (=> WSGI)
This module mainly takes care of basic input validation
Passes logic handling to logic.py
"""

# Built-in block
import logging
from functools import wraps

# 3rd party block
import jwt
# flask is not in requirements as is bundled with GAE (see requirements_nongae.txt)
from flask import Flask, request, g, abort, jsonify
from flask_cors import CORS

# Parts of OctoCore block
import logic
from constants import *
from jsonvalidator import JSONValidator, AND, OR
from jsonvalidator.fields import *

# Initiate flask WSGI as app
app = Flask(__name__)

if not app.config.get('INIT'):
    app.config['INIT'] = True
    # Allow all CORS origins (default) (for WebUI)
    CORS(app)
    # If chosen DB is mongo, initiate flask extension straight away.
    # (As Flask-PyMongo needs flask app context which logic, DB drivers don't have)
    if DB_TYPE == 'mongodb':
        from flask_pymongo import PyMongo

        app.config['MONGO_DBNAME'] = MONGO_NAME
        app.config['MONGO_URI'] = MONGO_URI
        flask_pymongo = PyMongo(app)
    elif DB_TYPE == 'datastore':
        # If we are in the App Engine Sandbox,
        # Register PyCrypto based SHA512 for PyJWT as the default cryptography based algorithm will not work on GAE
        from jwt.algorithms import get_default_algorithms as get_jwt_args

        if 'RS512' not in get_jwt_args():
            from jwt.contrib.algorithms.pycrypto import RSAAlgorithm

            jwt.register_algorithm('RS512', RSAAlgorithm(RSAAlgorithm.SHA512))


def auth_required(f):
    """
    A wrapper that ensures the user is authenticated. Wraps a flask function.
    :param f: flask function
    :return: function requiring authentication.
    """

    # noinspection PyPep8,PyBroadException
    @wraps(f)
    def do_auth(*args, **kwargs):
        # Allow all OPTIONS requests as they do not interact with the app, but only ensure CORS compliance
        try:
            if request.method not in ['OPTIONS']:
                supplied_auth_header = request.headers.get('Authorization')
                if not supplied_auth_header:
                    return 'No authentication token supplied', 401
                if 'Bearer' in supplied_auth_header:
                    token = supplied_auth_header.split(' ')[1]
                    try:
                        decoded_token = jwt.decode(token, SECRET_TOKEN_DEC_KEY, algorithm='RS512')
                    except jwt.InvalidTokenError:
                        return 'Authentication failed', 401
                    else:
                        g.user_id = decoded_token.get(TOKEN_USER_ID_KEY)
                        g.token = token
                else:
                    return 'Authentication header "Bearer" field format invalid', 401
        except:  # Catch ALL exceptions to ensure user does not go through on error
            return 'Authentication failed', 401
        # noinspection PyArgumentList
        return f(*args, **kwargs)

    return do_auth


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request')
    return 'An internal error occurred', 500


# noinspection PyUnresolvedReferences
@app.route('/{}/auth/register'.format(API_VERSION), methods=['POST'])
def register():
    """
    Registers a user
    Validates registration json and passes processing to logic.py

    Considered valid JSON (key names defined in constants.py):
    {
        FIRST_NAME_KEY: string
        LAST_NAME_KEY: string
        EMAIL_KEY: string - later verified in logic
        PASSWORD_KEY: string - no limits!!!
    }

    :return: A flask-compatible response tuple.
    """

    class UserRegistrationValidator(JSONValidator):
        """
        :param str first_name:
        :param str last_name:
        :param str email:
        :param str password:
        """
        first_name = StringField(name=FIRST_NAME_KEY)
        last_name = StringField(name=LAST_NAME_KEY)
        email = StringField(name=EMAIL_KEY)
        password = StringField(name=PASSWORD_KEY)

    validator = UserRegistrationValidator(request.get_json())
    if validator.validate():
        return logic.User.register(
            validator.first_name,
            validator.last_name,
            validator.email,
            validator.password
        )
    else:
        return jsonify(validator.errors), 400


# noinspection PyUnresolvedReferences
@app.route('/{}/auth/verify'.format(API_VERSION), methods=['POST'])
def verify():
    """
    Verifies user email
    Validates email verification json and passes processing to logic.py

    Considered valid JSON (key names defined in constants.py):
    {
        EMAIL_KEY_KEY: string - later verified in logic
    }

    :return: A flask-compatible response tuple.
    """

    class UserVerificationValidator(JSONValidator):
        """
        :param str email_key:
        """
        email_key = StringField(name=EMAIL_KEY_KEY)

    validator = UserVerificationValidator(request.get_json())
    if validator.validate():
        return logic.User.verify(validator.email_key)
    else:
        return jsonify(validator.errors), 400


# noinspection PyUnresolvedReferences
@app.route('/{}/auth/login'.format(API_VERSION), methods=['POST'])
def login():
    """
    Logs the user in responding with !!!PLAIN!!! JWT
    Validates login json and passes processing to logic.py

    Considered valid JSON (key names defined in constants.py):
    {
        EMAIL_KEY: string
        PASSWORD_KEY: string
    }

    :return: A flask-compatible response tuple.
    """

    class UserLoginValidator(JSONValidator):
        """
        :param str email:
        :param str password:
        """
        email = StringField(name=EMAIL_KEY)
        password = StringField(name=PASSWORD_KEY)

    validator = UserLoginValidator(request.get_json())
    if validator.validate():
        return logic.User.login(validator.email, validator.password)
    else:
        # Here we are only reporting format error, not giving away login/pass being wrong
        return jsonify(validator.errors), 400


@app.route('/{}/user'.format(API_VERSION), methods=['GET'])
@auth_required
def get_user():
    """
    Returns user information (eg. master_conf)
    :return: A flask-compatible response tuple.
    """
    return logic.User.get(g.user_id)


@app.route('/{}/user/messages'.format(API_VERSION), methods=['POST'])
@auth_required
def add_user_message():
    """
    Adds message to user messages

    Body is treated as ***PLAINTEXT*** message!

    :return: A flask-compatible response tuple.
    """
    message = request.get_data()
    if message:
        return logic.User.add_msg(message, g.user_id)
    else:
        return 'Empty message contents', 400


@app.route('/{}/servers/<string:server_provider>/<string:server_id>'.format(API_VERSION), methods=['GET'])
@auth_required
def get_server(server_provider, server_id):
    """
    Responds with JSON server object
    Passes processing to logic.py

    :param server_provider: server provider which holds the server. Typically a 2 Capital code (see constants.py)
    :param server_id: server id specific to provider. Format varies on per-provider basis

    :return: A flask-compatible response tuple.
    """
    return logic.Server.get(server_provider, str(server_id), g.user_id)


# noinspection PyUnresolvedReferences
@app.route('/{}/servers/<string:server_provider>/<string:server_id>'.format(API_VERSION), methods=['POST'])
@auth_required
def set_server(server_provider, server_id):
    """
    Sets server properties
    Validates json and passes processing to logic.py

    Considered valid JSON (key names defined in constants.py):
    {
        ACTION_KEY: string
        if ACTION_KEY:
            STATUS_KEY: string
    }

    :param server_provider: server provider which holds the server. Typically a 2 Capital code (see constants.py)
    :param server_id: server id specific to provider. Format varies on per-provider basis
    :return: A flask-compatible response tuple.
    """

    class ServerSetterActionValidator(JSONValidator):
        """
        :param str action:
        :param str status:
        """
        action = AND(StringField(), InListField([SET_STATUS_ACTION]), name=ACTION_KEY)
        status = StringField(name=STATUS_KEY, optional=True)

    validator = ServerSetterActionValidator(request.get_json())
    if validator.validate():
        if validator.action == SET_STATUS_ACTION:
            if validator.status:
                return logic.Server.update_status(server_provider, str(server_id), g.user_id, validator.status)
            else:
                return '{} is required for this action'.format(STATUS_KEY), 400
        else:  # Should never happen if validator is configured correctly (but it totally will)
            return 'Unsupported action', 400
    else:
        return jsonify(validator.errors), 400


@app.route('/{}/servers/<string:server_provider>/<string:server_id>'.format(API_VERSION), methods=['DELETE'])
@auth_required
def delete_server(server_provider, server_id):
    """
    Deletes a server
    Validates json for FORCE_KEY (optional) and passes processing to logic.py

    Considered valid JSON (key names defined in constants.py):
    {
        FORCE_KEY: bool
    }
    OR
    {}
    OR
    *NOTHING*

    :param server_provider: server provider which holds the server. Typically a 2 Capital code (see constants.py)
    :param server_id: server id specific to provider. Format varies on per-provider basis
    :return: A flask-compatible response tuple.
    """

    class ServerDeletionValidator(JSONValidator):
        """
        :param str force_delete:
        """
        force_delete = AND(StringField(), InListField(['true', 'false']), name=FORCE_KEY)

    # Google App Engine prevents multidicts, but native flask uses them -> do conversion
    if not isinstance(request.args, dict):
        normal_dict_args = {}
        for key in request.args.keys():
            normal_dict_args[key] = request.args[key]
    else:
        normal_dict_args = request.args

    validator = ServerDeletionValidator(normal_dict_args)
    if validator.validate():
        return logic.Server.delete(server_provider, str(server_id), validator.force_delete == 'true', g.user_id,
                                   g.token)
    else:
        # Ignore errors and just default to force_delete=False if no valid json supplied
        return logic.Server.delete(server_provider, str(server_id), False, g.user_id, g.token)


@app.route('/{}/servers'.format(API_VERSION), methods=['GET'])
@auth_required
def list_servers():
    """
    Responds with list of JSON server objects
    Passes processing to logic
    ANY GET is considered valid
    :return: A flask-compatible response tuple.
    """
    return logic.Servers.list(g.user_id)


@app.route('/{}/servers/<string:server_provider>/<string:server_id>/log'.format(API_VERSION), methods=['POST'])
@auth_required
def add_log_server(server_provider, server_id):
    """
    Adds log text to server log

    Body is treated as ***PLAINTEXT*** log!

    :return: A flask-compatible response tuple.
    """
    text = request.get_data()
    if text:
        return logic.Servers.log(server_provider, server_id, g.user_id, text)
    else:
        return 'Empty text contents', 400


# noinspection PyUnresolvedReferences
@app.route('/{}/servers/provision/create'.format(API_VERSION), methods=['POST'])
@auth_required
def create_server():
    """
    Starts the server provisioning process.
    Users are highly encouraged to *ONLY* use this endpoint for provisioning
    Validates json and passes processing to logic.py

    Considered valid JSON (key names defined in constants.py):
    {
        SERVER_PROPERTIES_KEY: dict - No full validation, invalid config will fail on processing
        VM_CONFIGURATION_DB_KEY: dict - No full validation, invalid config will fail on processing
    }

    :return: A flask-compatible response tuple.
    """

    class ServerCreationValidator(JSONValidator):
        """
        :param dict properties:
        :param dict configuration:
        """
        properties = DictField(name=SERVER_PROPERTIES_KEY)
        configuration = DictField(name=VM_CONFIGURATION_KEY)

    validator = ServerCreationValidator(request.get_json())
    if validator.validate():
        return logic.Server.create(validator.properties, validator.configuration, g.user_id,
                                   g.token)
    else:
        return jsonify(validator.errors), 400


# noinspection PyUnresolvedReferences
@app.route('/{}/servers/provision/configure'.format(API_VERSION), methods=['POST'])
@app.route('/{}/servers/provision/conf'.format(API_VERSION), methods=['POST'])
@auth_required
def configure_server():
    # noinspection SpellCheckingInspection
    """
        Moves server to configuration after creation.
        Users are highly *DIS*couraged from using this endpoint
        Validates json and passes processing to logic.py

        Considered valid JSON (key names defined in constants.py):
        *see validator class*

        :return: A flask-compatible response tuple.
        """

    class ServerConfigurationValidator(JSONValidator):
        """
        :param str temp_key:
        :param str provider:
        :param str server_id: We still accept and convert int though
        :param str server_ip:
        :param str access_token:
        :param str ssh_fgpt:
        :param str vm_config:
        :param str log:
        """
        # Not going to db
        temp_key = StringField(name=TEMP_SSH_KEY_KEY)
        log = StringField(name=LOG_KEY, optional=True)

        # Flask args
        provider = StringField(name=PROVIDER_KEY)
        # Temporarily support int for backwards-compatibility
        server_id = OR(StringField(), IntegerField(), name=ID_KEY)

        # Going to DB
        server_ip = StringField(name=IP_KEY)
        access_token = StringField(name=ACCESS_TOKEN_KEY)
        # status set in logic as is hardcoded on create
        ssh_fgpt = StringField(name=SSH_KEY_FINGERPRINT_KEY)
        vm_config = StringField(name=VM_CONFIGURATION_DB_KEY)
        # is_master set later. set to false in logic
        # is_self_destruct set later. set to false in logic
        # metadata set later. set to {} in logic

    validator = ServerConfigurationValidator(request.get_json())
    if validator.validate():
        return logic.Server.configure(
            validator.temp_key,
            validator.provider,
            str(validator.server_id),  # Temporarily support int for backwards-compatibility
            validator.server_ip,
            validator.access_token,
            validator.ssh_fgpt,
            validator.vm_config,
            g.user_id,
            g.token,
            validator.log
        )
    else:
        return jsonify(validator.errors), 400


# noinspection PyUnresolvedReferences
@app.route('/{}/servers/provision/initialize'.format(API_VERSION), methods=['POST'])
@app.route('/{}/servers/provision/initialise'.format(API_VERSION), methods=['POST'])
@app.route('/{}/servers/provision/init'.format(API_VERSION), methods=['POST'])
@auth_required
def initialise_server():
    # noinspection SpellCheckingInspection
    """
        Persists server in internal systems after configuration.
        Users are highly HIGHLY *DIS*couraged from using this endpoint
        Validates json and passes processing to logic.py

        Considered valid JSON (key names defined in constants.py):
        {
            ID_KEY: *string* - Server id as *STRING* (int still allowed for backwards-compatibility)
            PROVIDER_KEY: string - Server provider
            SELF_DESTRUCT_KEY: bool
            IS_MASTER_KEY: bool
            MASTERCONF_KEY: dict - dict describing random rancher config
        }
        :return: A flask-compatible response tuple.
        """

    class ServerInitialisationValidator(JSONValidator):
        """
        :param str provider:
        :param str server_id:
        :param bool is_master:
        :param bool self_destruct:
        :param dict master_conf:
        """
        provider = StringField(name=PROVIDER_KEY)
        # Temporarily support int for backwards-compatibility
        server_id = OR(StringField(), IntegerField(), name=ID_KEY)
        is_master = BooleanField(name=IS_MASTER_KEY, optional=True)
        self_destruct = BooleanField(name=SELF_DESTRUCT_KEY, optional=True)
        master_conf = DictField(name=MASTERCONF_KEY, optional=True)

    class MasterConfValidator(JSONValidator):
        """
        :param str host:
        :param str user:
        :param str password:
        :param str secret:
        """
        host = StringField(name=MASTERCONF_HOST_KEY)
        user = StringField(name=MASTERCONF_USER_KEY)
        password = StringField(name=MASTERCONF_PASSWORD_KEY)
        secret = StringField(name=MASTERCONF_SECRET_KEY)

    validator = ServerInitialisationValidator(request.get_json())
    if validator.validate():
        if validator.is_master:
            master_conf_validator = MasterConfValidator(validator.master_conf)
            if master_conf_validator.validate():
                return logic.Server.initialise(
                    str(validator.server_id),
                    validator.provider,
                    g.user_id,
                    g.token,
                    validator.is_master,
                    validator.self_destruct,
                    validator.master_conf  # Pass the validated DictField (as we ensured inner keys are valid)
                )
            else:
                return jsonify(master_conf_validator.errors), 400
        else:
            return logic.Server.initialise(
                str(validator.server_id),
                validator.provider,
                g.user_id,
                g.token,
                False,
                validator.self_destruct
                # Pass no master_conf
            )
    else:
        return jsonify(validator.errors), 400


# noinspection PyUnresolvedReferences
@app.route('/{}/infrary-compose'.format(API_VERSION), methods=['POST'])
@auth_required
def compose_env():
    """
    Parse and execute infrary-compose.yaml
    Passed in as base64 of file

    Considered valid JSON (key names defined in constants.py):
    {
        INFRARY_COMPOSE_KEY: str (base64) - No full validation, invalid config will fail on processing
    }

    :return: A flask-compatible response tuple.
    """

    class InfraryComposePOSTValidator(JSONValidator):
        """
        :param str infrary_compose_b64:
        """
        infrary_compose_b64 = StringField(name=INFRARY_COMPOSE_KEY)

    validator = InfraryComposePOSTValidator(request.get_json())
    if validator.validate():
        return logic.infrary_compose(validator.infrary_compose_b64, g.user_id, g.token)
    else:
        return jsonify(validator.errors), 400


# noinspection PyUnresolvedReferences
@app.route('/{}/servers/{}/meta'.format(API_VERSION, DIGITAL_OCEAN_PROVIDER_CODE), methods=['GET'])
@auth_required
def do_meta():
    """
    Returns all DO metadata required to launch a server
    Only responds with images supported by default configurations
    Validates 'form data' and passes processing to logic.py
    :return: A flask-compatible response tuple.
    """

    #  This is not json, but our validator only requires dict
    class DOMetadataValidator(JSONValidator):
        """
        :param str token:
        """
        token = StringField(name=TOKEN_KEY)

    # Google App Engine prevents multidicts, bit native flask uses them -> do conversion
    if not isinstance(request.args, dict):
        normal_dict_args = {}
        for key in request.args.keys():
            normal_dict_args[key] = request.args[key]
    else:
        normal_dict_args = request.args
    validator = DOMetadataValidator(normal_dict_args)
    if validator.validate():
        return logic.Do.get_metadata(validator.token, g.user_id)
    else:
        return jsonify(validator.errors), 400


# This endpoint is ONLY for internal use!
# It cleans the temp user list when called by cron
# Currently only in use by GAE (Datastore)
# noinspection SpellCheckingInspection
@app.route('/tmpusercleanup')
def tmp_user_cleanup():
    """
    Initiates TmpUser cleanup for db engines considered incapable or insufficent to do this
    Validates request origin and passes processing to logic.py
    :return: A flask-compatible response tuple.
    """
    if DB_TYPE == 'datastore' and request.headers.get('X-Appengine-Cron'):  # X-Appengine-Cron - special GAE header
        # only present on GAE Cron initiated requests
        return logic.tmp_user_cleanup()
    else:
        logging.info('Someone did a GET on /tmpusercleanup! Suspicios...')
        abort(404)


@app.route('/')
def index():
    """
    Provides a visual indication of API being alive for a user with a browser
    :return: A flask-compatible response tuple.
    """
    return '🛑🚧🚧🚧🛑'


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    app.run(debug=True, threaded=True, host='0.0.0.0', port=8080)
