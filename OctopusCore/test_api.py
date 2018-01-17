from flask import url_for
from conftest import *
from constants import *


#
# This is a test written with pytest and additional autogen_tests extension in conftest.py
# please refer to docs for explanation of how everything works (and how pytest is used here)
#


# noinspection PyDecorator,PyUnusedLocal
@staticmethod  # Yes, this is supposed to be here. This is a function to mock a @staticmethod in logic.py
def i_always_say_200(*args, **kwargs):
    return "This is very fake", 200


# noinspection PyShadowingNames
def test_auth(client, auth_headers):
    assert client.get(url_for('list_servers')).status_code == 401
    assert client.get(url_for('list_servers'), headers=auth_headers).status_code == 200


@pytest.mark.parametrize("input_data, expected_code",
                         [
                             (json.dumps({FIRST_NAME_KEY: "a", LAST_NAME_KEY: "b", EMAIL_KEY: "d", PASSWORD_KEY: "c"}),
                              200)
                         ] + autogen_tests(
                             (
                                     {FIRST_NAME_KEY: [get_everything_but_not_empty_string_list(), "a"],
                                      LAST_NAME_KEY: [get_everything_but_not_empty_string_list(), "b"],
                                      EMAIL_KEY: [get_everything_but_not_empty_string_list(), "a@b.c"],
                                      PASSWORD_KEY: [get_everything_but_not_empty_string_list(), "a"]}
                                     , 400)
                         ))
def test_register_input_filtering(monkeypatch, client, input_data, expected_code):
    monkeypatch.setattr('logic.User.register', i_always_say_200)

    assert client.post(url_for('register'), content_type='application/json',
                       data=input_data).status_code == expected_code


# noinspection SpellCheckingInspection
@pytest.mark.parametrize("input_data, expected_code",
                         [
                             (json.dumps({EMAIL_KEY_KEY: "aw34tuya4ADF"}), 200),
                             ('', 400)
                         ] + autogen_tests(
                             (
                                     {EMAIL_KEY_KEY: [[get_int(), get_float(), "", 0, 0.0, {}, []], "aw34tuya4ADF"]}
                                     , 400)
                         ))
def test_verify_input_filtering(monkeypatch, client, input_data, expected_code):
    monkeypatch.setattr('logic.User.verify', i_always_say_200)

    assert client.post(url_for('verify'), content_type='application/json',
                       data=input_data).status_code == expected_code


@pytest.mark.parametrize("input_data, expected_code",
                         [
                             (json.dumps({EMAIL_KEY: "a", PASSWORD_KEY: "b"}), 200),
                             ('', 400)
                         ] + autogen_tests(
                             (
                                     {EMAIL_KEY: [get_everything_but_not_empty_string_list(), "a@b.c"],
                                      PASSWORD_KEY: [get_everything_but_not_empty_string_list(), "a"]}
                                     , 400)
                         ))
def test_login_input_filtering(monkeypatch, client, input_data, expected_code):
    monkeypatch.setattr('logic.User.login', i_always_say_200)

    assert client.post(url_for('login'), content_type='application/json',
                       data=input_data).status_code == expected_code


# Most errors handled by flask
# noinspection PyShadowingNames
@pytest.mark.parametrize("server_id, provider, expected_code",
                         [
                             ('1', 'asd', 200)

                         ])
def test_server_get_input_filtering(monkeypatch, client, server_id, provider, expected_code, auth_headers):
    monkeypatch.setattr('logic.Server.get', i_always_say_200)

    assert client.get(url_for('get_server', provider=provider, server_id=server_id),
                      headers=auth_headers).status_code == expected_code


# noinspection PyShadowingNames
@pytest.mark.parametrize("server_id, provider, json_inp, expected_code",
                         [
                             ('1', 'asd', '', 200),
                             ('1', 'asd', '{"force":true}', 200),
                             ('1', 'asd', '{"force":false}', 200),
                             ('1', 'asd', '{"force":"sad"}', 200),

                         ])
def test_server_delete_input_filtering(monkeypatch, client, server_id, provider, json_inp, expected_code, auth_headers):
    monkeypatch.setattr('logic.Server.delete', i_always_say_200)

    if json_inp == '':
        del auth_headers["Content-Type"]

    assert client.delete(url_for('delete_server', provider=provider, server_id=server_id), data=json_inp,
                         headers=auth_headers).status_code == expected_code


# noinspection PyShadowingNames
def test_servers_list_input_filtering(monkeypatch, client, auth_headers):
    monkeypatch.setattr('logic.Server.delete', i_always_say_200)

    assert client.get(url_for('list_servers'), headers=auth_headers).status_code == 200


# noinspection PyShadowingNames
@pytest.mark.parametrize("input_data, expected_code",
                         [
                             (json.dumps({SERVER_PROPERTIES_KEY: {"asd": 0}, VM_CONFIGURATION_KEY: {"asd": 0}}), 200),
                         ] + autogen_tests(
                             (
                                     {SERVER_PROPERTIES_KEY: [get_everything_but_dict_list(), {"asd": 0}],
                                      VM_CONFIGURATION_KEY: [get_everything_but_dict_list(), {"asd": 0}]}
                                     , 400)
                         ))
def test_server_create_input_filtering(monkeypatch, client, input_data, expected_code, auth_headers):
    monkeypatch.setattr('logic.Server.create', i_always_say_200)

    assert client.post(url_for('create_server'), content_type='application/json',
                       data=input_data, headers=auth_headers).status_code == expected_code


VALID_SERVER_CONFIGURE_REQUEST_DATA = json.dumps({VM_CONFIGURATION_EXP_KEY: "TEST",
                                                  ACCESS_TOKEN_EXP_KEY: "24879haThis1$NoT\\/3RyR3@L",
                                                  PROVIDER_EXP_KEY: "GoodServers Ltd.",
                                                  SSH_KEY_FINGERPRINT_EXP_KEY:
                                                      "92:aa:45:bb:a8:cc:dd:3d:ee:ff:a4:55:gg:33:aa:d0",
                                                  IP_EXP_KEY: "127.0.0.1",
                                                  ID_EXP_KEY: 123455,
                                                  TEMP_SSH_KEY_EXP_KEY: "aRealKeyHere"})


# noinspection PyShadowingNames
@pytest.mark.parametrize("input_data, expected_code",
                         [
                             (VALID_SERVER_CONFIGURE_REQUEST_DATA, 200)

                         ] + autogen_tests(
                             (
                                     {VM_CONFIGURATION_EXP_KEY: [[get_int(), get_float(), "", {}, []],
                                                                 VALID_SERVER_CONFIGURE_REQUEST_DATA],
                                      ACCESS_TOKEN_EXP_KEY: [[get_int(), get_float(), "", {}, []], "8hgfR32"],
                                      SSH_KEY_FINGERPRINT_EXP_KEY: [get_everything_but_not_empty_string_list(),
                                                                    "92:aa:45:bb:a8:cc:dd:3d:ee:ff:a4:55:gg:33:aa:d0"
                                                                    ],
                                      IP_EXP_KEY: [[get_int(), get_float(), "", {}, []], "127.0.0.1"],
                                      ID_EXP_KEY: [[get_string(), get_float(), {}, []], "123455"],
                                      PROVIDER_EXP_KEY: [[get_int(), get_float(), "", {}, []], "DO"],
                                      TEMP_SSH_KEY_EXP_KEY: [[get_int(), get_float(), "", {}, []], "ttr//A=-"]}
                                     , 400)
                         ))
def test_server_configure_input_filtering(monkeypatch, client, input_data, expected_code, auth_headers):
    monkeypatch.setattr('logic.Server.configure', i_always_say_200)

    assert client.post(url_for('configure_server'), content_type='application/json',
                       data=input_data, headers=auth_headers).status_code == expected_code


# Masterconf is checked in logic
# noinspection PyShadowingNames
@pytest.mark.parametrize("input_data, expected_code",
                         [
                             (json.dumps({PROVIDER_EXP_KEY: "GoodServers Ltd.", ID_EXP_KEY: 123455}), 200),
                             (json.dumps({PROVIDER_EXP_KEY: "GoodServers Ltd.", ID_EXP_KEY: 123455,
                                          IS_MASTER_EXP_KEY: True}), 200),
                             (json.dumps({PROVIDER_EXP_KEY: "GoodServers Ltd.", ID_EXP_KEY: 123455,
                                          IS_MASTER_EXP_KEY: False}), 200),
                             (json.dumps({PROVIDER_EXP_KEY: "GoodServers Ltd.", ID_EXP_KEY: 123455,
                                          SELF_DESTRUCT_EXP_KEY: True}), 200),
                             (json.dumps({PROVIDER_EXP_KEY: "GoodServers Ltd.", ID_EXP_KEY: 123455,
                                          SELF_DESTRUCT_EXP_KEY: False}), 200),

                         ] + autogen_tests(
                             (
                                     {ID_EXP_KEY: [get_everything_but_int_list(), 123455],
                                      PROVIDER_EXP_KEY: [get_everything_but_not_empty_string_list(), "DO"]}
                                     , 400)
                         ))
def test_server_initialise_input_filtering(monkeypatch, client, input_data, expected_code, auth_headers):
    monkeypatch.setattr('logic.Server.initialise', i_always_say_200)

    assert client.post(url_for('initialise_server'), content_type='application/json',
                       data=input_data, headers=auth_headers).status_code == expected_code
