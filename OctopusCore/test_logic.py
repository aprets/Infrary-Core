from conftest import *
import logic
import time
import datetime
import jwt
from bson.objectid import ObjectId
import pytest
from mock import call

from constants import *


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
                             (True, 201)

                         ])
def test_user_register(mocker, does_exist, expected_code):
    mocker.patch('logic.db.mongo_db.exists_once_or_not')
    mocker.patch("logic.db.mongo_db.create_document")
    mocker.patch('logic.send_sendgrid_email_key_email')
    logic.db.mongo_db.exists_once_or_not.return_value = does_exist
    logic.send_sendgrid_email_key_email.return_value = MockSendGridResponse()
    response_text, response_code = logic.User.register("a", "b", "c", "d")
    assert response_code == expected_code
    if does_exist:
        # noinspection PyUnresolvedReferences,PyUnresolvedReferences
        assert (2 == logic.db.mongo_db.exists_once_or_not.call_count or 1 == logic.db.mongo_db.exists_once_or_not.call_count)
        # noinspection PyUnresolvedReferences
        assert not logic.db.mongo_db.create_document.called
    else:
        # noinspection PyUnresolvedReferences
        logic.db.mongo_db.exists_once_or_not.assert_has_calls([call({EMAIL_KEY: "c"}, USERS_COLLECTION_NAME),
                                                      call({EMAIL_KEY: "c"}, TMP_USERS_COLLECTION_NAME)])
        # noinspection PyUnresolvedReferences
        logic.db.mongo_db.create_document.assert_called_once_with({
            FIRST_NAME_KEY: "a",
            LAST_NAME_KEY: "b",
            EMAIL_KEY: "c",
            HASH_KEY: mocker.ANY,
            EMAIL_KEY_KEY: mocker.ANY,
            CREATED_AT_KEY: mocker.ANY,
        }, TMP_USERS_COLLECTION_NAME)
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
    mocker.patch('logic.db.mongo_db.find_one_if_exists')
    mocker.patch("logic.db.mongo_db.create_document")
    mocker.patch('logic.db.mongo_db.delete_one_document')
    creation_date_time = datetime.datetime.utcnow()
    logic.db.mongo_db.find_one_if_exists.return_value = \
        {
            FIRST_NAME_KEY: "a",
            LAST_NAME_KEY: "b",
            EMAIL_KEY: "c",
            HASH_KEY: "$2b$12$kWmswlgA/X50JCOkozD0Z.86v.iR4/909u/VGNH0CV3SVSFkGiEWm",
            EMAIL_KEY_KEY: "879rh4t98ty98hHUHIU8989h98hh8h89huihIUYHUYIUIUI78yh78y89h89hh",
            CREATED_AT_KEY: creation_date_time,
        }, does_exist
    response_text, response_code = logic.User.verify("879rh4t98ty98hHUHIU8989h98hh8h89huihIUYHUYIUIUI78yh78y89h89hh")
    assert response_code == expected_code
    # noinspection PyUnresolvedReferences
    logic.db.mongo_db.find_one_if_exists.assert_called_once_with({
        EMAIL_KEY_KEY: "879rh4t98ty98hHUHIU8989h98hh8h89huihIUYHUYIUIUI78yh78y89h89hh"
    }, TMP_USERS_COLLECTION_NAME)
    if does_exist:
        # noinspection PyUnresolvedReferences
        logic.db.mongo_db.delete_one_document.assert_called_once_with({
            EMAIL_KEY_KEY: "879rh4t98ty98hHUHIU8989h98hh8h89huihIUYHUYIUIUI78yh78y89h89hh"
        }, TMP_USERS_COLLECTION_NAME)
        # noinspection PyUnresolvedReferences
        logic.db.mongo_db.create_document.assert_called_once_with({
            FIRST_NAME_KEY: "a",
            LAST_NAME_KEY: "b",
            SERVERS_KEY: [],
            EMAIL_KEY: "c",
            HASH_KEY: "$2b$12$kWmswlgA/X50JCOkozD0Z.86v.iR4/909u/VGNH0CV3SVSFkGiEWm",
            CREATED_AT_KEY: creation_date_time,
        }, USERS_COLLECTION_NAME)
    else:
        # noinspection PyUnresolvedReferences
        assert not logic.db.mongo_db.delete_one_document.called
        # noinspection PyUnresolvedReferences
        assert not logic.db.mongo_db.create_document.called


# noinspection PyUnboundLocalVariable,SpellCheckingInspection
@pytest.mark.parametrize("does_exist, pw_hash, pw, expected_code",
                         [
                             (True, "$2a$12$krm6imEScXbJGF7zWJcIiesWvR1d2o5HpGtO9EjMw7GCUJvtv6gPa", "d", 200),
                             (False, "$2a$12$krm6imEScXbJGF7zWJcIiesWvR1d2o5HpGtO9EjMw7GCUJvtv6gPa", "d", 400),
                             (True, "sad", "d", 500),
                             (True, "$2a$12$krm6imEScXbJGF7zWJcIiesWvR1d2o5HpGtO9EjMw7GCUJvtv6gPa", "dd", 400),

                         ])
def test_user_login(mocker, does_exist, pw_hash, pw, expected_code):
    mocker.patch('logic.db.mongo_db.find_one_if_exists')
    creation_date_time = datetime.datetime.utcnow()
    logic.db.mongo_db.find_one_if_exists.return_value = {
                                                   DB_ID_KEY: "5a42c63d4830602278d0a7ca",
                                                   FIRST_NAME_KEY: "a",
                                                   LAST_NAME_KEY: "b",
                                                   SERVERS_KEY: [],
                                                   EMAIL_KEY: "c",
                                                   HASH_KEY: pw_hash,
                                                   CREATED_AT_KEY: creation_date_time,
                                               }, does_exist
    response_text, response_code = logic.User.login("c", pw)
    assert response_code == expected_code
    # noinspection PyUnresolvedReferences
    logic.db.mongo_db.find_one_if_exists.assert_called_once_with({EMAIL_KEY: "c"}, USERS_COLLECTION_NAME)
    if expected_code == 200:
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


# noinspection SpellCheckingInspection
@pytest.mark.parametrize("does_exist, provider, server_id, user_id, expected_code",
                         [
                             (True, "DO", 1, "5a42c63d4430602278d0a7ca", 200),
                             (True, "DO", 1, "5a42c63d4430602278d0a7c", 400),
                             (False, "DO", 1, "5a42c63d4430602278d0a7ca", 404)

                         ])
def test_server_get(mocker, does_exist, provider, server_id, user_id, expected_code):
    mocker.patch('logic.db.mongo_db.find_one_if_exists')
    mocker.patch('logic.jsonify',
                 side_effect=mock_jsonify)  # werkzeug does not like all the logic.py, db.py, api.py shenanigans
    creation_date_time = "TEST"
    logic.db.mongo_db.find_one_if_exists.return_value = \
        {
            "id": user_id,
            FIRST_NAME_KEY: "a",
            LAST_NAME_KEY: "b",
            SERVERS_KEY: [
                {VM_CONFIGURATION_EXP_KEY: "TEST",
                 ACCESS_TOKEN_EXP_KEY: "a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6",
                 PROVIDER_EXP_KEY: "DO",
                 SSH_KEY_FINGERPRINT_EXP_KEY: "92:6e:45:ba:a8:a0:7d:3d:ef:4c:a4:55:ec:33:aa:d0",
                 IP_EXP_KEY: "46.101.40.221", ID_EXP_KEY: 1}
            ],
            EMAIL_KEY: "c",
            HASH_KEY: "$2a$12$krm6imEScXbJGF7zWJcIiesWvR1d2o5HpGtO9EjMw7GCUJvtv6gPa",
            CREATED_AT_KEY: creation_date_time,
        }, does_exist
    response_text, response_code = logic.Server.get(provider, server_id, user_id)
    assert response_code == expected_code
    if expected_code != 400:
        # noinspection PyUnresolvedReferences
        logic.db.mongo_db.find_one_if_exists.assert_called_once_with({DB_ID_KEY: ObjectId(user_id), SERVERS_KEY: {
                '$elemMatch': {
                    ID_EXP_KEY: server_id, PROVIDER_EXP_KEY: provider
                }
        }
                                                                      }, USERS_COLLECTION_NAME)
    if expected_code == 200:
        # noinspection PyUnresolvedReferences
        logic.jsonify.assert_called_once_with(
            {VM_CONFIGURATION_EXP_KEY: "TEST",
             ACCESS_TOKEN_EXP_KEY: "a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6",
             PROVIDER_EXP_KEY: "DO",
             SSH_KEY_FINGERPRINT_EXP_KEY: "92:6e:45:ba:a8:a0:7d:3d:ef:4c:a4:55:ec:33:aa:d0",
             IP_EXP_KEY: "46.101.40.221", ID_EXP_KEY: 1})
    else:
        # noinspection PyUnresolvedReferences
        assert not logic.jsonify.called


# As it turns out, delete method is quite complex and so is testing it -_- . Please refer to the documentation.
# TLDR: It's behavior when server exists in servers or provisioning or both or none has to be tested
#       and the amount and type of calls can wildly differ based on the above.
# UPDATE: More sane server storage was implemented where all servers are in db.SERVER_KEY and have db.SERVER_KEY.$.STATUS_EXP_KEY
# This negates a lot of complexity in this test
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
                             (True, True, True, "5a42c63d4430602278d0a7ca", 1, "DO", False, 500),  # in both lists
                             (True, True, True, "5a42c63d4430602278d0a7ca", 1, "DO", True, 500),  # in both lists, force
                             (True, False, True, "5a42c63d4430602278d0a7ca", 1, "DO", False, 400),  # in prov. no force
                             (True, True, True, "5a42c63d4430602278d0a7ca", 1, "DO", True, 500),  # in prov. force
                             (True, True, False, "5a42c63d4430602278d0a7ca", 2, "DO", False, 404),  # Invalid serverID
                             (True, True, False, "5a42c63d4430602278d0a7ca", 1, "DOO", False, 404),  # Invalid prov

                         ])
def test_server_delete(mocker, does_exist, is_in_servers, is_in_provisioning, user_id, server_id, provider,
                       force_delete, expected_code):
    mocker.patch('logic.db.mongo_db.find_one_if_exists')
    mocker.patch('logic.db.mongo_db.remove_from_list_param')
    mocker.patch('logic.launch_container')
    logic.launch_container.return_value = "204 Very nice!"
    creation_date_time = datetime.datetime.utcnow()

    user_dict = {'id': "5a42c63d4430602278d0a7ca", FIRST_NAME_KEY: "a", LAST_NAME_KEY: "b", SERVERS_KEY: [], 'provisioning': [],
                 EMAIL_KEY: "c", HASH_KEY: "$2a$12$krm6imEScXbJGF7zWJcIiesWvR1d2o5HpGtO9EjMw7GCUJvtv6gPa",
                 CREATED_AT_KEY: creation_date_time}
    server_dict = {VM_CONFIGURATION_EXP_KEY: "TEST",
                   ACCESS_TOKEN_EXP_KEY: "a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6",
                   PROVIDER_EXP_KEY: "DO",
                   STATUS_EXP_KEY: UP_STATUS,
                   SSH_KEY_FINGERPRINT_EXP_KEY: "92:6e:45:ba:a8:a0:7d:3d:ef:4c:a4:55:ec:33:aa:d0",
                   IP_EXP_KEY: "46.101.40.221", ID_EXP_KEY: 1}
    server_bad_dict = server_dict.copy()
    server_bad_dict[STATUS_EXP_KEY] = CONFIGURING_STATUS

    if is_in_servers:
        user_dict[SERVERS_KEY].append(server_dict)
    if is_in_provisioning:
        user_dict[SERVERS_KEY].append(server_bad_dict)

    logic.db.mongo_db.find_one_if_exists.return_value = user_dict, does_exist

    response_text, response_code = logic.Server.delete(provider, server_id, force_delete, user_id, "")

    assert response_code == expected_code

    if not expected_code == 400:
        # noinspection PyUnresolvedReferences
        logic.db.mongo_db.find_one_if_exists.assert_called_once_with({DB_ID_KEY: ObjectId(user_id)}, USERS_COLLECTION_NAME)

    if expected_code not in [400, 404, 500] and not (is_in_servers and is_in_provisioning and force_delete):
        # noinspection PyUnresolvedReferences
        logic.launch_container.assert_called_once_with(PROVISIONER_CONTAINER_NAME, 'destroy', "",
                                                       {'SERVER_ID': server_id, 'SERVER_PROVIDER': provider,
                                                        'ACCESS_TOKEN': server_dict[ACCESS_TOKEN_EXP_KEY]})

    if expected_code not in [400, 404, 500] and (is_in_servers and is_in_provisioning and force_delete):
        # noinspection PyUnresolvedReferences
        logic.launch_container.assert_has_calls([call(PROVISIONER_CONTAINER_NAME, 'destroy', "",
                                                      {'SERVER_ID': server_id, 'SERVER_PROVIDER': provider,
                                                       'ACCESS_TOKEN': server_dict[ACCESS_TOKEN_EXP_KEY]}),
                                                 call(PROVISIONER_CONTAINER_NAME, 'destroy', "",
                                                      {'SERVER_ID': server_id, 'SERVER_PROVIDER': provider,
                                                       'ACCESS_TOKEN': server_dict[ACCESS_TOKEN_EXP_KEY]})
                                                 ])
    if expected_code == 200:
        if is_in_provisioning and is_in_servers and force_delete:
            # noinspection PyUnresolvedReferences
            logic.db.mongo_db.remove_from_list_param.assert_has_calls([
                call({DB_ID_KEY: ObjectId(user_id)}, SERVERS_KEY,
                     {ID_EXP_KEY: server_id, PROVIDER_EXP_KEY: provider},
                     USERS_COLLECTION_NAME),
                call({DB_ID_KEY: ObjectId(user_id)}, SERVERS_KEY,
                     {ID_EXP_KEY: server_id,
                      PROVIDER_EXP_KEY: provider},
                     USERS_COLLECTION_NAME)])
        elif is_in_servers:
            # noinspection PyUnresolvedReferences
            logic.db.mongo_db.remove_from_list_param.assert_called_once_with({DB_ID_KEY: ObjectId(user_id)}, SERVERS_KEY,
                                                                    {ID_EXP_KEY: server_id,
                                                                     PROVIDER_EXP_KEY: provider},
                                                                    USERS_COLLECTION_NAME)
        elif is_in_provisioning:
            # noinspection PyUnresolvedReferences
            logic.db.mongo_db.remove_from_list_param.assert_called_once_with({DB_ID_KEY: ObjectId(user_id)}, SERVERS_KEY,
                                                                    {ID_EXP_KEY: server_id,
                                                                     PROVIDER_EXP_KEY: provider},
                                                                    USERS_COLLECTION_NAME)
    else:
        # noinspection PyUnresolvedReferences
        assert not logic.db.mongo_db.remove_from_list_param.called


# noinspection SpellCheckingInspection
SERVER_PROPERTIES = {'SERVER_PROVIDER': "DO",
                     'ACCESS_TOKEN': "a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6",
                     'SERVER_NAME': "Infrary", 'SERVER_SIZE': "512mb", 'SERVER_IMAGE': "ubuntu-14-04-x64",
                     'SERVER_LOCATION': "lon1", 'SSH_KEY': "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3KVkFiPI"
                                                           "+5RlTiTKsRkjEZr6ssjYFw9Tk0dzoLKYQH8NOWA13tpSo8r6wT7P"
                                                           "+yxXG631wGSBfHyarCpuNO8X2sS7y1zWFVIiDvp1cT4sKGF3kfMPjmt5vrfrp"
                                                           "+qEzxHDG9oQqCvnYv1NnhIsb+ZgLG+S56z7ssEx+CPpbUU2RE+27/RYxRNjSZQ7l3eNiQyyvBlPBnK"
                                                           "+RK6uccUJhG8KfqWB1hOtlJ7H71Mx0RwiLA6as7OK5PuwqkCN5JhzJs48mRjtRE86R0VwKwny"
                                                           "/LuPmTMyyz7JCg38C4PDgEXIJrAfuo/TJDcqiJnxPeX4+neDnmXEeVvUqMUnbVNlk8qZ+w=="}

VM_CONFIGURATION = {VMCONF_IS_MASTER_KEY: True, VMCONF_SELF_DESTRUCT_KEY: True,
                    VMCONF_COMMAND_LIST_KEY: []}


@pytest.mark.parametrize("server_properties, vm_configuration, expected_code",
                         [
                             (SERVER_PROPERTIES, VM_CONFIGURATION, 201),  # Valid
                         ])
def test_server_create(mocker, server_properties, vm_configuration, expected_code):
    mocker.patch('logic.launch_container')

    return_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(125))

    logic.launch_container.return_value = return_str

    response_text, response_code = logic.Server.create(server_properties, vm_configuration, "")

    assert response_code == expected_code
    assert response_text == return_str
    # noinspection PyUnresolvedReferences
    logic.launch_container.assert_called_once_with(PROVISIONER_CONTAINER_NAME, PROVISIONER_CREATE_COMMAND, "", server_properties)


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
    server_dict = {"foo": "bar", TEMP_SSH_KEY_EXP_KEY: "fake"}

    mocker.patch('logic.launch_container')
    mocker.patch('logic.db.mongo_db.add_to_list_param')

    return_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(125))

    logic.launch_container.return_value = return_str

    response_text, response_code = logic.Server.configure(server_dict.copy(), temp_key, server_hostname,
                                                          server_provider, server_id, vm_configuration, user_id, "")

    server_dict.pop(TEMP_SSH_KEY_EXP_KEY)
    server_dict[STATUS_EXP_KEY] = CREATED_STATUS

    assert response_code == expected_code

    if expected_code == 200:
        assert response_text == return_str
        # noinspection PyUnresolvedReferences
        logic.db.mongo_db.add_to_list_param.assert_called_once_with({DB_ID_KEY: ObjectId(user_id)}, SERVERS_KEY, server_dict,
                                                           USERS_COLLECTION_NAME)
        octo_conf = json.dumps(
            {VMCONF_SERVER_HOSTNAME_KEY: server_hostname, VMCONF_OCTO_TOKEN_KEY: "", VMCONF_SERVER_PROVIDER_KEY: server_provider,
             VMCONF_SERVER_ID_KEY: server_id}).replace('"', '\\"')  # todo ITSINTHEVArgs

        vm_configuration = vm_configuration.replace(r'"', r'\"').replace(r'\\', '\\\\\\')

        # noinspection PyUnresolvedReferences
        logic.launch_container.assert_called_once_with(VMCONF_CONTAINER_NAME,
                                                       '"{}" "{}" "{}"'.format(temp_key, octo_conf, vm_configuration),
                                                       "", detach=True)


@pytest.mark.parametrize("does_exist, user_dict, user_id, is_master, is_self_destruct, master_conf, expected_code",
                         [
                             (True,
                              {DB_ID_KEY: "5a42c63d4830602278d0a7ca", FIRST_NAME_KEY: "a", LAST_NAME_KEY: "b",
                               EMAIL_KEY: "c", HASH_KEY: hash, CREATED_AT_KEY: "fake", SERVERS_KEY: [
                                  {ID_EXP_KEY: 1, STATUS_EXP_KEY: CONFIGURING_STATUS, PROVIDER_EXP_KEY: "DO"}]},
                              "5a42c63d4430602278d0a7ca", False, False, {}, 200),
                             (True, {DB_ID_KEY: "5a42c63d4830602278d0a7c", FIRST_NAME_KEY: "a", LAST_NAME_KEY: "b",
                                     EMAIL_KEY: "c", HASH_KEY: hash, CREATED_AT_KEY: "fake", SERVERS_KEY: [
                                     {ID_EXP_KEY: 1, STATUS_EXP_KEY: CONFIGURING_STATUS,  PROVIDER_EXP_KEY: "DO"}]},
                              "5a42c63d4430602278d0a7c", False, False, {}, 400),
                             (False,
                              {DB_ID_KEY: "5a42c63d4830602278d0a7ca", FIRST_NAME_KEY: "a", LAST_NAME_KEY: "b",
                               EMAIL_KEY: "c", HASH_KEY: hash, CREATED_AT_KEY: "fake", SERVERS_KEY: [
                                  {ID_EXP_KEY: 1, STATUS_EXP_KEY: CONFIGURING_STATUS, PROVIDER_EXP_KEY: "DO"}]},
                              "5a42c63d4430602278d0a7ca", False, False, {}, 500),
                             (True,
                              {DB_ID_KEY: "5a42c63d4830602278d0a7ca", FIRST_NAME_KEY: "a", LAST_NAME_KEY: "b",
                               EMAIL_KEY: "c", HASH_KEY: hash, CREATED_AT_KEY: "fake", SERVERS_KEY: [
                                  {ID_EXP_KEY: 1, STATUS_EXP_KEY: CONFIGURING_STATUS, PROVIDER_EXP_KEY: "DO"},
                                  {ID_EXP_KEY: 1, STATUS_EXP_KEY: CONFIGURING_STATUS, PROVIDER_EXP_KEY: "DO"}
                                  ]},
                              "5a42c63d4430602278d0a7ca", False, False, {}, 500),
                         ])
def test_server_initialise(mocker, does_exist, user_dict, user_id, is_master, is_self_destruct, master_conf,
                           expected_code):
    server_id = 1
    server_provider = "DO"

    mocker.patch('logic.launch_container')
    mocker.patch('logic.db.mongo_db.update_one_document_values')
    mocker.patch('logic.db.mongo_db.find_one_if_exists')
    mocker.patch('logic.Server.get')
    mocker.patch('logic.Server.delete')
    logic.Server.get.return_value = "test", 200
    logic.db.mongo_db.find_one_if_exists.return_value = user_dict, does_exist

    response_text, response_code = logic.Server.initialise(server_id, server_provider, user_id, "", is_master,
                                                           is_self_destruct, master_conf)

    assert response_code == expected_code

    if not expected_code == 400:
        # noinspection PyUnresolvedReferences
        logic.db.mongo_db.find_one_if_exists.assert_called_once_with({DB_ID_KEY: ObjectId(user_id)}, USERS_COLLECTION_NAME)

    if expected_code == 200:
        assert response_text == "test"

        if not is_master:
            cur_server = {IS_MASTER_EXP_KEY: False}
        else:
            cur_server = {IS_MASTER_EXP_KEY: True,
                          MASTERCONF_EXP_KEY: master_conf}

        cur_server[STATUS_EXP_KEY] = UP_STATUS

        # noinspection PyUnresolvedReferences
        logic.db.mongo_db.update_one_document_values.assert_called_once_with({
            DB_ID_KEY: user_id,
            SERVERS_KEY: {
                '$elemMatch': {
                    ID_EXP_KEY: server_id, PROVIDER_EXP_KEY: server_provider
                }
            }
        },
            cur_server, USERS_COLLECTION_NAME, create_if_nonexistent=True)

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
        assert not logic.db.mongo_db.update_one_document_values.called


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
    mocker.patch('logic.db.mongo_db.find_one_if_exists')
    mocker.patch('logic.jsonify',
                 side_effect=mock_jsonify)  # werkzeug does not like all the logic.py, db.py, api.py shenanigans
    creation_date_time = datetime.datetime.utcnow()
    server_dict = {VM_CONFIGURATION_EXP_KEY: "TEST",
                   ACCESS_TOKEN_EXP_KEY: "a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6",
                   PROVIDER_EXP_KEY: "DO",
                   SSH_KEY_FINGERPRINT_EXP_KEY: "92:6e:45:ba:a8:a0:7d:3d:ef:4c:a4:55:ec:33:aa:d0",
                   IP_EXP_KEY: "46.101.40.221", ID_EXP_KEY: 1}
    user_dict = {
        "id": user_id,
        FIRST_NAME_KEY: "a",
        LAST_NAME_KEY: "b",
        SERVERS_KEY: [],
        EMAIL_KEY: "c",
        HASH_KEY: "$2a$12$krm6imEScXbJGF7zWJcIiesWvR1d2o5HpGtO9EjMw7GCUJvtv6gPa",
        CREATED_AT_KEY: creation_date_time,
    }
    for i in range(num_servers):
        user_dict[SERVERS_KEY].append(server_dict)
    logic.db.mongo_db.find_one_if_exists.return_value = user_dict, does_exist
    response_text, response_code = logic.Servers.list(user_id)
    assert response_code == expected_code
    if expected_code != 400:
        # noinspection PyUnresolvedReferences
        logic.db.mongo_db.find_one_if_exists.assert_called_once_with({DB_ID_KEY: ObjectId(user_id)}, USERS_COLLECTION_NAME)
    else:
        # noinspection PyUnresolvedReferences
        assert not logic.db.mongo_db.find_one_if_exists.called
    if expected_code == 200:
        assert response_text == json.dumps(user_dict[SERVERS_KEY])
        # noinspection PyUnresolvedReferences
        logic.jsonify.assert_called_once_with(user_dict[SERVERS_KEY])
    else:
        # noinspection PyUnresolvedReferences
        assert not logic.jsonify.called
