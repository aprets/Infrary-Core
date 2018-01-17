import datetime
import json
import random
import string
import time

import os
import sys
ROOT_PATH = os.path.dirname(__file__)
sys.path.append(os.path.join(ROOT_PATH, '..'))
from constants import *

import requests
import bcrypt
import jwt
import sendgrid
from bson.objectid import ObjectId, InvalidId
from flask import jsonify
from sendgrid.helpers.mail import *

import db_helper as db


def launch_container(image, cmd, octo_token=None, env=None, detach=False, add_octo=True):
    if not IS_DEBUG:
        auto_remove = detach
    else:
        auto_remove = False
    if env is None:
        env = {}
    if CONTAINER_HANDLER == 'local_win':
        import docker
        docker = docker.DockerClient(base_url='tcp://127.0.0.1:2375')
        if add_octo:
            env[OCTO_TOKEN_KEY] = octo_token
            env[OCTO_DOMAIN_KEY] = OCTO_DOMAIN
            env[OCTO_PORT_KEY] = OCTO_PORT
            env[OCTO_SERVER_SUBMIT_PATH_KEY] = OCTO_SERVER_SUBMIT_PATH
            env[OCTO_CONFIGURED_SERVER_SUBMIT_PATH_KEY] = OCTO_CONFIGURED_SERVER_SUBMIT_PATH
        name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(25))
        print 'docker run {} \n{}\n{}'.format(image, cmd, env)
        out = docker.containers.run(image, cmd, environment=env, auto_remove=auto_remove, name=name,
                                    network_mode='host',
                                    detach=detach)
        if not detach:
            container = docker.containers.get(name)
            if not IS_DEBUG:
                container.remove()
        return out
    else:
        exit(1)


# noinspection SpellCheckingInspection
def send_sendgrid_email_key_email(email_key, email):
    # noinspection SpellCheckingInspection
    sendgrid_client = sendgrid.SendGridAPIClient(
        apikey=SENDGRID_API_KEY
    )
    from_email = Email(FROM_EMAIL, FROM_EMAIL_NAME)
    to_email = Email(email)
    subject = USER_CREATION_EMAIL_SUBJECT
    content = Content("text/plain", "emailKey = {}".format(email_key))
    the_email = Mail()
    the_email.from_email = from_email
    the_email.subject = subject
    personalization = Personalization()
    personalization.add_to(to_email)
    the_email.add_personalization(personalization)
    the_email.add_content(content)
    the_email.add_content(Content
                          ("text/html", USER_CREATION_EMAIL_HTML.
                           replace("**key**", email_key).
                           replace("**url**", EMAIL_VERIFY_LINK.format(email_key))))
    return sendgrid_client.client.mail.send.post(request_body=the_email.get())


# noinspection PyClassHasNoInit
class User:
    @staticmethod
    def register(first_name, last_name, email, password):
        user_already_exist = db.check_if_user_exists_email(email, is_temp_user=False) or db.check_if_user_exists_email(
            email, is_temp_user=True)
        if not user_already_exist:
            email_key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(72))
            response = send_sendgrid_email_key_email(email_key, email)
            if response.status_code == 202:

                # Hash 'n salt
                hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

                db.create_user({
                    FIRST_NAME_KEY: first_name,
                    LAST_NAME_KEY: last_name,
                    EMAIL_KEY: email,
                    HASH_KEY: hashed,
                    EMAIL_KEY_KEY: email_key,
                    CREATED_AT_KEY: datetime.datetime.utcnow(),
                }, is_temp_user=True)

                return "Verify the email address to finish account creation. REPEATED USERS ARE NOT CREATED", 201

            else:
                return "Sending email failed", 400  # an attacker could bruteforce users with *WRONG* emails (todo?)

        else:
            return "User already exists!", 404

    @staticmethod
    def verify(email_key):
        try:
            tmp_user, does_exist = db.find_temp_user_email_key(email_key)

            if does_exist:

                db.delete_temp_user_email_key(email_key)

                tmp_user[SERVERS_KEY] = []
                tmp_user.pop(EMAIL_KEY_KEY)

                db.create_user(tmp_user)

                return "Account created", 201
            else:
                return "Invalid emailKey", 400
        except SystemError:
            return "System Error. Please try creating an account again", 500

    @staticmethod
    def login(email, password):

        user, does_exist = db.find_user_email(email)

        if does_exist:
            try:
                does_match = bcrypt.checkpw(password.encode('utf8'), user[HASH_KEY].encode('utf8'))
            except ValueError:
                return "System error, please contact support regarding your account", 500
            if does_match:
                exp_time = int(time.time()) + 60 * 60  # expire in an hour
                payload = {TOKEN_EXPIRY_KEY: exp_time, TOKEN_USER_ID_KEY: str(user[DB_ID_KEY])}
                jwt_token = jwt.encode(payload, SECRET_TOKEN_ENC_KEY, 'HS256')
                return jwt_token, 200
            else:
                return "Invalid credentials", 400
        else:
            return "Invalid credentials", 400


# noinspection PyClassHasNoInit
class Server:

    @staticmethod
    def _check_user_id(user_id):
        try:
            user_object_id = ObjectId(user_id)
        except InvalidId:
            return "Invalid userID format", False
        else:
            return user_object_id, True

    @staticmethod
    def get(provider, server_id, user_id):

        user_object_id, is_id_valid = Server._check_user_id(user_id)
        if not is_id_valid:
            return "Invalid userID format", 400

        user, does_exist = db.find_server_id_provider(user_object_id, server_id, provider)

        if does_exist:
            return jsonify(user[SERVERS_KEY][0]), 200
        else:
            return "Incorrect server id or provider", 404

    @staticmethod
    def delete(provider, server_id, force_delete, user_id, octo_token):

        user_object_id, is_id_valid = Server._check_user_id(user_id)
        if not is_id_valid:
            return "Invalid userID format", 400

        user, does_exist = db.find_user_id(user_object_id)

        if not does_exist:
            return "System error, please contact support", 500

        else:

            server_list = [server for server in user[SERVERS_KEY]
                           if server[ID_EXP_KEY] == server_id and server[PROVIDER_EXP_KEY] == provider]

            if len(server_list) == 0:
                return "Incorrect server id", 404

            elif len(server_list) > 1:
                return "System error, please contact support", 500

            else:

                server = server_list[0]

                if server[STATUS_EXP_KEY] in CANNOT_DELETE_STATUS_LIST and not force_delete:
                    return "Server is processing, forceDelete=True to delete it", 400

                if launch_container(PROVISIONER_CONTAINER_NAME, PROVISIONER_DESTROY_COMMAND, octo_token,
                                    {
                                        PROVISIONER_SERVER_ID_KEY: server_id,
                                        PROVISIONER_PROVIDER_KEY: provider,
                                        PROVISIONER_ACCESS_TOKEN_KEY: server[ACCESS_TOKEN_EXP_KEY]
                                    }, detach=True):
                    return "Server deletion started", 200
                else:
                    return "Failed to start server deletion", 500

    @staticmethod
    def _delete_from_db(provider, server_id, user_object_id):

        if db.delete_server_id_provider(user_object_id, server_id, provider):
            return 'Server deleted', 200
        else:
            return 'System error', 500

    @staticmethod
    def update_status(provider, server_id, user_id, status):
        if status not in ALL_STATUS_LIST:
            return "Invalid status", 400

        user_object_id, is_id_valid = Server._check_user_id(user_id)
        if not is_id_valid:
            return "Invalid userID format", 400

        if status == DELETED_STATUS:
            return Server._delete_from_db(provider, server_id, user_object_id)
        else:
            db.set_server_status_id_provider(user_object_id, server_id, provider, status)
            return "Success", 200

    @staticmethod
    def create(server_properties, vm_configuration, octo_token):
        server_properties[VM_CONFIGURATION_KEY] = json.dumps(vm_configuration)
        if launch_container(PROVISIONER_CONTAINER_NAME, PROVISIONER_CREATE_COMMAND, octo_token,
                            server_properties, detach=True):
            return "Started provisioning process", 200
        else:
            return "System error", 500

    @staticmethod
    def configure(server_dict, temp_key, server_hostname, server_provider, server_id, vm_configuration, user_id,
                  octo_token):

        user_object_id, is_id_valid = Server._check_user_id(user_id)
        if not is_id_valid:
            return "Invalid userID format", 400

        server_dict.pop(TEMP_SSH_KEY_EXP_KEY)
        server_dict[STATUS_EXP_KEY] = CREATED_STATUS

        db.create_server(user_object_id, server_dict)

        octo_conf = json.dumps({VMCONF_SERVER_HOSTNAME_KEY: server_hostname, VMCONF_OCTO_TOKEN_KEY: octo_token,
                                VMCONF_SERVER_PROVIDER_KEY: server_provider,
                                VMCONF_SERVER_ID_KEY: server_id}).replace('"', '\\"')  # todo ITSINTHEVArgs
        vm_configuration = vm_configuration.replace('"', '\\"').replace('\\\\', '\\\\\\')
        container = launch_container(VMCONF_CONTAINER_NAME,
                                     '"{}" "{}" "{}"'.format(temp_key, octo_conf, vm_configuration),
                                     octo_token, detach=True)
        return str(container), 200

    @staticmethod
    def initialise(server_id, server_provider, user_id, octo_token, is_master=None, is_self_destruct=None,
                   master_conf=None):

        user_object_id, is_id_valid = Server._check_user_id(user_id)
        if not is_id_valid:
            return "Invalid userID format", 400

        user, does_exist = db.find_user_id(user_object_id)

        if not does_exist:
            return "System error, please contact support", 500

        cur_server = []

        for a_server in user[SERVERS_KEY]:
            if a_server[ID_EXP_KEY] == server_id and a_server[PROVIDER_EXP_KEY] == server_provider:
                cur_server.append(a_server)

        if len(cur_server) == 0:
            return "Incorrect server id or provider", 404
        elif len(cur_server) > 1:
            return "System error. Please contact support", 500
        else:

            response = "OK", 200

            value_dict = {STATUS_EXP_KEY: UP_STATUS}

            if is_master is True:
                value_dict[IS_MASTER_EXP_KEY] = True
                value_dict[MASTERCONF_EXP_KEY] = master_conf
            else:
                value_dict[IS_MASTER_EXP_KEY] = False

            db_response = db.set_server_values(user_object_id, server_id, server_provider, value_dict)
            if db_response.acknowledged:
                if not db_response.modified_count == 1 or not db_response.matched_count == 1:
                    is_self_destruct = True
                    response = "System error. Please contact support", 500
            else:
                is_self_destruct = True
                response = "DB write error. Please contact support", 500

        server_delete_response = None
        if is_self_destruct:
            server_delete_response = Server.delete(server_provider, server_id, True, user_id, octo_token)

        if not response[1] == 200:
            return response
        elif is_self_destruct and server_delete_response:
            return server_delete_response
        else:
            server, status = Server.get(server_provider, server_id, user_id)
            if status == 200:
                return server, 200
            else:
                return "Unable to verify server init", 500


# noinspection PyClassHasNoInit
class Servers(Server):
    @staticmethod
    def list(user_id):

        user_object_id, is_id_valid = Server._check_user_id(user_id)
        if not is_id_valid:
            return "Invalid userID format", 400

        user, does_exist = db.find_user_id(user_object_id)

        if not does_exist:
            return "System error, please contact support", 500

        return jsonify(user[SERVERS_KEY])


# noinspection PyClassHasNoInit
class Do(object):
    @staticmethod
    def get_metadata(token):
        session = requests.Session()
        session.headers.update({'Authorization': 'Bearer ' + token})

        response = session.get(DO_BASE_URL + "/sizes")
        if response.status_code != 200:
            return "Invalid request, check API key!", 400
        sizes = response.json()["sizes"]

        # response = session.get(DO_BASE_URL + "/images?type=distribution")
        # if response.status_code != 200:
        #     return "Invalid request", 400
        # images = response.json()["images"]
        images = DO_SUPPORTED_IMAGES

        return jsonify({"sizes": sizes, "images": images})

