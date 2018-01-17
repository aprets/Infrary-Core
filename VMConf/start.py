import requests
import os
import time
import sys
import paramiko
import select
import string
import random
import json
import StringIO

from constants import *

# todo debug
OCTOCORE_DOMAIN = os.environ[OCTO_DOMAIN_KEY]
OCTOCORE_PORT = os.environ[OCTO_PORT_KEY]
OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH = os.environ[OCTO_CONFIGURED_SERVER_SUBMIT_PATH_KEY]

# todo undebug
for arg in sys.argv:
    print arg


def rancher_init(session):
    # Create API Key for future use

    print "Ready to init rancher"
    rancher_key_secret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(50))
    rancher_response = session.post(
        "http://{}:{}{}".format(octo_conf[VMCONF_SERVER_HOSTNAME_KEY], 8080, '/v2-beta/apiKeys'),
        json=
        {
            "description": "Do Not Delete Infrary API KEY",
            "name": "Infrary API KEY",
            "publicValue": "InfraryAPIKey",
            "secretValue": rancher_key_secret
        }
    )
    if rancher_response.status_code != 201:
        return False, rancher_response.text
    import base64
    auth_str = base64.b64encode('InfraryAPIKey:{}'.format(rancher_key_secret))
    session.headers.update({'Authorization': 'Basic {}'.format(auth_str)})

    # Enable auth

    rancher_user = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
    rancher_pass = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(50))
    rancher_response = session.post(
        "http://{}:{}{}".format(octo_conf[VMCONF_SERVER_HOSTNAME_KEY], 8080, '/v2-beta/localauthconfig'),
        json=
        {
            "enabled": True,
            "name": "Infrary User",
            "password": rancher_pass,
            "username": rancher_user
        }
    )
    if rancher_response.status_code != 201:
        return False, rancher_response.text
    else:
        rancher_conf_dict = \
            {
                MASTERCONF_HOST_KEY: '{}:8080'.format(octo_conf[VMCONF_SERVER_HOSTNAME_KEY]),
                MASTERCONF_USER_KEY: rancher_user,
                MASTERCONF_PASSWORD_KEY: rancher_pass,
                MASTERCONF_SECRET_KEY: rancher_key_secret
            }
        return True, rancher_conf_dict


def rancher_install():
    try_counter = 1
    is_rancher_alive = False
    session = requests.Session()
    while not is_rancher_alive:
        if try_counter == 15:
            return False, 'Rancher not responding'
        print 'Attempting to connect to Rancher (Attempt {})'.format(str(try_counter))
        try_counter += 1
        try:
            rancher_response = session.get('http://{}:{}/'.format(octo_conf[VMCONF_SERVER_HOSTNAME_KEY], 8080))
            if rancher_response.status_code == 200:
                is_rancher_alive = True
                print "Rancher is up!"
        except Exception as an_error:
            print an_error, an_error.message, an_error.args
            time.sleep(10)

    return rancher_init(session)


if len(sys.argv) == 4 and '' not in [sys.argv[1], sys.argv[2], sys.argv[3]]:

    key_str = sys.argv[1].replace('\\n', '\n')

    print key_str

    ssh_key = paramiko.RSAKey.from_private_key(StringIO.StringIO(key_str))

    try:
        octo_conf = json.loads(sys.argv[2])
    except Exception as e:
        # todo undebug
        print "An error has occurred parsing the octoConf"
        print e
        exit(1)

    try:
        print sys.argv[3]
        vm_configuration = json.loads(sys.argv[3])
        print vm_configuration
        command_list = vm_configuration[VMCONF_COMMAND_LIST_KEY]
    except Exception as e:
        # todo undebug
        print "An error has occurred parsing the command list"
        print e
        exit(1)

    try:
        # noinspection PyStatementEffect,PyUnboundLocalVariable
        command_list
        # noinspection PyStatementEffect,PyUnboundLocalVariable
        octo_conf
        # noinspection PyStatementEffect,PyUnboundLocalVariable
        vm_configuration

    except NameError:
        print "well, it WASN'T defined after all!"
        exit(1)

    print command_list, octo_conf, vm_configuration

    is_master = False
    try:
        if vm_configuration[VMCONF_IS_MASTER_KEY] is True:
            is_master = True
    except (ValueError, TypeError):
        pass

    try:
        if vm_configuration[VMCONF_SELF_DESTRUCT_KEY] is True:
            self_destruct = True
        else:
            self_destruct = False
    except (ValueError, TypeError):
        self_destruct = False

    counter = 1
    connected = False
    while not connected:
        print "Attempting to connect... (Attempt {})".format(str(counter))

        if counter >= 15:
            print ("Failed to connect")
            exit(1)

        counter += 1

        try:

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy)
            ssh_client.connect(octo_conf[VMCONF_SERVER_HOSTNAME_KEY], 22, 'root', pkey=ssh_key)  # todo always root?
            connected = True
            print "connected"
            for command in command_list:
                print "EXEC: " + command

                stdin, stdout, stderr = ssh_client.exec_command(command)

                # Wait for the command to terminate
                while not stdout.channel.exit_status_ready():
                    # Only print data if there is data to read in the channel
                    if stdout.channel.recv_ready():
                        rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                        if len(rl) > 0:
                            # Print data from stdout
                            print stdout.channel.recv(1024),
                    if stderr.channel.recv_ready():
                        rl, wl, xl = select.select([stderr.channel], [], [], 0.0)
                        if len(rl) > 0:
                            # Print data from stderr
                            print stderr.channel.recv(1024),

        except Exception as e:
            print e, e.message, e.args

        finally:
            ssh_client.close()

        if not connected:
            time.sleep(5)

    try:

        if is_master:
            result, data = rancher_install()
            if result is True:
                master_conf = data
            else:
                self_destruct = True
                # todo report to octocore
                print "Error configuring Rancher server"
        else:
            pass
            # todo make slave

    except Exception as e:
        print e, e.message, e.args
        self_destruct = True

    print "Prepping to submit results..."

    submit_dict = {SELF_DESTRUCT_EXP_KEY: self_destruct, IS_MASTER_EXP_KEY: is_master}

    print command_list, octo_conf, vm_configuration

    if is_master:
        submit_dict[MASTERCONF_EXP_KEY] = master_conf
    submit_dict[PROVIDER_EXP_KEY] = octo_conf["serverProvider"]
    submit_dict[ID_EXP_KEY] = octo_conf["serverID"]
    headers = {'Authorization': 'Bearer ' + octo_conf[VMCONF_OCTO_TOKEN_KEY], 'Content-Type': 'application/json'}
    response = requests.post(OCTO_URL+OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH, headers=headers, json=submit_dict)
    print response.status_code, response.text


else:
    print "Not enough args supplied!"
