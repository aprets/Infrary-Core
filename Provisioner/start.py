import sys

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from constants import *
from do import *

try:
    from cStringIO import StringIO  # Python 2
except ImportError:
    from io import StringIO

logger = logging.getLogger('provisioner')
logger.setLevel(logging.DEBUG)
log_stream = StringIO()
console_log_handler = logging.StreamHandler(sys.stdout)
console_log_handler.setLevel(logging.DEBUG)
stream_log_handler = logging.StreamHandler(log_stream)
stream_log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s %(asctime)s: %(message)s')
formatter.converter = time.gmtime
console_log_handler.setFormatter(formatter)
stream_log_handler.setFormatter(formatter)
logger.addHandler(console_log_handler)
logger.addHandler(stream_log_handler)


def get_log_str():
    log_stream.seek(0)
    return log_stream.read()


raw_cmd_str = sys.argv[1]
cmd_str = base64.b64decode(raw_cmd_str)
cmd_dict = json.loads(cmd_str)

logger.debug(cmd_dict)

OCTO_CONF = cmd_dict[PROVISIONER_OCTO_CONF_KEY]
octo_token = OCTO_CONF[OCTO_TOKEN_KEY]
action = OCTO_CONF[PROVISIONER_ACTION_KEY]
server_props = cmd_dict[PROVISIONER_PROPERTIES_KEY]

OCTO_URL = OCTO_CONF[OCTO_URL_KEY]
OCTO_MESSAGE_SUBMIT_PATH = OCTO_CONF[OCTO_MESSAGE_SUBMIT_PATH_KEY]
OCTO_SERVER_STATUS_SUBMIT_PATH = OCTO_CONF[OCTO_SERVER_STATUS_SUBMIT_PATH_KEY]


def send_message(submit_message):
    requests.post(OCTO_URL + OCTO_MESSAGE_SUBMIT_PATH, data=submit_message,
                  headers={'Authorization': 'Bearer ' + octo_token, 'Content-Type': 'application/json'})


def fail(fail_message):
    logger.error(fail_message)
    send_message('ERROR:{}'.format(fail_message))
    sys.exit(fail_message)


server_provider = server_props.get(PROVISIONER_PROVIDER_KEY)

if action == PROVISIONER_CREATE_ACTION:
    OCTO_SERVER_SUBMIT_PATH = OCTO_CONF[OCTO_SERVER_SUBMIT_PATH_KEY]

    tmp_key_object = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)
    tmp_pem_key_enc = tmp_key_object.private_bytes(encoding=serialization.Encoding.PEM,
                                                   format=serialization.PrivateFormat.TraditionalOpenSSL,
                                                   encryption_algorithm=serialization.NoEncryption())
    tmp_pem_key_str = tmp_pem_key_enc.decode('utf-8')
    tmp_pub_oss_key_enc = tmp_key_object.public_key().public_bytes(serialization.Encoding.OpenSSH,
                                                                   serialization.PublicFormat.OpenSSH)
    tmp_pub_oss_key_str = tmp_pub_oss_key_enc.decode('utf-8')

    # noinspection SpellCheckingInspection
    if server_provider == DIGITAL_OCEAN_PROVIDER_CODE:

        access_token = server_props.get(PROVISIONER_ACCESS_TOKEN_KEY)
        server_name = server_props.get(PROVISIONER_SERVER_NAME_KEY)
        server_size = server_props.get(PROVISIONER_SERVER_SIZE_KEY)
        server_image = server_props.get(PROVISIONER_SERVER_IMAGE_KEY)
        server_location = server_props.get(PROVISIONER_SERVER_LOCATION_KEY)
        ssh_key = server_props.get(PROVISIONER_SSH_KEY_KEY)

        if not access_token or not server_name or not server_image or not server_location or not server_size \
                or not ssh_key:
            fail("Critical provisioning error: Server properties invalid or missing!")

        server = DoDroplet(access_token=access_token, name=server_name, image={'slug': server_image},
                           region={'slug': server_location}, size={'slug': server_size},
                           ssh_keys=[tmp_pub_oss_key_str, ssh_key], fail_func=fail)

    else:
        fail("Unknown server provider!")

    try:
        # noinspection PyStatementEffect,PyUnboundLocalVariable
        server
        # noinspection PyStatementEffect,PyUnboundLocalVariable
        access_token
        # noinspection PyStatementEffect,PyUnboundLocalVariable
        octo_token

    except NameError:
        fail("Invalid input")

    logger.info("Starting the provisioning process...")
    status, message = server.provision()
    if status is True:
        logger.info("Server ID {} provisioned successfully!".format(str(server.id)))
        response = ''
        try:
            submit_dict = {
                PROVIDER_KEY: server_provider,
                ID_KEY: server.id,
                IP_KEY: server.networks[u'v4'][0][u'ip_address'],
                VM_CONFIGURATION_DB_KEY: server_props.get(VM_CONFIGURATION_DB_KEY),
                SSH_KEY_FINGERPRINT_KEY: server.SSHFingerprints[1],
                TEMP_SSH_KEY_KEY: tmp_pem_key_str,
                ACCESS_TOKEN_KEY: access_token,
                LOG_KEY: get_log_str()
            }
            headers = {'Authorization': 'Bearer ' + octo_token, 'Content-Type': 'application/json'}
            response = requests.post(OCTO_URL + OCTO_SERVER_SUBMIT_PATH, json=submit_dict, headers=headers)
            logger.info("Server data submitted successfully!")
        except Exception as e:
            logger.info("Destroying the server...")
            logger.debug("Server:\n{}\nResponse:\n{}".format(str(server), str(server.destroy())))
            fail('Unable to submit server: {}'.format(response.text))
        finally:
            logger.debug("Server:\n{}".format(str(server)))

    else:
        try:
            logger.info("Destroying the server...")
            logger.debug("Server:\n{}\nResponse:\n{}".format(str(server), str(server.destroy())))
        except (ValueError, TypeError):
            pass
        fail("Critical provisioning error: {}".format(message))

elif action == PROVISIONER_DESTROY_ACTION:

    def submit_status(server_provider, server_id, status):
        try:
            headers_delete = {'Authorization': 'Bearer ' + octo_token, 'Content-Type': 'application/json'}
            requests.post(OCTO_URL + OCTO_SERVER_STATUS_SUBMIT_PATH.format(
                server_id=server_id,
                server_provider=server_provider),
                          json=
                          {
                              ACTION_KEY: SET_STATUS_ACTION,
                              STATUS_KEY: status,

                          }, headers=headers_delete)
        except Exception as e:
            logger.debug("{}\n{}\n{}".format(status, OCTO_CONF, server_props))
            fail("Unable to submit data to OctoCore {}".format(str(e.message)))

        else:
            logger.debug("{}\n{}\n{}".format(status, OCTO_CONF, server_props))


    if server_provider == DIGITAL_OCEAN_PROVIDER_CODE:
        access_token = server_props.get(PROVISIONER_ACCESS_TOKEN_KEY)
        server_id = server_props.get(PROVISIONER_SERVER_ID_KEY)

        server = DoDroplet(access_token=access_token, server_id=server_id, fail_func=fail)
        response = server.destroy()
        logger.debug('{}\n{}\n{}'.format(response, response.status_code, response.text))
        if response.status_code == 204:
            submit_status(server_provider, server_id, DELETED_STATUS)

        elif response.status_code == 404:
            submit_status(server_provider, server_id, FAILED_DELETE_PROVIDER_STATUS)

        else:
            submit_status(server_provider, server_id, FAILED_DELETE_STATUS)

    elif server_provider == BYO_PROVIDER_CODE:
        server_id = server_props.get(PROVISIONER_SERVER_ID_KEY)
        submit_status(server_provider, server_id, DELETED_STATUS)

    else:
        fail("Unknown server provider!")
