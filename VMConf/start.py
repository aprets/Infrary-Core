from main import *
import os
import time
import sys
import paramiko
import select
import string
import random
import json
import StringIO

# todo debug
OCTOCORE_DOMAIN = os.environ['OCTOCORE_DOMAIN']
OCTOCORE_PORT = os.environ['OCTOCORE_PORT']
OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH = os.environ['OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH']

# todo undebug
for arg in sys.argv:
    print arg


def rancher_init():
    # Create API Key for future use

    rancher_key_secret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(50))
    json_headers = {'Content-Type': 'application/json'}
    an_http_client = HTTPClient(json_headers, octo_conf['serverHostname'], 8080, False)
    body = json.dumps(
        {"description": "Do Not Delete Infrary API KEY", "name": "Infrary API KEY", "publicValue": "InfraryAPIKey",
         "secretValue": rancher_key_secret})
    rancher_response = an_http_client.post('/v2-beta/apiKeys', body)
    if rancher_response.status != 201:
        return False, rancher_response.body
    import base64
    auth_str = base64.b64encode('InfraryAPIKey:{}'.format(rancher_key_secret))
    json_headers['Authorization'] = 'Basic {}'.format(auth_str)
    # Init a new Client with API key in headers
    an_http_client = HTTPClient(json_headers, octo_conf['serverHostname'], 8080, False)

    # Enable auth

    rancher_user = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
    rancher_pass = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(50))
    body = json.dumps({"enabled": True, "name": "Infrary User", "password": rancher_pass, "username": rancher_user})
    rancher_response = an_http_client.post('/v2-beta/localauthconfig', body)
    if rancher_response.status != 201:
        return False, rancher_response.body
    else:
        rancher_conf_dict = \
            {
                'host': '{}:8080'.format(octo_conf['serverHostname']),
                'user': rancher_user,
                'pass': rancher_pass,
                'keySecret': rancher_key_secret
            }
        return True, rancher_conf_dict


def rancher_install():
    try_counter = 1
    is_rancher_alive = False
    while not is_rancher_alive:
        if try_counter == 15:
            return False, 'Rancher not responding'
        print 'Attempting to connect to Rancher (Attempt {})'.format(str(try_counter))
        try_counter += 1
        try:
            rancher_headers = {'Content-Type': 'application/json'}
            an_http_client = HTTPClient(rancher_headers, octo_conf['serverHostname'], 8080, False)
            rancher_response = an_http_client.get('/')
            if rancher_response.status == 200:
                is_rancher_alive = True
                print "Rancher is up!"
        except Exception as an_error:
            print an_error, an_error.message, an_error.args
            time.sleep(10)

    return rancher_init()


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
        command_list = vm_configuration["cmdList"]
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
        if vm_configuration['isMaster'] is True:
            is_master = True
    except (ValueError, TypeError):
        pass

    try:
        if vm_configuration['selfDestruct'] is True:
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
            ssh_client.connect(octo_conf['serverHostname'], 22, 'root', pkey=ssh_key)
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

    submit_dict = {'__Infrary__SelfDestruct': self_destruct, '__Infrary__IsMaster': is_master}

    try:
        # noinspection PyStatementEffect,PyUnboundLocalVariable
        master_conf

    except NameError:
        print "well, it WASN'T defined after all!"
        exit(1)

    print command_list, octo_conf, vm_configuration

    if is_master:
        submit_dict['__Infrary__MasterConf'] = master_conf
    submit_dict['__Infrary__Provider'] = octo_conf["serverProvider"]
    submit_dict['__Infrary__ID'] = octo_conf["serverID"]
    headers = {'Authorization': 'Bearer ' + octo_conf['octoToken'], 'Content-Type': 'application/json'}
    an_http_client = HTTPClient(headers, OCTOCORE_DOMAIN, OCTOCORE_PORT, False)
    an_http_client.post(OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH, json.dumps(submit_dict))


else:
    print "Not enough args supplied!"
