import pytest
import random
import string
import json
import jwt
import time
import database_mongodb as db
import logic
from flask import url_for
from bson import ObjectId

from constants import *


def user_creation_check(app, client):
    user_firstname = ''.join(random.choice(string.ascii_letters) for _ in range(15))
    user_lastname = ''.join(random.choice(string.ascii_letters) for _ in range(25))
    user_email = "tpk1100@gmail.com"
    user_password = "qwertyui"
    assert not app.debug, 'Ensure the app not in debug mode'
    try:
        db.delete_one_document({EMAIL_KEY: user_email}, USERS_COLLECTION_NAME)
    except:
        pass
    try:
        db.delete_one_document({EMAIL_KEY: user_email}, TMP_USERS_COLLECTION_NAME)
    except:
        pass
    resp = client.post(url_for('register'), content_type='application/json',
                       data=json.dumps(
                           {FIRST_NAME_KEY: user_firstname, LAST_NAME_KEY: user_lastname, EMAIL_KEY: user_email,
                            PASSWORD_KEY: user_password}))
    assert resp.status_code == 201
    tmp_user_dict = db.find_one({EMAIL_KEY: user_email}, TMP_USERS_COLLECTION_NAME)
    print tmp_user_dict
    email_key = tmp_user_dict[EMAIL_KEY_KEY]
    assert client.post(url_for('verify'), content_type='application/json',
                       data=json.dumps({EMAIL_KEY_KEY: email_key})).status_code == 201
    assert db.find_one_if_exists({EMAIL_KEY: user_email}, TMP_USERS_COLLECTION_NAME) == (None, False)
    tmp_user_dict[SERVERS_KEY] = []
    tmp_user_dict.pop(EMAIL_KEY_KEY)
    user_dict = db.find_one({EMAIL_KEY: user_email}, USERS_COLLECTION_NAME)
    assert tmp_user_dict == user_dict
    print user_dict
    resp = client.post(url_for('login'), content_type='application/json',
                       data=json.dumps({EMAIL_KEY: user_email, PASSWORD_KEY: user_password}))
    assert resp.status_code == 200
    response_text = resp.get_data()
    print response_text
    try:
        payload = jwt.decode(response_text, SECRET_TOKEN_ENC_KEY, 'HS256')  # todo change in transition to Asymmetric
        passed = True
    except jwt.InvalidTokenError:
        passed = False
    assert passed
    assert isinstance(payload, dict)
    assert isinstance(payload[TOKEN_USER_ID_KEY], basestring)
    assert isinstance(payload[TOKEN_EXPIRY_KEY], int)
    # assert expires in 1h or less
    assert payload[TOKEN_EXPIRY_KEY] <= int(time.time()) + 60 * 60
    return response_text, user_dict, user_email


@pytest.mark.options(debug=False)
def test_user_creation(pytestconfig, app, client):
    if pytestconfig.getoption("quick"):
        return None

    response_text, user_dict, user_email = user_creation_check(app, client)

    db.delete_one_document({EMAIL_KEY: user_email}, USERS_COLLECTION_NAME)


@pytest.mark.options(debug=False)
def test_server_cycle(pytestconfig, app, client, server):
    if pytestconfig.getoption("quick"):
        return None

    response_text, user_dict, user_email = user_creation_check(app, client)

    server_properties = \
        {PROVISIONER_PROVIDER_KEY: DIGITAL_OCEAN_PROVIDER_CODE,
         PROVISIONER_ACCESS_TOKEN_KEY: "a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6",
         PROVISIONER_SERVER_NAME_KEY: "Infrary", PROVISIONER_SERVER_SIZE_KEY: "512mb",
         PROVISIONER_SERVER_IMAGE_KEY: "ubuntu-14-04-x64",
         PROVISIONER_SERVER_LOCATION_KEY: "lon1",
         PROVISIONER_SSH_KEY_KEY: "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3KVkFiPI"
                                  "+5RlTiTKsRkjEZr6ssjYFw9Tk0dzoLKYQH8NOWA13tpSo8r6wT7P"
                                  "+yxXG631wGSBfHyarCpuNO8X2sS7y1zWFVIiDvp1cT4sKGF3kfMPjmt5vrfrp+qEzxHDG9oQqCvnYv1NnhIsb"
                                  "+ZgLG+S56z7ssEx+CPpbUU2RE+27/RYxRNjSZQ7l3eNiQyyvBlPBnK"
                                  "+RK6uccUJhG8KfqWB1hOtlJ7H71Mx0RwiLA6as7OK5PuwqkCN5JhzJs48mRjtRE86R0VwKwny"
                                  "/LuPmTMyyz7JCg38C4PDgEXIJrAfuo/TJDcqiJnxPeX4+neDnmXEeVvUqMUnbVNlk8qZ+w=="}

    vm_configuration = \
        {VMCONF_IS_MASTER_KEY: True, VMCONF_SELF_DESTRUCT_KEY: False,
         VMCONF_COMMAND_LIST_KEY: ["curl https://releases.rancher.com/install-docker/17.06.sh | sh", "service ntp stop",
                                   "update-rc.d -f ntp remove", "fallocate -l 4G /swapfile", "chmod 600 /swapfile",
                                   "mkswap /swapfile", "swapon /swapfile",
                                   "echo \"/swapfile   none    swap    sw    0   0\" >> /etc/fstab",
                                   "docker run -d --restart=unless-stopped -p 8080:8080 rancher/server", "sleep 60"]}

    body = json.dumps({SERVER_PROPERTIES_KEY: server_properties, VM_CONFIGURATION_KEY: vm_configuration})

    resp = client.post(url_for('create_server'), content_type='application/json',
                       data=body, headers={'Authorization': 'Bearer ' + response_text,
                                           'Content-Type': 'application/json'})
    assert resp.status_code == 200

    user_id = user_dict[DB_ID_KEY]

    def del_user():
        db.delete_one_document({EMAIL_KEY: user_email}, USERS_COLLECTION_NAME)

    db_wait_counter = 0
    server_found = False
    while not server_found:
        if db_wait_counter >= 30:
            del_user()
            assert False, "server was never created"
        db_wait_counter += 1

        user = db.find_one({DB_ID_KEY: ObjectId(user_id)}, USERS_COLLECTION_NAME)

        for server in user[SERVERS_KEY]:
            if server[PROVIDER_EXP_KEY] == DIGITAL_OCEAN_PROVIDER_CODE:
                user_server = server
                server_found = True
        time.sleep(10)

    print user_server

    db_wait_counter = 0
    server_found = False
    while not server_found:
        if db_wait_counter >= 30:
            del_user()
            assert False, "server was never finalised"
        db_wait_counter += 1

        user = db.find_one({DB_ID_KEY: ObjectId(user_id)}, USERS_COLLECTION_NAME)

        for server in user[SERVERS_KEY]:
            if server[PROVIDER_EXP_KEY] == DIGITAL_OCEAN_PROVIDER_CODE and server[STATUS_EXP_KEY] == UP_STATUS:
                user_server = server
                server_found = True
        time.sleep(10)

    print user_server

    resp = client.delete(
        url_for('delete_server', server_provider=user_server[PROVIDER_EXP_KEY], server_id=user_server[ID_EXP_KEY]),
        headers={'Authorization': 'Bearer ' + response_text})

    print resp
    assert resp.status_code == 200

    db_wait_counter = 0
    server_found = False
    while not server_found:
        if db_wait_counter >= 30:
            del_user()
            assert False, "server was never deleted"
        db_wait_counter += 1

        resp = client.get(
            url_for('get_server', server_provider=user_server[PROVIDER_EXP_KEY], server_id=user_server[ID_EXP_KEY]),
            content_type='application/json',
            headers={'Authorization': 'Bearer ' + response_text,
                     'Content-Type': 'application/json'})

        print resp

        if resp.status_code == 404:
            server_found = True
        time.sleep(10)

    db.delete_one_document({EMAIL_KEY: user_email}, USERS_COLLECTION_NAME)
