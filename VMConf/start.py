import base64
import json
import logging
import sys
import time
from StringIO import StringIO

import requests

import master
import ssh
from constants import *

logger = logging.getLogger('vmconf')
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

raw_cmd_str = sys.argv[1]
cmd_str = base64.b64decode(raw_cmd_str)
cmd_dict = json.loads(cmd_str)

logger.debug(cmd_dict)

OCTO_CONF = cmd_dict[VMCONF_OCTO_CONF_KEY]
OCTO_TOKEN = OCTO_CONF[OCTO_TOKEN_KEY]
KEY_STR = cmd_dict[VMCONF_PRIVATE_KEY_KEY]

logger.debug("KEY: {}".format(KEY_STR))


def get_log_str():
    log_stream.seek(0)
    return log_stream.read()


def send_message(submit_message):
    global OCTO_CONF
    requests.post(OCTO_CONF[OCTO_URL_KEY] + OCTO_CONF[OCTO_MESSAGE_SUBMIT_PATH_KEY], data=submit_message,
                  headers={'Authorization': 'Bearer ' + OCTO_TOKEN, 'Content-Type': 'application/json'})


def fail(fail_message):
    logger.error(fail_message)
    send_message('ERROR:{}'.format(fail_message))
    sys.exit(fail_message)


len_log_submitted = 0


def submit_log():
    global len_log_submitted
    global OCTO_CONF
    text_to_submit = get_log_str()[len_log_submitted:]
    len_log_submitted += len(text_to_submit)
    if text_to_submit:
        response = requests.post(OCTO_CONF[OCTO_URL_KEY] + OCTO_CONF[OCTO_SERVER_LOG_SUBMIT_PATH_KEY].format(
            server_id=OCTO_CONF[VMCONF_SERVER_ID_KEY],
            server_provider=OCTO_CONF[VMCONF_SERVER_PROVIDER_KEY]), data=text_to_submit,
                                 headers={'Authorization': 'Bearer ' + OCTO_TOKEN, 'Content-Type': 'application/json'})
        if response.status_code != 200:
            logger.error('Failed to submit log: {}'.format(response.text))


class BadCmdListTypeError(Exception):
    pass

try:
    VM_CONFIGURATION = json.loads(cmd_dict[VMCONF_VMCONF_KEY])
    COMMAND_LIST = VM_CONFIGURATION[VMCONF_COMMAND_LIST_KEY]
    if not isinstance(COMMAND_LIST, list):
        raise BadCmdListTypeError
except Exception as e:
    if isinstance(e, BadCmdListTypeError):
        logger.error("An error has occurred parsing the command list. Proceeding with empty list.")
        send_message("ERROR:Error parsing command list. Proceeding with empty list.")
        COMMAND_LIST = []
    else:
        logger.error("An error has occurred parsing the vm configuration. Proceeding with empty vm configuration")
        send_message("ERROR:Error parsing the vm configuration. Proceeding with empty vm configuration")
        VM_CONFIGURATION = {}
        COMMAND_LIST = []


logger.debug("Command list:\n{}\n\nOcto Conf:\n{}\n\nVM Conf:\n{}\n\n".format(
    COMMAND_LIST, OCTO_CONF, VM_CONFIGURATION)
)

submit_log()

is_master = False
try:
    if VM_CONFIGURATION[VMCONF_IS_MASTER_KEY] is True:
        is_master = True
except (ValueError, TypeError):
    logger.error("An error has occurred parsing is_master. Assuming a slave")
    pass

self_destruct = False
try:
    if VM_CONFIGURATION[VMCONF_SELF_DESTRUCT_KEY] is True:
        self_destruct = True
except (ValueError, TypeError):
    logger.error("An error has occurred parsing self_destruct. Assuming no self destruct")
    pass

if len(COMMAND_LIST) == 0 and is_master:
    COMMAND_LIST = ["curl https://releases.rancher.com/install-docker/17.06.sh | sh", "service ntp stop",
                    "update-rc.d -f ntp remove", "fallocate -l 4G /swapfile", "chmod 600 /swapfile",
                    "mkswap /swapfile", "swapon /swapfile",
                    "echo \"/swapfile   none    swap    sw    0   0\" >> /etc/fstab", "docker rm -f rancher",
                    "docker run -d --restart=unless-stopped --name=rancher -p 8080:8080 rancher/server:v1.6.17", "sleep 60"]

if not is_master:
    logger.info('Adding slave configuration to commands...')
    for cmd in master.Rancher.fetch_slave_cmds(OCTO_CONF[VMCONF_MASTERCONF_KEY]):
        COMMAND_LIST.append(cmd)

ssh_client = ssh.SSHClient(OCTO_CONF[VMCONF_SERVER_HOSTNAME_KEY], 22, 'root', KEY_STR)

counter = 1
connected = False
while not connected:
    logger.info("Attempting to SSH to the server... (Attempt {})".format(str(counter)))

    if counter >= 15:
        logger.error("Failed to SSH to the server")
        submit_log()
        fail("Failed to SSH to the server")

    counter += 1

    connected = ssh_client.connect()

    if not connected:
        time.sleep(5)

    submit_log()

try:
    logger.info("Connected to the server!")
    for command in COMMAND_LIST:
        try:
            command = str(command)
        except:
            logger.error('Command is not a string!')
        else:
            logger.info("EXEC: {}".format(str(command)))  # just in case
            submit_log()
            if command:
                ssh_client.execute_command(command)
            submit_log()
finally:
    ssh_client.close()

if is_master:
    # master.Rancher logs for us
    rancher = master.Rancher(OCTO_CONF[VMCONF_SERVER_HOSTNAME_KEY], OCTO_CONF[VMCONF_COMPOSE_STACKS_KEY])

    if rancher.connect(submit_log):
        logger.info('Connected to Rancher!')
        logger.info('Configuring Rancher...')
        submit_log()

        try:
            rancher_conf_dict = rancher.configure()

        except master.RancherCommError as error:
            is_master = False
            self_destruct = True
            logger.error("Error configuring Rancher server:\n    {}".format(error.message))
            submit_log()
            send_message("Error configuring Rancher server:\n    {}".format(error.message))

        else:
            if rancher_conf_dict:
                logger.info('Rancher configured successfully!')
                master_conf = rancher_conf_dict
            else:
                logger.error("Error configuring Rancher server: Got no master_conf dict")
                is_master = False
                self_destruct = True
                submit_log()
                send_message("Error configuring Rancher server: Got no master_conf dict")

    else:
        is_master = False
        self_destruct = True
        logger.error("Failed to connect to rancher")
        submit_log()
        send_message("Failed to connect to rancher")

logger.debug("Prepping to submit results...")

submit_dict = {SELF_DESTRUCT_KEY: self_destruct, IS_MASTER_KEY: is_master}

if is_master:
    # noinspection PyUnboundLocalVariable
    submit_dict[MASTERCONF_KEY] = master_conf
submit_dict[PROVIDER_KEY] = OCTO_CONF[VMCONF_SERVER_PROVIDER_KEY]
submit_dict[ID_KEY] = OCTO_CONF[VMCONF_SERVER_ID_KEY]
headers = {'Authorization': 'Bearer ' + OCTO_TOKEN, 'Content-Type': 'application/json'}
logger.debug("Submit dict:\n" + str(submit_dict))
response = requests.post(OCTO_CONF[OCTO_URL_KEY] + OCTO_CONF[OCTO_CONFIGURED_SERVER_SUBMIT_PATH_KEY], headers=headers,
                         json=submit_dict)
logger.debug("Response:\n" + str(response.status_code) + "\n" + response.text)
submit_log()
