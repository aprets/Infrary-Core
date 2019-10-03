import base64
import datetime
import json
import logging
import random
import string
import time
import jwt
import requests
import sendgrid
from flask import jsonify  # Is not in requirements as is bundled with GAE (see requirements_nongae.txt)
from passlib.hash import pbkdf2_sha512
from sendgrid.helpers.mail import *

from constants import *
from infrary_compose_parser import InfraryComposeParser

if DB_TYPE == 'mongodb':
    import db_driver_mongodb as db
elif DB_TYPE == 'datastore':
    import db_driver_datastore as db
    # noinspection PyUnresolvedReferences
    import requests_toolbelt.adapters.appengine

    # Use the App Engine Requests adapter. This makes sure that Requests uses
    # URLFetch.
    requests_toolbelt.adapters.appengine.monkeypatch()
    # JWT is patched in API
else:
    logging.error('Emm {} is not a supported DB_TYPE ?!?!?!?!?'.format(DB_TYPE))
    sys.exit('INVALID DB TYPE')


def issue_token(user_id, time_valid=3600, is_admin=False):
    """
    Issues and returns a timed JWT with optional admin rights
    :param user_id: User ID or email of the user which TOKEN_USER_ID_KEY is set to
    :param time_valid: Time, in seconds for which the token is valid (1h by default)
    :param is_admin: If True, sets admin key to True. False by default
    :return: Issued JWT
    :rtype: str
    """
    exp_time = int(time.time()) + time_valid
    # Also, yes, time.time() is unix timestamp (UTC). Way to make it clear, python...
    payload = {TOKEN_EXPIRY_KEY: exp_time, TOKEN_USER_ID_KEY: user_id}
    if is_admin:
        payload['admin'] = True
    jwt_token = jwt.encode(payload, SECRET_TOKEN_ENC_KEY, algorithm='RS512')
    logging.info('Gave "{}" a token until {}'.format(user_id, exp_time))
    return jwt_token


def launch_container(image, cmd):
    """
    Send container launch instructions to ContMan adding all the required authentication
     and communication metadata.
    :param str image: Image for ContMan to run (passed directly to docker)
    :param str cmd: Command to pass to the container
    environmental variables are no longer used due to security implications
    :return: response from ContMan
    :rtype: requests.Response
    """
    logging.info('docker run {} \n{}'.format(image, cmd))

    headers = {'Authorization': 'Bearer ' + issue_token('admin', is_admin=True), 'Content-Type': 'application/json'}
    try:
        out = requests.post(CONTMAN_SUBMIT_URL, headers=headers, json={
            'img': image,
            'cmd': cmd,
            'env': {}  # env is no longer used due to security implications
        })
        return out
    except Exception as e:  # Catch all possible ContMan communication errors to error out gracefully.
        logging.error('Failed to talk to ContMan!!!\n' + str(e.message) + str(e.args))
        return False


# noinspection SpellCheckingInspection
def sendgrid_send_email_key_email(email_key, email):
    """
    Send user email verification email using sendgrid python API
     uses template in constants.py
    :param str email_key: Key to include in template (to be posted to /...verify)
    :param str email: User email
    :return: Response from sendgrid API (at time of writing requests.Response)
    :rtype: requests.Response
    """
    # noinspection SpellCheckingInspection
    sendgrid_client = sendgrid.SendGridAPIClient(
        apikey=SENDGRID_API_KEY
    )
    content = Content('text/plain', 'email_key = {}'.format(email_key))
    the_email = Mail()
    the_email.from_email = Email(FROM_EMAIL, FROM_EMAIL_NAME)
    the_email.subject = USER_CREATION_EMAIL_SUBJECT
    personalization = Personalization()  # Apperantly needed for html + text emails
    personalization.add_to(Email(email))  # add 'to email' from params
    the_email.add_personalization(personalization)
    the_email.add_content(content)
    # Build-in python .format or % would not play well with HTML
    the_email.add_content(
        Content(
            'text/html',
            USER_CREATION_EMAIL_HTML
                .replace('**key**', email_key)
                .replace('**url**', EMAIL_VERIFY_LINK.format(email_key))
        )
    )
    logging.info('Emailing the emailkey "{}" to "{}"'.format(email_key, email))
    return sendgrid_client.client.mail.send.post(request_body=the_email.get())


# noinspection PyClassHasNoInit
class User:
    """
    A "Class" containing all the user related logic.
    All methods are static as they are called by flask functions (so true OOP would be pointless).
    """

    @staticmethod
    def register(first_name, last_name, email, password):
        """
        Handle user registration.
        Here all user DB properties have to be explicitly set for readability and DB flexibility.
        :param str first_name: User's first name (Not strictly enforced)
        :param str last_name: User's last name (Not strictly enforced)
        :param str email: User's email address (is used as main user ID)
        :param str password: User's *PLAINTEXT* password
        :return: A flask-compatible response tuple.
        :rtype: tuple
        """
        user = db.User(email=email)
        if not user.exists():
            # Generate random email_key
            email_key = ''.join(
                random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(72))
            # email_key_combo for use in the email
            email_key_combo_b64 = base64.urlsafe_b64encode(email + ';' + email_key)
            response = sendgrid_send_email_key_email(email_key_combo_b64, email)
            if response.status_code == 202:
                user.is_active = False
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.hash = pbkdf2_sha512.hash(password)
                user.email_key = email_key  # Put *ONLY* the email_key into DB
                user.created_at = datetime.datetime.utcnow()
                user.servers = []
                user.master_conf = {}
                user.compose = ''
                user.compose_completed = False
                user.messages = []
                if user.create():
                    logging.info('User "{}" added to temp users'.format(email))
                    return 'Verify the email address to finish account creation', 201
                else:
                    logging.error('FusionDB failed to create user! {}'.format(str(user.data)))
                    return 'Error creating user', 500

            else:
                logging.debug('SendGrid failed to email "{}" => signup failed'.format(email))
                return 'Sending email failed', 400  # an attacker could bruteforce users with *WRONG* emails

        else:
            logging.debug('A repeat signup registered for "{}"'.format(email))
            return 'User already exists!', 400  # Allows email harvesting

    @staticmethod
    def verify(email_key_combo_b64):
        """
        Verify email_key and activate user.
        :param str email_key_combo_b64: combination of user email and email_key separated by ';'
        :return: A flask-compatible response tuple.
        :rtype: tuple
        """
        try:
            email_key_combo = base64.urlsafe_b64decode(email_key_combo_b64.encode('ascii'))
        except (TypeError, UnicodeEncodeError):
            return 'Invalid email_key', 400
        split_email_key = email_key_combo.split(';')  # Split into email and email_key
        if len(split_email_key) != 2:
            return 'Invalid email_key', 400
        email = split_email_key[0]
        email_key = split_email_key[1]
        user = db.User(email=email)
        if user.exists():
            user.pull()
            if user.email_key == email_key:
                user.is_active = True
                if user.push():
                    logging.info('User "{}" activated'.format(email))
                    return 'Account created', 201
                else:
                    logging.error('FusionDB failed to activate user! {}'.format(str(user.data)))
                    return 'Error creating user', 500
            else:
                logging.debug('User "{}" failed emailkey verification'.format(email))
                return 'Invalid email_key', 400
        else:
            logging.info(
                'User "{}" supplied emailkey to a nonexistent user.'.format(email) +
                'Emailkey manipulation or system error possible'
            )
            # Users CAN easily manipulate emailkey to get here! DON'T TELL THEM ANYTHING :)
            return 'Invalid email_key', 400

    @staticmethod
    def login(email, password):
        """
        Verify user credentials and issue a timed JWT.
        :param str email: User's email address aka user_id
        :param str password: User's *PLAINTEXT* password
        :return: A flask-compatible response tuple. *WARNING* response is plaintext JWT *NOT* json.
        :rtype: tuple
        """

        user = db.User(email=email)

        if user.exists():
            user.pull()
            if user.is_active:
                try:
                    does_match = pbkdf2_sha512.verify(password, user.hash)
                except ValueError:
                    # ValueError means hash in DB is unreadable.
                    # On bad password, does_match = False AND NO ValueError occurs!
                    logging.error(
                        'Hash "{}" for "{}" caused passlib to ValueError! (Entered password was "{}")'.format(
                            user.hash,
                            email,
                            password
                        )
                    )
                    return 'System error, please contact support regarding your account', 500
                if does_match:
                    return issue_token(email), 200
                else:
                    logging.debug('Bad password provided for "{}"'.format(email))
                    # Have to return the same message to prevent harvesting & brute-force attacks
                    return 'Invalid credentials', 400
            else:
                logging.debug('Attempt to login as an inactive user "{}"'.format(email))
                # Have to return the same message to prevent harvesting & brute-force attacks
                return 'Invalid credentials', 400
        else:
            logging.debug('Attempt to login as a nonexistent user "{}"'.format(email))
            # Have to return the same message to prevent harvesting & brute-force attacks
            # #irony
            return 'Invalid credentials', 400

    @staticmethod
    def get(email):
        """
        Get basic user details.
        (For WebUI, master_conf fetching)
        :param str email: User's email address aka user_id
        :return: A flask-compatible response tuple.
        :rtype: tuple
        """

        user = db.User(email=email)

        if user.exists():
            user.pull()
            response_dict = user.data
            # Hide internal params
            for key in ['hash', 'email_key']:
                response_dict.pop(key)
            logging.debug('User.get on "{}"'.format(email))
            return jsonify(response_dict)
        else:
            logging.error('Failed to get (pull) "{}" from FusionDB'.format(email))
            return 'System error fetching user data', 500

    @staticmethod
    def add_msg(message, email):
        """
        Add a message to user messages
        aka send user a message
        mostly used for internal interservice communications
        :param str message: Message contents
        :param str email: User's email address aka user_id
        :return: A flask-compatible response tuple.
        :rtype: tuple
        """

        user = db.User(email=email)

        if user.exists():
            user.pull()
            if len(user.messages) >= 25:
                user.messages.pop(0)
            user.messages.append(
                {
                    'time': time.time(),
                    'message': message
                })
            messages = list(user.messages)
            if user.push():
                logging.debug('Added message "{}" for "{}"'.format(message, email))
                return jsonify(messages)
            else:
                logging.error(
                    'Failed to save (push) message "{}" for "{}" to FusionDB. User data:\n{}'.format(message, email,
                                                                                                     user.data))
                return 'System error saving user data', 500
        else:
            logging.error('Failed to find (pull) "{}" from FusionDB'.format(email))
            return 'System error fetching user data', 500


# noinspection PyClassHasNoInit
class Server:
    """
    A "Class" containing all the server (singular only) related logic.
    All methods are static as they are called by flask functions (so true OOP would be pointless).
    """

    @staticmethod
    def get(provider, server_id, owner_email):
        """
        Fetch server data.
        :param str provider: Server provider lettercode
        :param str server_id: Server ID from provider
        :param str owner_email: Owner's email address aka user_id
        :return: A flask-compatible response tuple.
        :rtype: tuple
        """

        server = db.Server(owner_email=owner_email, provider=provider, id=server_id)
        if server.exists():
            server.pull()
            logging.debug('"{}" did a .get on {}{}'.format(owner_email, provider, server_id))
            return jsonify(server.data), 200
        else:
            logging.info('"{}" wanted a nonexistent server {}{}'.format(owner_email, provider, server_id))
            return 'Incorrect server id or provider', 404

    @staticmethod
    def delete(provider, server_id, force_delete, owner_email, octo_token, access_token=None):
        """
        *Initiate* server deletion:
        aka start provisioner with a task to delete the container.
        DOES NOT actually remove server from DB!
        (Provisioner calls back to do that if provider delete successful)
        :param str provider: Server provider lettercode
        :param str server_id: Server ID from provider
        :param bool force_delete: On True, server with any status will be deleted (dangerous). This is false by
        default only allowing configured servers to be deleted.
        :param str owner_email: Owner's email address aka user_id
        :param str octo_token: (User) OctoCore Token to authenticate callbacks.
        :param str access_token: Internally passed token on "emergency" delete.
        :return: A flask-compatible response tuple.
        :rtype: tuple
        """

        server = db.Server(owner_email=owner_email, provider=provider, id=server_id)

        if server.exists():
            server.pull()
            if server.status in CANNOT_DELETE_STATUS_LIST and not force_delete:
                logging.debug(
                    '"{}" wanted to delete {}{} without using the force'.format(owner_email, provider, server_id)
                )
                return 'Server is processing, use the force to delete it, if desired', 400
            if server.is_master:
                # When master is deleted, it DELETES ALL SLAVES with itself
                owner = db.User(email=owner_email)
                owner.pull()
                for owners_server in owner.servers:
                    if not (owners_server[0] == provider and owners_server[1] == server_id):
                        Server.delete(owners_server[0], owners_server[1], force_delete, owner_email, octo_token)

        else:
            logging.debug(
                '"{}" requested deletion of nonexistent server {}{}'.format(owner_email, provider, server_id))
            if force_delete and access_token:
                server.access_token = access_token
            else:
                return 'Incorrect server id or provider', 404

        octo_conf = \
            {
                OCTO_URL_KEY: OCTO_URL,
                OCTO_SERVER_STATUS_SUBMIT_PATH_KEY: OCTO_SERVER_STATUS_SUBMIT_PATH,
                OCTO_MESSAGE_SUBMIT_PATH_KEY: OCTO_MESSAGE_SUBMIT_PATH,
                OCTO_TOKEN_KEY: issue_token(owner_email),
                PROVISIONER_ACTION_KEY: PROVISIONER_DESTROY_ACTION
            }

        server_properties = \
            {
                PROVISIONER_SERVER_ID_KEY: server_id,
                PROVISIONER_PROVIDER_KEY: provider,
                PROVISIONER_ACCESS_TOKEN_KEY: server.access_token
            }

        command = base64.b64encode(
            json.dumps(
                {
                    PROVISIONER_OCTO_CONF_KEY: octo_conf,
                    PROVISIONER_PROPERTIES_KEY: server_properties
                }
            )
        )

        if launch_container(PROVISIONER_CONTAINER_NAME, command):
            logging.info('Starting deletion of {}{} for "{}"'.format(provider, server_id, owner_email))
            return 'Server deletion started', 200
        else:
            logging.error(
                'Failed to schedule deletion of {}{} for "{}". Server info:\n{}'.format(
                    provider,
                    server_id,
                    owner_email,
                    server.data
                )
            )
            return 'System error scheduling server deletion', 500

    @staticmethod
    def log(provider, server_id, owner_email, message):
        server = db.Server(owner_email=owner_email, provider=provider, id=server_id)
        if server.exists():
            server.pull()
            server.log += message
            if server.push():
                logging.debug('"{}" logged on {}{}'.format(owner_email, provider, server_id))
                return message, 200
            else:
                logging.error(
                    'FusionDB failed to push new log "{}" for {}{} (user "{}")'.format(
                        server.log, provider, server_id, owner_email
                    )
                )
        else:
            logging.info('"{}" wanted to log on a nonexistent server {}{}'.format(owner_email, provider, server_id))
            return 'Incorrect server id or provider', 404

    @staticmethod
    def _delete_from_db(provider, server_id, owner_email):
        """
        ***INTERNAL*** method to actually delete server from DB.
        Used in provisioner callback.
        Called from update_status.
        :param str provider: Server provider lettercode
        :param str server_id: Server ID from provider
        :param str owner_email: Owner's email address aka user_id
        :return: A flask-compatible response tuple.
        :rtype: tuple
        """
        server = db.Server(owner_email=owner_email, provider=provider, id=server_id)
        try:
            server.pull()
        except AttributeError:
            logging.debug('Deletion of {}{} from db requested, but its not there'.format(provider,server_id))
            return 'Server does not exist in DB', 404
        if server.is_master:
            # As this is the first instance of more advanced, "fancy" fusiondb use, it is explained here:
            # Since default driver initiator ("constructor") (__init__) maps **kwargs to model properties,
            # we can specify our identifying properties AND the property (or properties) we want to change without
            # ever saving the object instance (owner = db.User...) or pulling it. We just call instance's .pull()
            # and the driver will take care of the rest and doing pulls, pushes etc. behind the scenes
            # if they are required by DB type.
            logging.info('Removing master_conf for "{}"'.format(owner_email))
            # Indicate no master and no servers are present anymore
            db.User(email=owner_email, master_conf={}, servers=[]).push()
        if server.delete():
            logging.info('Called fusion_db.model.delete... on {}{} for "{}"'.format(provider, server_id, owner_email))
            return 'Server deleted if existed', 200
        else:
            logging.debug('.delete failed on {}{} for "{}". Server info:\n{}'.format(
                provider, server_id, owner_email, server.data
            ))
            return 'Deletion failed! Does the server exist?', 400

    @staticmethod
    def update_status(provider, server_id, owner_email, status):
        """
        Update server status (in DB).
        :param str provider: Server provider lettercode
        :param str server_id: Server ID from provider
        :param str owner_email: Owner's email address aka user_id
        :param str status: New server status (from allowed status list) (see ALL_STATUS_LIST)
        :return: A flask-compatible response tuple.
        :rtype: tuple
        """
        if status not in ALL_STATUS_LIST:
            logging.debug(
                '"{}" wants to set an invalid stats "{}" for {}{}'.format(owner_email, status, provider, server_id)
            )
            return 'Invalid status', 400

        # DELETED_STATUS is a special status which WILL ACTUALLY DELETE THE SERVER FROM DB!
        if status == DELETED_STATUS:
            # Server._delete_from_db will log
            return Server._delete_from_db(provider, server_id, owner_email)
        else:
            if db.Server(owner_email=owner_email, provider=provider, id=server_id, status=status).push():
                logging.info('Set status "{}" for {}{} for user "{}"'.format(status, provider, server_id, owner_email))
                return 'Status updated', 200
            else:
                logging.error(
                    'FusionDB failed to push new status "{}" for {}{} (user "{}")'.format(
                        status, provider, server_id, owner_email
                    )
                )
                return 'System error', 500

    # noinspection PyUnusedLocal
    @staticmethod
    def create(server_properties, vm_configuration, owner_email, octo_token, running_compose=False):
        """
        *Initiate* server creation.
        Launches a provisioner container to create the server (async).
        At this stage the server is not formally considered *created* (, but requested)
        :param dict server_properties: All the properties for provider to create the server (and for Infrary to
        register it). Eg. Server name, plan id
        :param dict vm_configuration: Configuration for VMConf to configure the server. Eg. command list, is_master
        :param str owner_email: Owner's email address aka user_id
        :param str octo_token: (User) OctoCore Token to authenticate callbacks (Not in use. Left for future use)
        :param bool running_compose: Indicates if method is executed internally on compose application
        :return: A flask-compatible response tuple.
        :rtype: tuple
        """

        owner = db.User(email=owner_email)
        owner.pull()
        if vm_configuration.get(VMCONF_IS_MASTER_KEY):  # Default to False on problems.
            if owner.master_conf and owner.servers:
                # This is not normal as owner.master_conf suggests we have a master
                if owner.master_conf == {'placeholder': 'placeholder'}:
                    logging.info('Assuming provisioner failure for {} and recreating master'.format(owner.email))
                    User.add_msg('Assuming provisioner failure', owner_email)
                else:
                    # Assume it is user not understanding things
                    logging.debug('"{}" wanted to create another master'.format(owner_email))
                    return 'Multiple masters are not supported!', 400
            # "Normal branch"
            if not running_compose:
                # If we are doing a new master, clear compose conf (if we are not running_compose)
                owner.compose = ''
                owner.compose_completed = False
                owner.push()
            owner.master_conf = {'placeholder': 'placeholder'}  # Make sure no new masters can be created
            # As the check is always if owner.master_conf:...
            owner.push()
        else:
            if not owner.master_conf:
                logging.debug('"{}" wanted to create a slave before a master'.format(owner_email))
                return 'A master must be created before slaves!', 400
        # vm_configuration is embedded in server_properties for provisioner to pass it on
        server_properties[VM_CONFIGURATION_DB_KEY] = json.dumps(vm_configuration)

        octo_conf = \
            {
                OCTO_URL_KEY: OCTO_URL,
                OCTO_SERVER_SUBMIT_PATH_KEY: OCTO_SERVER_SUBMIT_PATH,
                OCTO_SERVER_STATUS_SUBMIT_PATH_KEY: OCTO_SERVER_STATUS_SUBMIT_PATH,
                OCTO_MESSAGE_SUBMIT_PATH_KEY: OCTO_MESSAGE_SUBMIT_PATH,
                OCTO_TOKEN_KEY: issue_token(owner_email),
                PROVISIONER_ACTION_KEY: PROVISIONER_CREATE_ACTION
            }

        # Base64 as docker and transport WILL mess with escapes otherwise
        command = base64.b64encode(
            json.dumps(
                {
                    PROVISIONER_OCTO_CONF_KEY: octo_conf,
                    PROVISIONER_PROPERTIES_KEY: server_properties
                }
            )
        )

        if launch_container(PROVISIONER_CONTAINER_NAME, command):
            User.add_msg(
                'Server provisioning starting for {}@{}'.format(
                    server_properties.get(PROVISIONER_SERVER_NAME_KEY, 'ERROR'),
                    server_properties.get(PROVISIONER_PROVIDER_KEY, 'ERROR')),
                owner_email)
            logging.info('Starting provisioning a server for "{}"'.format(owner_email))
            return 'Started provisioning process', 200
        else:
            logging.error(
                'Could not schedule server provisioning for "{}". User info:\n{}\n'.format(
                    owner_email, owner.data
                ) + 'ServerProps;VMConfiguration:\n{}\n{}'.format(server_properties, vm_configuration))
            owner.master_conf = {}
            owner.push()
            return 'System error scheduling server provisioning', 500

    @staticmethod
    def configure(temp_key, provider, server_id, server_ip, access_token, ssh_fgpt,
                  vm_config, owner_email, octo_token, log=''):
        """
        *Initiate* server configuration.
        Launches a VMConf container to configure the server (async).
        This stage ACTUALLY PERSISTS THE SERVER IN DB.
        :param str temp_key: *TEMPORARY* ssh PRIVATE key (For use by VMConf). DO NOT PERSIST!
        :param str provider: Server provider lettercode
        :param str server_id: Server ID from provider
        :param str server_ip: Server IP *AS STRING*
        :param str access_token: Provider access token.
        :param str ssh_fgpt: Permanent user key ssh fingerprint.
        :param str vm_config: Configuration for VMConf to configure the server. Eg. command list, is_master
        :param str owner_email: Owner's email address aka user_id
        :param str octo_token: (User) OctoCore Token to authenticate callbacks.
        :param str log: Provisioning log
        :return: A flask-compatible response tuple.
        :rtype: tuple
        """

        server = db.Server(owner_email=owner_email, provider=provider, id=server_id)
        # if server.exists(): Is "reconfiguring" servers allowed ? It seems to be ok to do.
        owner = db.User(email=owner_email)
        # Note this can cause 2 pulls straight away due to driver|logic abstraction
        # (driver might have to pull owner to append to User.servers)
        # right now we just trust the model to cache requests
        owner.pull()
        # If owner has master_conf (so a master is present), put master_conf into octo_conf
        # so that VMConf can register slave with master.
        try:
            is_master = json.loads(vm_config)[VMCONF_IS_MASTER_KEY]
            if not isinstance(is_master, bool):
                raise ValueError
        except (ValueError, KeyError, TypeError):
            msg = '{} field invalid or not present in VM configuration!'.format(VMCONF_IS_MASTER_KEY)
            User.add_msg('Error:{}'.format(msg), owner_email)
            Server.delete(provider, server_id, True, owner_email, octo_token, access_token=access_token)
            logging.debug('For {}:{}'.format(owner_email, msg))
            return msg, 400
        # Try to catch a possible lost master provisioner
        if is_master and owner.servers:
            msg = 'Master configure requested with existing servers!'.format(VMCONF_IS_MASTER_KEY)
            User.add_msg('Error:{}'.format(msg), owner_email)
            Server.delete(provider, server_id, True, owner_email, octo_token, access_token=access_token)
            logging.debug('For {}:{}'.format(owner_email, msg))
            return msg, 400
        # Try to catch a possible lost slave provisioner
        if not is_master and owner.master_conf in [{'placeholder': 'placeholder'}, {'placeholder': 'configuring'}, {}]:
            msg = 'Slave configure requested with no master!'.format(VMCONF_IS_MASTER_KEY)
            User.add_msg('Error:{}'.format(msg), owner_email)
            Server.delete(provider, server_id, True, owner_email, octo_token, access_token=access_token)
            logging.debug('For {}:{}'.format(owner_email, msg))
            return msg, 400
        server.is_master = is_master
        server.ip = server_ip
        server.access_token = access_token
        server.status = CREATED_STATUS
        server.ssh_fgpt = ssh_fgpt
        server.vm_config = vm_config
        server.is_self_destruct = False
        server.log = log
        server.metadata = []

        if server.create():

            if server.is_master and owner.master_conf == {'placeholder': 'placeholder'}:
                owner.master_conf = {'placeholder': 'configuring'}  # Make sure create now knows not to recreate master
                owner.push()

            master_conf = None
            if not server.is_master and owner.master_conf:
                master_conf = owner.master_conf

            compose_stacks = None
            if owner.compose and not owner.compose_completed:
                compose_stacks = json.loads(owner.compose)['stacks']

            octo_conf = \
                {
                    OCTO_URL_KEY: OCTO_URL,
                    OCTO_CONFIGURED_SERVER_SUBMIT_PATH_KEY: OCTO_CONFIGURED_SERVER_SUBMIT_PATH,
                    OCTO_SERVER_LOG_SUBMIT_PATH_KEY: OCTO_SERVER_LOG_SUBMIT_PATH,
                    OCTO_MESSAGE_SUBMIT_PATH_KEY: OCTO_MESSAGE_SUBMIT_PATH,
                    OCTO_TOKEN_KEY: issue_token(owner_email),
                    VMCONF_SERVER_HOSTNAME_KEY: server_ip,
                    VMCONF_OCTO_TOKEN_KEY: octo_token,
                    VMCONF_SERVER_PROVIDER_KEY: provider,
                    VMCONF_SERVER_ID_KEY: server_id,
                    VMCONF_MASTERCONF_KEY: master_conf,
                    VMCONF_COMPOSE_STACKS_KEY: compose_stacks
                }

            # Base64 as docker and transport WILL mess with escapes otherwise
            command = base64.b64encode(
                json.dumps(
                    {
                        VMCONF_OCTO_CONF_KEY: octo_conf,
                        VMCONF_PRIVATE_KEY_KEY: temp_key,
                        VMCONF_VMCONF_KEY: vm_config
                    }
                )
            )

            if launch_container(VMCONF_CONTAINER_NAME, command):
                logging.info('Started configuring {}{} for "{}"'.format(provider, server_id, owner_email))
                return 'Server configuration started', 200
            else:
                logging.error(
                    'Failed to schedule configuration of {}{} for "{}". Server info:\n{}'.format(provider,
                                                                                                 server_id,
                                                                                                 owner_email,
                                                                                                 server.data
                                                                                                 )
                )
                return 'System error scheduling server configuration', 500

        else:
            logging.error('FusionDB failed to create a server for "{}". Server info:\n{}'.format(
                owner_email, server.data
            ))
            return 'Failed to create a server', 500

    @staticmethod
    def initialise(server_id, provider, owner_email, octo_token, is_master=False, is_self_destruct=False,
                   master_conf=None):

        # It is easier to use a var as there are a lot of possible responses (Which might be independent of results
        # of called methods)
        response = 'Server initialised', 200

        server = db.Server(owner_email=owner_email, provider=provider, id=server_id)
        if not server.exists():
            return 'Server does not exist', 404
        server.pull()
        if server.status != CREATED_STATUS:
            return 'Server must have created status to be initialised!', 400
        server.status = UP_STATUS
        server.is_master = is_master

        if server.push():
            if is_master:
                owner = db.User(email=owner_email)
                owner.pull()
                owner.master_conf = master_conf
                if owner.push():
                    if owner.compose and not owner.compose_completed:
                        _infrary_compose_stage_two(owner_email, owner, octo_token)
                else:
                    # If anything goes wrong in this section, destroy the server at the end
                    # this is so a broken and/or alienated server is not left with provider costing a customer money
                    is_self_destruct = True
                    response = 'Failed to update master configuration', 500

        else:
            is_self_destruct = True
            response = 'Failed to update server', 500

        server_delete_response = None

        if is_self_destruct:
            server_delete_response = Server.delete(provider, server_id, True, owner_email, octo_token)

        # See logging.*(...) and HTTP codes to understand different branches

        if response[1] != 200:
            logging.debug(
                'There was a problem initialising {}{} for "{}". We told them:\n {}'.format(
                    provider,
                    server_id,
                    owner_email,
                    response
                )
            )
            return response
        elif is_self_destruct:
            if server_delete_response:
                logging.debug('Self-destructed {}{} for "{}"'.format(provider, server_id, owner_email))
                return server_delete_response
            else:  # This is virtually impossible as we should get at least a 500 unless flask goes mad...
                # (Meaning it will 100% happen)
                logging.error('Failed to self-destruct {}{} for "{}". Server info:\n{}'.format(
                    provider, server_id, owner_email, server.data
                ))
                return 'Failed to self destruct the server', 500
        else:
            server, status = Server.get(provider, server_id, owner_email)
            if status == 200:
                logging.debug('Initialised {}{} for "{}"'.format(provider, server_id, owner_email))
                return server, 200
            else:
                logging.error('Everything seemed ok, but I can\'t .get {}{} for "{}". Server info:\n{}'.format(
                    provider, server_id, owner_email, server.get('data')
                ))
                return 'Unable to verify server init', 500


# noinspection PyClassHasNoInit
class Servers(Server):
    """
        A "Class" containing all the logic related to MULTIPLE servers.
        All methods are static as they are called by flask functions (so true OOP would be pointless).
    """

    @staticmethod
    def list(owner_email):
        """
        Returns a list of all servers owned by the user.
        :param str owner_email: Owner's email address aka user_id
        :return: A flask-compatible response tuple.
        :rtype: tuple
        """

        owner = db.User(email=owner_email)
        owner.pull()
        servers = []
        for server_provider_id_pair in owner.servers:
            server = db.Server(
                owner_email=owner_email,
                provider=server_provider_id_pair[0],
                id=server_provider_id_pair[1]
            )
            try:
                server.pull()
            except (AttributeError, NameError):
                # If this comes up, you likely messed up the DB (causing a desync between User.servers and Server)
                logging.error(
                    'Hhmm... {} is in User.servers for "{}", but I failed to get a Server(...) like this'.format(
                        server_provider_id_pair, owner_email
                    ))
                return 'Failed to fetch {}{}'.format(server.provider, server.id), 500
            else:
                servers.append(server.data)
        logging.debug('Listed servers for "{}"'.format(owner_email))
        return jsonify(servers)


def infrary_compose(infrary_compose_b64, owner_email, octo_token):
    """

    :param infrary_compose_b64: base64 encoded infrary-copose file to parse
    :param owner_email:
    :param octo_token:
    :return:
    """
    # noinspection PyPep8
    try:
        infrary_compose_str = base64.b64decode(infrary_compose_b64)
    except TypeError:
        return 'Failed to decode base64', 400
    parser = InfraryComposeParser(infrary_compose_str)
    if not parser.parse():
        return 'Failed to parse infrary-yaml: {}'.format(parser.error), 400
    compose_dict = {'servers': parser.servers, 'master': parser.master, 'stacks': parser.stacks}
    user = db.User(email=owner_email)
    user.pull()
    user.compose = json.dumps(compose_dict)
    if user.master_conf:
        # This is not normal as owner.master_conf suggests we have a master
        if user.master_conf == {'placeholder': 'placeholder'}:
            logging.info('Assuming provisioner failure for {} and redoing compose'.format(owner_email))
            User.add_msg('Assuming compose failure', owner_email)
        else:
            # Assume it is user not understanding things
            logging.debug('"{}" wanted to create another master'.format(owner_email))
            return 'Multiple masters are not supported!', 400
    user.compose_completed = False
    user.push()
    User.add_msg('Applying infrary-compose: Creating master...', owner_email)
    response = Server.create(parser.master['properties'], parser.master['configuration'], owner_email, octo_token,
                             running_compose=True)
    if response[1] != 200:
        return 'Failed to create master: {}'.format(response[0]), response[1]
    else:
        return 'Infrary-compose successfully parsed. Master creation started', 200


def _infrary_compose_stage_two(owner_email, user, octo_token):
    User.add_msg('Master up! Now processing slaves...', owner_email)
    for server in json.loads(user.compose)['servers']:
        result = Server.create(server['properties'], server['configuration'], owner_email, octo_token)
        if result[1] != 200:
            return result
    user.pull()
    user.compose_completed = True
    user.push()
    return 'Compose server creation started', 200


# noinspection PyClassHasNoInit
class Do:
    """
        A provider-specific "Class" containing all the logic related to Digital Ocean servers.
        All methods are static as they are called by flask functions (so true OOP would be pointless).
    """

    @staticmethod
    def get_metadata(token, email):
        """
        Fetch all the metadata options for server creation.
        :param str token: Digital Ocean Account API token.
        :param str email: User email
        :return: A flask-compatible response tuple.
        :rtype: tuple
        """
        session = requests.Session()
        session.headers.update({'Authorization': 'Bearer ' + token})

        response = session.get(DO_BASE_URL + '/sizes')
        if response.status_code != 200:
            logging.debug('"{}" tried using a bad DO key to get metadata'.format(email))
            return 'Invalid request, check API key!', 400
        sizes = response.json()['sizes']

        # we only return images we support auto-configuring (User can still use the rest via the API)
        images = DO_SUPPORTED_IMAGES

        logging.debug('Gave "{}" DO metadata'.format(email))
        return jsonify({'sizes': sizes, 'images': images})


def tmp_user_cleanup():
    """
    A function to cleanup expired inactive users.
    :return: A flask-compatible response tuple.
    :rtype: tuple
    """
    if db.tmp_user_cleanup():
        logging.info('Cleaned temp users')
        return '', 200
    else:
        logging.error('Failed to clean temp users')
        return '', 500
