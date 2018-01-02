from conftest import *
import logic
import time
import datetime
import jwt
from bson.objectid import ObjectId
import pytest
from mock import call


# There is no launchContainer test (yet[ish]) as it really, really should not exist.
# Substitute will be completely different.

# noinspection PyClassHasNoInit
class MockSendGridResponse:
    status_code = 202
    body = "I am really fake"
    headers = "We are fake too!"


def mock_jsonify(data):
    return json.dumps(data), 200


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize("does_exist, expected_code",
                         [
                             (False, 201),
                             (True, 400)

                         ])
def test_user_register(mocker, does_exist, expected_code):
    mocker.patch('logic.db.exists_once_or_not')
    mocker.patch("logic.db.create_document")
    mocker.patch('logic.send_sendgrid_email_key_email')
    logic.db.exists_once_or_not.return_value = does_exist
    logic.send_sendgrid_email_key_email.return_value = MockSendGridResponse()
    response_text, response_code = logic.User.register("a", "b", "c", "d")
    assert response_code == expected_code
    if does_exist:
        # noinspection PyUnresolvedReferences,PyUnresolvedReferences
        assert (2 == logic.db.exists_once_or_not.call_count or 1 == logic.db.exists_once_or_not.call_count)
        # noinspection PyUnresolvedReferences
        assert not logic.db.create_document.called
    else:
        # noinspection PyUnresolvedReferences
        logic.db.exists_once_or_not.assert_has_calls([call({'email': "c"}, db_name="users"), call({'email': "c"},
                                                                                                  db_name="tmpUsers")])
        # noinspection PyUnresolvedReferences
        logic.db.create_document.assert_called_once_with({
            "firstName": "a",
            "lastName": "b",
            "email": "c",
            "hash": mocker.ANY,
            "emailKey": mocker.ANY,
            "createdAt": mocker.ANY,
        }, db_name="tmpUsers")
    if expected_code == 200 or not does_exist:
        # noinspection PyUnresolvedReferences
        assert logic.send_sendgrid_email_key_email.called_once_with(mocker.ANY, "c")
    else:
        # noinspection PyUnresolvedReferences
        assert not logic.send_sendgrid_email_key_email.called


# noinspection SpellCheckingInspection
@pytest.mark.parametrize("does_exist, expected_code",
                         [
                             (True, 201),
                             (False, 400)

                         ])
def test_user_verify(mocker, does_exist, expected_code):
    mocker.patch('logic.db.find_one_if_exists')
    mocker.patch("logic.db.create_document")
    mocker.patch('logic.db.delete_one_document')
    creation_date_time = datetime.datetime.utcnow()
    logic.db.find_one_if_exists.return_value = \
        {
            "firstName": "a",
            "lastName": "b",
            "email": "c",
            "hash": "$2b$12$kWmswlgA/X50JCOkozD0Z.86v.iR4/909u/VGNH0CV3SVSFkGiEWm",
            "emailKey": "879rh4t98ty98hHUHIU8989h98hh8h89huihIUYHUYIUIUI78yh78y89h89hh",
            "createdAt": creation_date_time,
        }, does_exist
    response_text, response_code = logic.User.verify("879rh4t98ty98hHUHIU8989h98hh8h89huihIUYHUYIUIUI78yh78y89h89hh")
    assert response_code == expected_code
    # noinspection PyUnresolvedReferences
    logic.db.find_one_if_exists.assert_called_once_with({
        'emailKey': "879rh4t98ty98hHUHIU8989h98hh8h89huihIUYHUYIUIUI78yh78y89h89hh"
    }, db_name="tmpUsers")
    if does_exist:
        # noinspection PyUnresolvedReferences
        logic.db.delete_one_document.assert_called_once_with({
            'emailKey': "879rh4t98ty98hHUHIU8989h98hh8h89huihIUYHUYIUIUI78yh78y89h89hh"
        }, db_name="tmpUsers")
        # noinspection PyUnresolvedReferences
        logic.db.create_document.assert_called_once_with({
            "firstName": "a",
            "lastName": "b",
            "servers": [],
            "provisioning": [],
            "email": "c",
            "hash": "$2b$12$kWmswlgA/X50JCOkozD0Z.86v.iR4/909u/VGNH0CV3SVSFkGiEWm",
            "createdAt": creation_date_time,
        }, db_name="users")
    else:
        # noinspection PyUnresolvedReferences
        assert not logic.db.delete_one_document.called
        # noinspection PyUnresolvedReferences
        assert not logic.db.create_document.called


# noinspection PyUnboundLocalVariable,SpellCheckingInspection
@pytest.mark.parametrize("does_exist, pw_hash, pw, expected_code",
                         [
                             (True, "$2a$12$krm6imEScXbJGF7zWJcIiesWvR1d2o5HpGtO9EjMw7GCUJvtv6gPa", "d", 200),
                             (False, "$2a$12$krm6imEScXbJGF7zWJcIiesWvR1d2o5HpGtO9EjMw7GCUJvtv6gPa", "d", 400),
                             (True, "sad", "d", 500),
                             (True, "$2a$12$krm6imEScXbJGF7zWJcIiesWvR1d2o5HpGtO9EjMw7GCUJvtv6gPa", "dd", 400),

                         ])
def test_user_login(mocker, does_exist, pw_hash, pw, expected_code):
    mocker.patch('logic.db.find_one_if_exists')
    creation_date_time = datetime.datetime.utcnow()
    logic.db.find_one_if_exists.return_value = {
                                                   "_id": "5a42c63d4830602278d0a7ca",
                                                   "firstName": "a",
                                                   "lastName": "b",
                                                   "servers": [],
                                                   "provisioning": [],
                                                   "email": "c",
                                                   "hash": pw_hash,
                                                   "createdAt": creation_date_time,
                                               }, does_exist
    response_text, response_code = logic.User.login("c", pw)
    assert response_code == expected_code
    # noinspection PyUnresolvedReferences
    logic.db.find_one_if_exists.assert_called_once_with({'email': "c"}, db_name="users")
    if expected_code == 200:
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


# noinspection SpellCheckingInspection
@pytest.mark.parametrize("does_exist, provider, server_id, user_id, expected_code",
                         [
                             (True, "DO", 1, "5a42c63d4430602278d0a7ca", 200),
                             (True, "DO", 1, "5a42c63d4430602278d0a7c", 400),
                             (False, "DO", 1, "5a42c63d4430602278d0a7ca", 500),
                             (True, "DOO", 2, "5a42c63d4430602278d0a7ca", 404),
                             (True, "DO", 2, "5a42c63d4430602278d0a7ca", 404),
                             (True, "DOO", 1, "5a42c63d4430602278d0a7ca", 404),

                         ])
def test_server_get(mocker, does_exist, provider, server_id, user_id, expected_code):
    mocker.patch('logic.db.find_one_if_exists')
    mocker.patch('logic.jsonify',
                 side_effect=mock_jsonify)  # werkzeug does not like all the logic.py, db.py, api.py shenanigans
    creation_date_time = datetime.datetime.utcnow()
    logic.db.find_one_if_exists.return_value = \
        {
            "id": user_id,
            "firstName": "a",
            "lastName": "b",
            "servers": [
                dict(
                    __Infrary__VMConfiguration=r"{\"isMaster\": true, \"selfDestruct\": true, \"cmdList\": [\"curl "
                                               r"https://releases.rancher.com/install-docker/17.06.sh | sh\", "
                                               r"\"service ntp stop\", \"update-rc.d -f ntp remove\", \"fallocate -l "
                                               r"4G /swapfile\", \"chmod 600 /swapfile\", \"mkswap /swapfile\", "
                                               r"\"swapon /swapfile\", \"echo \\\"/swapfile   none    swap    sw    0  "
                                               r" 0\\\" >> /etc/fstab\", \"docker run -d --restart=unless-stopped -p "
                                               r"8080:8080 rancher/server\", \"sleep 60\"]}",
                    __Infrary__AccessToken="a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6",
                    __Infrary__Provider="DO",
                    __Infrary__SSHKeyFingerprint="92:6e:45:ba:a8:a0:7d:3d:ef:4c:a4:55:ec:33:aa:d0",
                    __Infrary__IP="46.101.40.221", __Infrary__ID=1)
            ],
            "provisioning": [],
            "email": "c",
            "hash": "$2a$12$krm6imEScXbJGF7zWJcIiesWvR1d2o5HpGtO9EjMw7GCUJvtv6gPa",
            "createdAt": creation_date_time,
        }, does_exist
    response_text, response_code = logic.Server.get(provider, server_id, user_id)
    assert response_code == expected_code
    if expected_code != 400:
        # noinspection PyUnresolvedReferences
        logic.db.find_one_if_exists.assert_called_once_with({'_id': ObjectId(user_id)}, db_name="users")
    if expected_code == 200:
        # noinspection PyUnresolvedReferences
        logic.jsonify.assert_called_once_with(dict(
            __Infrary__VMConfiguration=r"{\"isMaster\": true, \"selfDestruct\": true, \"cmdList\": [\"curl "
                                       r"https://releases.rancher.com/install-docker/17.06.sh | sh\", "
                                       r"\"service ntp stop\", \"update-rc.d -f ntp remove\", \"fallocate -l "
                                       r"4G /swapfile\", \"chmod 600 /swapfile\", \"mkswap /swapfile\", "
                                       r"\"swapon /swapfile\", \"echo \\\"/swapfile   none    swap    sw    0  "
                                       r" 0\\\" >> /etc/fstab\", \"docker run -d --restart=unless-stopped -p "
                                       r"8080:8080 rancher/server\", \"sleep 60\"]}",
            __Infrary__AccessToken="a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6",
            __Infrary__Provider="DO",
            __Infrary__SSHKeyFingerprint="92:6e:45:ba:a8:a0:7d:3d:ef:4c:a4:55:ec:33:aa:d0",
            __Infrary__IP="46.101.40.221", __Infrary__ID=1))
    else:
        # noinspection PyUnresolvedReferences
        assert not logic.jsonify.called


# As it turns out, delete method is quite complex and so is testing it -_- . Please refer to the documentation.
# TLDR: It's behavior when server exists in servers or provisioning or both or none has to be tested
#       and the amount and type of calls can wildly differ based on the above.
# noinspection SpellCheckingInspection
@pytest.mark.parametrize("does_exist, is_in_servers, is_in_provisioning, user_id, server_id, provider," +
                         "force_delete, expected_code",
                         [  # I am terribly sorry...
                             # Different servers with the same prov,id not tested as "this will never happen"
                             # UPDATE: Actually this CANNOT happen as if prov, id are different it wont be found
                             # #wontfix
                             (True, True, False, "5a42c63d4430602278d0a7ca", 1, "DO", False, 200),  # Valid
                             (False, True, False, "5a42c63d4430602278d0a7ca", 1, "DO", False, 500),  # DB:User not found
                             (True, True, False, "5a42c63d4430602278d0a7c", 1, "DO", False, 400),  # invalid userID form
                             (True, True, True, "5a42c63d4430602278d0a7ca", 1, "DO", False, 200),  # in both lists
                             (True, True, True, "5a42c63d4430602278d0a7ca", 1, "DO", True, 200),  # in both lists, force
                             (True, False, True, "5a42c63d4430602278d0a7ca", 1, "DO", False, 404),  # in prov. no force
                             (True, True, True, "5a42c63d4430602278d0a7ca", 1, "DO", True, 200),  # in prov. force
                             (True, True, False, "5a42c63d4430602278d0a7ca", 2, "DO", False, 404),  # Invalid serverID
                             (True, True, False, "5a42c63d4430602278d0a7ca", 1, "DOO", False, 404),  # Invalid prov

                         ])
def test_server_delete(mocker, does_exist, is_in_servers, is_in_provisioning, user_id, server_id, provider,
                       force_delete, expected_code):
    mocker.patch('logic.db.find_one_if_exists')
    mocker.patch('logic.db.remove_from_list_param')
    mocker.patch('logic.launch_container')
    logic.launch_container.return_value = "204 Very nice!"
    creation_date_time = datetime.datetime.utcnow()

    user_dict = dict(id="5a42c63d4430602278d0a7ca", firstName="a", lastName="b", servers=[], provisioning=[], email="c",
                     hash="$2a$12$krm6imEScXbJGF7zWJcIiesWvR1d2o5HpGtO9EjMw7GCUJvtv6gPa", createdAt=creation_date_time)
    server_dict = dict(
        __Infrary__VMConfiguration=r"{\"isMaster\": true, \"selfDestruct\": true, \"cmdList\": [\"curl "
                                   r"https://releases.rancher.com/install-docker/17.06.sh | sh\", \"service ntp "
                                   r"stop\", \"update-rc.d -f ntp remove\", \"fallocate -l 4G /swapfile\", "
                                   r"\"chmod 600 /swapfile\", \"mkswap /swapfile\", \"swapon /swapfile\", "
                                   r"\"echo \\\"/swapfile   none    swap    sw    0   0\\\" >> /etc/fstab\", "
                                   r"\"docker run -d --restart=unless-stopped -p 8080:8080 rancher/server\", "
                                   r"\"sleep 60\"]}",
        __Infrary__AccessToken="a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6",
        __Infrary__Provider="DO", __Infrary__SSHKeyFingerprint="92:6e:45:ba:a8:a0:7d:3d:ef:4c:a4:55:ec:33:aa:d0",
        __Infrary__IP="46.101.40.221", __Infrary__ID=1)

    if is_in_servers:
        user_dict["servers"].append(server_dict)
    if is_in_provisioning:
        user_dict["provisioning"].append(server_dict)

    logic.db.find_one_if_exists.return_value = user_dict, does_exist

    response_text, response_code = logic.Server.delete(provider, server_id, force_delete, user_id, "")

    assert response_code == expected_code

    if not expected_code == 400:
        # noinspection PyUnresolvedReferences
        logic.db.find_one_if_exists.assert_called_once_with({'_id': ObjectId(user_id)}, "users")

    if expected_code not in [400, 404, 500] and not (is_in_servers and is_in_provisioning and force_delete):
        # noinspection PyUnresolvedReferences
        logic.launch_container.assert_called_once_with('provisioner', 'destroy', "",
                                                       {'SERVER_ID': server_id, 'SERVER_PROVIDER': provider,
                                                        'ACCESS_TOKEN': server_dict['__Infrary__AccessToken']})

    if expected_code not in [400, 404, 500] and (is_in_servers and is_in_provisioning and force_delete):
        # noinspection PyUnresolvedReferences
        logic.launch_container.assert_has_calls([call('provisioner', 'destroy', "",
                                                      {'SERVER_ID': server_id, 'SERVER_PROVIDER': provider,
                                                       'ACCESS_TOKEN': server_dict['__Infrary__AccessToken']}),
                                                 call('provisioner', 'destroy', "",
                                                      {'SERVER_ID': server_id, 'SERVER_PROVIDER': provider,
                                                       'ACCESS_TOKEN': server_dict['__Infrary__AccessToken']})
                                                 ])
    if expected_code == 200:
        if is_in_provisioning and is_in_servers and force_delete:
            # noinspection PyUnresolvedReferences
            logic.db.remove_from_list_param.assert_has_calls([
                call({"_id": ObjectId(user_id)}, "servers",
                     {"__Infrary__ID": server_id, "__Infrary__Provider": provider},
                     db_name="users"),
                call({"_id": ObjectId(user_id)}, "provisioning",
                     {"__Infrary__ID": server_id,
                      "__Infrary__Provider": provider},
                     db_name="users")])
        elif is_in_servers:
            # noinspection PyUnresolvedReferences
            logic.db.remove_from_list_param.assert_called_once_with({"_id": ObjectId(user_id)}, "servers",
                                                                    {"__Infrary__ID": server_id,
                                                                     "__Infrary__Provider": provider},
                                                                    db_name="users")
        elif is_in_provisioning:
            # noinspection PyUnresolvedReferences
            logic.db.remove_from_list_param.assert_called_once_with({"_id": ObjectId(user_id)}, "provisioning",
                                                                    {"__Infrary__ID": server_id,
                                                                     "__Infrary__Provider": provider},
                                                                    db_name="users")
    else:
        # noinspection PyUnresolvedReferences
        assert not logic.db.remove_from_list_param.called


# noinspection SpellCheckingInspection
SERVER_PROPERTIES = dict(SERVER_PROVIDER="DO",
                         ACCESS_TOKEN="a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6",
                         SERVER_NAME="Infrary", SERVER_SIZE="512mb", SERVER_IMAGE="ubuntu-14-04-x64",
                         SERVER_LOCATION="lon1",
                         SSH_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3KVkFiPI"
                                 "+5RlTiTKsRkjEZr6ssjYFw9Tk0dzoLKYQH8NOWA13tpSo8r6wT7P"
                                 "+yxXG631wGSBfHyarCpuNO8X2sS7y1zWFVIiDvp1cT4sKGF3kfMPjmt5vrfrp"
                                 "+qEzxHDG9oQqCvnYv1NnhIsb+ZgLG+S56z7ssEx+CPpbUU2RE+27/RYxRNjSZQ7l3eNiQyyvBlPBnK"
                                 "+RK6uccUJhG8KfqWB1hOtlJ7H71Mx0RwiLA6as7OK5PuwqkCN5JhzJs48mRjtRE86R0VwKwny"
                                 "/LuPmTMyyz7JCg38C4PDgEXIJrAfuo/TJDcqiJnxPeX4+neDnmXEeVvUqMUnbVNlk8qZ+w==")

VM_CONFIGURATION = dict(isMaster=True, selfDestruct=True,
                        cmdList=["curl https://releases.rancher.com/install-docker/17.06.sh | sh", "service ntp stop",
                                 "update-rc.d -f ntp remove", "fallocate -l 4G /swapfile", "chmod 600 /swapfile",
                                 "mkswap /swapfile", "swapon /swapfile",
                                 "echo \"/swapfile   none    swap    sw    0   0\" >> /etc/fstab",
                                 "docker run -d --restart=unless-stopped -p 8080:8080 rancher/server", "sleep 60"])


@pytest.mark.parametrize("server_properties, vm_configuration, expected_code",
                         [
                             (SERVER_PROPERTIES, VM_CONFIGURATION, 200),  # Valid
                         ])
def test_server_create(mocker, server_properties, vm_configuration, expected_code):
    mocker.patch('logic.launch_container')

    return_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(125))

    logic.launch_container.return_value = return_str

    response_text, response_code = logic.Server.create(server_properties, vm_configuration, "")

    assert response_code == expected_code
    assert response_text == return_str
    # noinspection PyUnresolvedReferences
    logic.launch_container.assert_called_once_with('provisioner', 'create', "", server_properties)


@pytest.mark.parametrize("user_id, expected_code",
                         [
                             ("5a42c63d4430602278d0a7ca", 200),
                             ("5a42c63d4430602278d0a7c", 400),
                         ])
def test_server_configure(mocker, user_id, expected_code):
    vm_configuration = str(VM_CONFIGURATION)
    server_id = 1
    server_provider = "DO"
    server_hostname = "127.0.0.1"
    temp_key = "AA:vv:3r:f4:43:34:34:r3:2r:2r"
    server_dict = {"foo": "bar", '__Infrary__TempSSHKey': "fake"}

    mocker.patch('logic.launch_container')
    mocker.patch('logic.db.add_to_list_param')

    return_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(125))

    logic.launch_container.return_value = return_str  # This is not realistic behaviour todo

    response_text, response_code = logic.Server.configure(server_dict.copy(), temp_key, server_hostname,
                                                          server_provider, server_id, vm_configuration, user_id, "")

    server_dict.pop("__Infrary__TempSSHKey")

    assert response_code == expected_code

    if expected_code == 200:
        assert response_text == return_str
        # noinspection PyUnresolvedReferences
        logic.db.add_to_list_param.assert_called_once_with({'_id': ObjectId(user_id)}, "provisioning", server_dict,
                                                           db_name="users")
        octo_conf = json.dumps(
            dict(
                serverHostname=server_hostname, octoToken="", serverProvider=server_provider, serverID=server_id
            )).replace('"', '\\"')  # todo ITSINTHEVArgs

        vm_configuration = vm_configuration.replace(r'"', r'\"').replace(r'\\', '\\\\\\')

        # noinspection PyUnresolvedReferences
        logic.launch_container.assert_called_once_with('vmconf',
                                                       '"{}" "{}" "{}"'.format(temp_key, octo_conf, vm_configuration),
                                                       "", detach=True)


@pytest.mark.parametrize("does_exist, user_dict, user_id, is_master, is_self_destruct, master_conf, expected_code",
                         [
                             (True, dict(_id="5a42c63d4830602278d0a7ca", firstName="a", lastName="b", servers=[],
                                         email="c", hash=hash, createdAt="fake",
                                         provisioning=[dict(
                                             __Infrary__ID=1, __Infrary__Provider="DO"
                                         )]),
                              "5a42c63d4430602278d0a7ca", False, False, {}, 200),
                             (True, dict(_id="5a42c63d4830602278d0a7c", firstName="a", lastName="b", servers=[],
                                         email="c", hash=hash, createdAt="fake",
                                         provisioning=[dict(
                                             __Infrary__ID=1, __Infrary__Provider="DO"
                                         )]),
                              "5a42c63d4430602278d0a7c", False, False, {}, 400),
                             (False, dict(_id="5a42c63d4830602278d0a7ca", firstName="a", lastName="b", servers=[],
                                          email="c", hash=hash, createdAt="fake",
                                          provisioning=[dict(
                                              __Infrary__ID=1, __Infrary__Provider="DO"
                                          )]),
                              "5a42c63d4430602278d0a7ca", False, False, {}, 500),
                             (True, dict(_id="5a42c63d4830602278d0a7ca", firstName="a", lastName="b", servers=[],
                                         email="c", hash=hash, createdAt="fake",
                                         provisioning=[dict(
                                             __Infrary__ID=1, __Infrary__Provider="DO"
                                         ),
                                             dict(
                                                 __Infrary__ID=1, __Infrary__Provider="DO"
                                             )
                                         ]),
                              "5a42c63d4430602278d0a7ca", False, False, {}, 500),
                         ])
def test_server_initialise(mocker, does_exist, user_dict, user_id, is_master, is_self_destruct, master_conf,
                           expected_code):
    server_id = 1
    server_provider = "DO"

    mocker.patch('logic.launch_container')
    mocker.patch('logic.db.add_to_list_param')
    mocker.patch('logic.db.remove_from_list_param')
    mocker.patch('logic.db.find_one_if_exists')
    mocker.patch('logic.Server.delete')
    mocker.patch('logic.Server.get')
    logic.Server.get.return_value = "test"
    logic.db.find_one_if_exists.return_value = user_dict, does_exist

    response_text, response_code = logic.Server.initialise(server_id, server_provider, user_id, "", is_master,
                                                           is_self_destruct, master_conf)

    assert response_code == expected_code

    if not expected_code == 400:
        # noinspection PyUnresolvedReferences
        logic.db.find_one_if_exists.assert_called_once_with({'_id': ObjectId(user_id)}, "users")

    if expected_code == 200:
        assert response_text == "test"
        # noinspection PyUnresolvedReferences
        logic.db.remove_from_list_param.assert_called_once_with({"_id": ObjectId(user_id)}, "provisioning", {
            "__Infrary__ID": server_id,
            "__Infrary__Provider": server_provider
        }, db_name="users")

        if not is_master:
            cur_server = dict(__Infrary__ID=1, __Infrary__Provider="DO")
            cur_server['__Infrary__IsMaster'] = False
        else:
            cur_server = dict(__Infrary__ID=1, __Infrary__Provider="DO")
            cur_server['__Infrary__IsMaster'] = True
            cur_server['__Infrary__MasterConf'] = master_conf

        # noinspection PyUnresolvedReferences
        logic.db.add_to_list_param.assert_called_once_with({"_id": ObjectId(user_id)}, "servers", cur_server,
                                                           db_name="users")

        # noinspection PyUnresolvedReferences
        logic.Server.get.assert_called_once_with(server_provider, server_id, user_id)

        if is_self_destruct:
            # noinspection PyUnresolvedReferences
            logic.Server.delete.assert_called_once_with(server_provider, server_id, True, user_id, "")
        else:
            # noinspection PyUnresolvedReferences
            assert not logic.Server.delete.called
    else:
        # noinspection PyUnresolvedReferences
        assert not logic.Server.delete.called
        # noinspection PyUnresolvedReferences
        assert not logic.Server.get.called
        # noinspection PyUnresolvedReferences
        assert not logic.db.add_to_list_param.called
        # noinspection PyUnresolvedReferences
        assert not logic.db.remove_from_list_param.called


# noinspection SpellCheckingInspection
@pytest.mark.parametrize("does_exist, user_id, num_servers, expected_code",
                         [
                             (True, "5a42c63d4430602278d0a7ca", 1, 200),
                             (True, "5a42c63d4430602278d0a7ca", 0, 200),
                             (True, "5a42c63d4430602278d0a7ca", 2, 200),
                             (True, "5a42c63d4430602278d0a7ca", 3145, 200),
                             (True, "5a42c63d4430602278d0a7c", 1, 400),
                             (False, "5a42c63d4430602278d0a7ca", 1, 500),

                         ])
def test_servers_list(mocker, does_exist, user_id, num_servers, expected_code):
    mocker.patch('logic.db.find_one_if_exists')
    mocker.patch('logic.jsonify',
                 side_effect=mock_jsonify)  # werkzeug does not like all the logic.py, db.py, api.py shenanigans
    creation_date_time = datetime.datetime.utcnow()
    server_dict = dict(
        __Infrary__VMConfiguration=r"{\"isMaster\": true, \"selfDestruct\": true, \"cmdList\": [\"curl "
                                   r"https://releases.rancher.com/install-docker/17.06.sh | sh\", "
                                   r"\"service ntp stop\", \"update-rc.d -f ntp remove\", \"fallocate -l "
                                   r"4G /swapfile\", \"chmod 600 /swapfile\", \"mkswap /swapfile\", "
                                   r"\"swapon /swapfile\", \"echo \\\"/swapfile   none    swap    sw    0  "
                                   r" 0\\\" >> /etc/fstab\", \"docker run -d --restart=unless-stopped -p "
                                   r"8080:8080 rancher/server\", \"sleep 60\"]}",
        __Infrary__AccessToken="a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6",
        __Infrary__Provider="DO",
        __Infrary__SSHKeyFingerprint="92:6e:45:ba:a8:a0:7d:3d:ef:4c:a4:55:ec:33:aa:d0",
        __Infrary__IP="46.101.40.221", __Infrary__ID=1
    )
    user_dict = {
        "id": user_id,
        "firstName": "a",
        "lastName": "b",
        "servers": [],
        "provisioning": [],
        "email": "c",
        "hash": "$2a$12$krm6imEScXbJGF7zWJcIiesWvR1d2o5HpGtO9EjMw7GCUJvtv6gPa",
        "createdAt": creation_date_time,
    }
    for i in range(num_servers):
        user_dict["servers"].append(server_dict)
    logic.db.find_one_if_exists.return_value = user_dict, does_exist
    response_text, response_code = logic.Servers.list(user_id)
    assert response_code == expected_code
    if expected_code != 400:
        # noinspection PyUnresolvedReferences
        logic.db.find_one_if_exists.assert_called_once_with({'_id': ObjectId(user_id)}, db_name="users")
    else:
        # noinspection PyUnresolvedReferences
        assert not logic.db.find_one_if_exists.called
    if expected_code == 200:
        assert response_text == json.dumps(user_dict["servers"])
        # noinspection PyUnresolvedReferences
        logic.jsonify.assert_called_once_with(user_dict["servers"])
    else:
        # noinspection PyUnresolvedReferences
        assert not logic.jsonify.called
