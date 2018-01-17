from do import *
import requests
import os
import sys

from constants import *

# crypto stuff
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# todo debug
OCTOCORE_DOMAIN = os.environ[OCTO_DOMAIN_KEY]
OCTOCORE_PORT = os.environ[OCTO_PORT_KEY]
OCTOCORE_SERVER_SUBMIT_PATH = os.environ[OCTO_SERVER_SUBMIT_PATH_KEY]

server_provider = os.environ[PROVISIONER_PROVIDER_KEY]

if sys.argv[1] == PROVISIONER_CREATE_COMMAND:

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

        access_token = os.environ[PROVISIONER_ACCESS_TOKEN_KEY]
        server_name = os.environ[PROVISIONER_SERVER_NAME_KEY]
        server_size = os.environ[PROVISIONER_SERVER_SIZE_KEY]
        server_image = os.environ[PROVISIONER_SERVER_IMAGE_KEY]
        server_location = os.environ[PROVISIONER_SERVER_LOCATION_KEY]
        ssh_key = os.environ[PROVISIONER_SSH_KEY_KEY]
        octo_token = os.environ[OCTO_TOKEN_KEY]

        if not access_token or not server_name or not server_image or not server_location or not server_size \
                or not ssh_key or not octo_token:
            print("Vars missing")
            exit(1)

        server = DoDroplet(access_token=access_token, name=server_name, image={'slug': server_image},
                           region={'slug': server_location}, size={'slug': server_size},
                           ssh_keys=[tmp_pub_oss_key_str, ssh_key])

    # TODO VT SUPPORT DISABLED UNTIL FUTURE VERSIONS
    # elif serverProvider == "VT":
    #     apiKey = os.environ['API_KEY']
    #     DCID = os.environ['DCID']
    #     VPSPLANID = os.environ['VPSPLANID']
    #     OSID = os.environ['OSID']
    #     server = doDroplet(accessToken=accessToken,name=serverName, image={'slug':serverImage},region={'slug':serverLocation},size={'slug':serverSize})
    else:
        print ("Unknown server provider!")
        exit(1)

    try:
        # noinspection PyStatementEffect,PyUnboundLocalVariable
        server
        # noinspection PyStatementEffect,PyUnboundLocalVariable
        access_token
        # noinspection PyStatementEffect,PyUnboundLocalVariable
        octo_token

    except NameError:
        print "well, it WASN'T defined after all!"  # TODO
        exit(1)

    print "Starting the provisioning process..."
    status, message = server.provision()
    if status is True:
        print "Server ID {} provisioned successfully!".format(str(server.id))
        try:
            server_property_dict = {}
            for k, v in vars(server).items():  # m/b do not do this? rely on further code for fetching? todo ?
                if k[0] != '_':
                    server_property_dict[k] = v
            server_property_dict[PROVIDER_EXP_KEY] = server_provider
            server_property_dict[ID_EXP_KEY] = server.id
            server_property_dict[IP_EXP_KEY] = server.networks[u'v4'][0][u'ip_address']
            server_property_dict[VM_CONFIGURATION_EXP_KEY] = os.environ['VMConfiguration']
            server_property_dict[SSH_KEY_FINGERPRINT_EXP_KEY] = server.SSHFingerprints[1]
            server_property_dict[TEMP_SSH_KEY_EXP_KEY] = tmp_pem_key_str
            # noinspection PyUnboundLocalVariable
            server_property_dict[ACCESS_TOKEN_EXP_KEY] = access_token
            # noinspection PyUnboundLocalVariable
            headers = {'Authorization': 'Bearer ' + octo_token, 'Content-Type': 'application/json'}
            requests.post(OCTO_URL + OCTOCORE_SERVER_SUBMIT_PATH, json=server_property_dict, headers=headers)
            print "Great success!"
        except Exception as e:
            print ("Unable to submit data to OctoCore"), e  # TODO use production name
            print "Destroying the server..."
            print "Response:\n", server.destroy()
        finally:
            # print json.dumps(server, default=lambda o: o.__dict__)
            # debug
            print "\n\n\n\nDebug stuff:\n"
            print "Server:"
            print server

    else:
        print "There was a critical error provisioning the server!"
        try:
            print "Destroying the server..."
            print "Response:\n", server.destroy()
        except (ValueError, TypeError):
            pass

elif sys.argv[1] == PROVISIONER_DESTROY_COMMAND:

    def submit_status(server_provider, server_id, status):
        print("boii")
        try:
            headers_delete = {'Authorization': 'Bearer ' + octo_token, 'Content-Type': 'application/json'}
            print("boiii")
            requests.post(OCTO_URL + OCTO_SERVER_STATUS_SUBMIT_PATH.format(
                server_id=server_id,
                server_provider=server_provider),
                          json=
                          {
                              ACTION_KEY: SET_STATUS_ACTION,
                              STATUS_KEY: status,

                          }, headers=headers_delete)
            print("boiiii")
        except Exception as e:
            print ("Unable to submit data to OctoCore"), e  # TODO use production name
        finally:
            # print json.dumps(server, default=lambda o: o.__dict__)
            # debug
            print "\n\n\n\nDebug stuff:\n"
            print status, os.environ


    if server_provider == DIGITAL_OCEAN_PROVIDER_CODE:
        access_token = os.environ[PROVISIONER_ACCESS_TOKEN_KEY]
        server_id = os.environ[PROVISIONER_SERVER_ID_KEY]
        octo_token = os.environ[OCTO_TOKEN_KEY]

        server = DoDroplet(access_token=access_token, server_id=server_id)
        response = server.destroy()
        print("boi")
        print response, response.status_code, response.text
        if response.status_code == 204:
            submit_status(server_provider, server_id, DELETED_STATUS)

        elif response.status_code == 404:
            submit_status(server_provider, server_id, FAILED_DELETE_PROVIDER_STATUS)

        else:
            submit_status(server_provider, server_id, FAILED_DELETE_STATUS)
            # todo extend submission for error reporting

    else:
        exit(1)
