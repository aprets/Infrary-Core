from do import *
from main import *
import os
import json
import sys

# crypto stuff
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# serverProvider = os.environ['SERVER_PROVIDER']

# todo debug
OCTOCORE_DOMAIN = os.environ['OCTOCORE_DOMAIN']
OCTOCORE_PORT = os.environ['OCTOCORE_PORT']
OCTOCORE_SERVER_SUBMIT_PATH = os.environ['OCTOCORE_SERVER_SUBMIT_PATH']

server_provider = os.environ['SERVER_PROVIDER']

if sys.argv[1] == 'create':

    tmp_key_object = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)
    tmp_pem_key_enc = tmp_key_object.private_bytes(encoding=serialization.Encoding.PEM,
                                                   format=serialization.PrivateFormat.TraditionalOpenSSL,
                                                   encryption_algorithm=serialization.NoEncryption())
    tmp_pem_key_str = tmp_pem_key_enc.decode('utf-8')
    tmp_pub_oss_key_enc = tmp_key_object.public_key().public_bytes(serialization.Encoding.OpenSSH,
                                                                   serialization.PublicFormat.OpenSSH)
    tmp_pub_oss_key_str = tmp_pub_oss_key_enc.decode('utf-8')

    # noinspection SpellCheckingInspection
    if server_provider == "DO":

        access_token = os.environ['ACCESS_TOKEN']
        server_name = os.environ['SERVER_NAME']
        server_size = os.environ['SERVER_SIZE']
        server_image = os.environ['SERVER_IMAGE']
        server_location = os.environ['SERVER_LOCATION']
        ssh_key = os.environ['SSH_KEY']
        octo_token = os.environ['OCTO_TOKEN']

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
        print "well, it WASN'T defined after all!"
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
            server_property_dict['__Infrary__Provider'] = server_provider
            server_property_dict['__Infrary__ID'] = server.id
            server_property_dict['__Infrary__IP'] = server.networks[u'v4'][0][u'ip_address']
            server_property_dict['__Infrary__VMConfiguration'] = os.environ['VMConfiguration']
            server_property_dict['__Infrary__SSHKeyFingerprint'] = server.SSHFingerprints[1]
            server_property_dict['__Infrary__TempSSHKey'] = tmp_pem_key_str
            # noinspection PyUnboundLocalVariable
            server_property_dict['__Infrary__AccessToken'] = access_token
            # noinspection PyUnboundLocalVariable
            headers = {'Authorization': 'Bearer ' + octo_token, 'Content-Type': 'application/json'}
            http_client = HTTPClient(headers, OCTOCORE_DOMAIN, OCTOCORE_PORT, False)
            http_client.post(OCTOCORE_SERVER_SUBMIT_PATH, json.dumps(server_property_dict))
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

elif sys.argv[1] == 'destroy':

    if server_provider == "DO":
        access_token = os.environ['ACCESS_TOKEN']
        serverId = os.environ['SERVER_ID']
        octo_token = os.environ['OCTO_TOKEN']

        server = DoDroplet(access_token=access_token, server_id=serverId)
        response = server.destroy()
        print response.status
