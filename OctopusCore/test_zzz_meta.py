import pytest
import random
import string
import json
import jwt
import time
import db
import logic
from flask import url_for
from bson import ObjectId


def user_creation_check(app, client):
    user_firstname = ''.join(random.choice(string.ascii_letters) for _ in range(15))
    user_lastname = ''.join(random.choice(string.ascii_letters) for _ in range(25))
    user_email = "tpk1100@gmail.com"
    user_password = "qwerty"
    assert not app.debug, 'Ensure the app not in debug mode'
    try:
        db.delete_one_document({"email": user_email}, db_name="users")
    except:
        pass
    try:
        db.delete_one_document({"email": user_email}, db_name="tmpUsers")
    except:
        pass
    resp = client.post(url_for('register'), content_type='application/json',
                       data=json.dumps(dict(firstName=user_firstname, lastName=user_lastname, email=user_email,
                                            password=user_password)))
    assert resp.status_code == 201
    tmp_user_dict = db.find_one({"email": user_email}, db_name="tmpUsers")
    print tmp_user_dict
    email_key = tmp_user_dict["emailKey"]
    assert client.post(url_for('verify'), content_type='application/json',
                       data=json.dumps(dict(emailKey=email_key))).status_code == 201
    assert db.find_one_if_exists({"email": user_email}, db_name="tmpUsers") == (None, False)
    tmp_user_dict["servers"] = []
    tmp_user_dict["provisioning"] = []
    tmp_user_dict.pop("emailKey")
    user_dict = db.find_one({"email": user_email}, db_name="users")
    assert tmp_user_dict == user_dict
    print user_dict
    resp = client.post(url_for('login'), content_type='application/json',
                       data=json.dumps(dict(email=user_email,
                                            password=user_password)))
    assert resp.status_code == 200
    response_text = resp.get_data()
    print response_text
    try:
        payload = jwt.decode(response_text, 'totallysecure', 'HS256')  # todo change in transition to Asymmetric
        passed = True
    except jwt.InvalidTokenError:
        passed = False
    assert passed
    assert isinstance(payload, dict)
    assert isinstance(payload['uid'], basestring)
    assert isinstance(payload['exp'], int)
    # assert expires in 1h or less
    assert payload['exp'] <= int(time.time()) + 60 * 60
    return response_text, user_dict, user_email

@pytest.mark.options(debug=False)
def test_user_creation(pytestconfig, app, client):
    if pytestconfig.getoption("quick"):
        return None

    response_text, user_dict, user_email = user_creation_check(app, client)

    db.delete_one_document({"email": user_email}, db_name="users")


@pytest.mark.options(debug=False)
def test_user_creation(pytestconfig, app, client, server):
    if pytestconfig.getoption("quick"):
        return None

    response_text, user_dict, user_email = user_creation_check(app, client)


    server_properties = \
        dict(SERVER_PROVIDER="DO", ACCESS_TOKEN="a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6",
             SERVER_NAME="Infrary", SERVER_SIZE="512mb", SERVER_IMAGE="ubuntu-14-04-x64", SERVER_LOCATION="lon1",
             SSH_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3KVkFiPI"
                     "+5RlTiTKsRkjEZr6ssjYFw9Tk0dzoLKYQH8NOWA13tpSo8r6wT7P"
                     "+yxXG631wGSBfHyarCpuNO8X2sS7y1zWFVIiDvp1cT4sKGF3kfMPjmt5vrfrp+qEzxHDG9oQqCvnYv1NnhIsb"
                     "+ZgLG+S56z7ssEx+CPpbUU2RE+27/RYxRNjSZQ7l3eNiQyyvBlPBnK"
                     "+RK6uccUJhG8KfqWB1hOtlJ7H71Mx0RwiLA6as7OK5PuwqkCN5JhzJs48mRjtRE86R0VwKwny"
                     "/LuPmTMyyz7JCg38C4PDgEXIJrAfuo/TJDcqiJnxPeX4+neDnmXEeVvUqMUnbVNlk8qZ+w==")

    vm_configuration = \
        dict(isMaster=True, selfDestruct=False,
             cmdList=["curl https://releases.rancher.com/install-docker/17.06.sh | sh", "service ntp stop",
                      "update-rc.d -f ntp remove", "fallocate -l 4G /swapfile", "chmod 600 /swapfile",
                      "mkswap /swapfile", "swapon /swapfile",
                      "echo \"/swapfile   none    swap    sw    0   0\" >> /etc/fstab",
                      "docker run -d --restart=unless-stopped -p 8080:8080 rancher/server", "sleep 60"])

    body = json.dumps({"serverProperties": server_properties, "VMConfiguration": vm_configuration})

    resp = client.post(url_for('create_server'), content_type='application/json',
                       data=body , headers = {'Authorization': 'Bearer ' + response_text,
            'Content-Type': 'application/json'})
    assert resp.status_code == 201


    user_id = user_dict["_id"]

    def del_user():
        db.delete_one_document({"email": user_email}, db_name="users")

    db_wait_counter = 0
    server_found = False
    while not server_found:
        if db_wait_counter >= 15:
            del_user()
            assert False, "server was never created"
        db_wait_counter += 1

        user = db.find_one({'_id': ObjectId(user_id)}, db_name="users")

        for server in user["provisioning"]:
            if server['__Infrary__Provider'] == "DO":
                user_server = server
                server_found = True
        time.sleep(10)

    print user_server

    db_wait_counter = 0
    server_found = False
    while not server_found:
        if db_wait_counter >= 25:
            del_user()
            assert False, "server was never finalised"
        db_wait_counter += 1

        user = db.find_one({'_id': ObjectId(user_id)}, db_name="users")

        for server in user["servers"]:
            if server['__Infrary__Provider'] == "DO":
                user_server = server
                server_found = True
        time.sleep(10)

    print user_server

    logic.launch_container('provisioner', 'destroy', response_text,
                     {'SERVER_ID': user_server["__Infrary__ID"], 'SERVER_PROVIDER': user_server['__Infrary__Provider'],
                      'ACCESS_TOKEN': server['__Infrary__AccessToken']})

    db.delete_one_document({"email": user_email}, db_name="users")