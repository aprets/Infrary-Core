from flask import url_for
from conftest import *


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
                             ('{"firstName":"a","lastName":"b","email":"d","password":"c"}', 200)
                         ] + autogen_tests(
                             (
                                     {"firstName": [get_everything_but_not_empty_string_list(), "a"],
                                      "lastName": [get_everything_but_not_empty_string_list(), "b"],
                                      "email": [get_everything_but_not_empty_string_list(), "a@b.c"],
                                      "password": [get_everything_but_not_empty_string_list(), "a"]}
                                     , 400)
                         ))
def test_register_input_filtering(monkeypatch, client, input_data, expected_code):
    monkeypatch.setattr('logic.User.register', i_always_say_200)

    assert client.post(url_for('register'), content_type='application/json',
                       data=input_data).status_code == expected_code


# noinspection SpellCheckingInspection
@pytest.mark.parametrize("input_data, expected_code",
                         [
                             ('{"emailKey":"aw34tuya4ADF"}', 200),
                             ('', 400)
                         ] + autogen_tests(
                             (
                                     {"emailKey": [[get_int(), get_float(), "", 0, 0.0, {}, []], "aw34tuya4ADF"]}
                                     , 400)
                         ))
def test_verify_input_filtering(monkeypatch, client, input_data, expected_code):
    monkeypatch.setattr('logic.User.verify', i_always_say_200)

    assert client.post(url_for('verify'), content_type='application/json',
                       data=input_data).status_code == expected_code


@pytest.mark.parametrize("input_data, expected_code",
                         [
                             ('{"email":"a","password":"b"}', 200),
                             ('', 400)
                         ] + autogen_tests(
                             (
                                     {"email": [get_everything_but_not_empty_string_list(), "a@b.c"],
                                      "password": [get_everything_but_not_empty_string_list(), "a"]}
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
                             ('{"serverProperties":{"asd":0}, "VMConfiguration":{"asd":0}}', 200),
                         ] + autogen_tests(
                             (
                                     {"serverProperties": [get_everything_but_dict_list(), {"asd": 0}],
                                      "VMConfiguration": [get_everything_but_dict_list(), {"asd": 0}]}
                                     , 400)
                         ))
def test_server_create_input_filtering(monkeypatch, client, input_data, expected_code, auth_headers):
    monkeypatch.setattr('logic.Server.create', i_always_say_200)

    assert client.post(url_for('create_server'), content_type='application/json',
                       data=input_data, headers=auth_headers).status_code == expected_code


# Relatively complex test data to ensure multiple escape levels [eg. in commandList] still function

VALID_SERVER_CONFIGURE_REQUEST_DATA = (r'' '\n'
                                       r'{"__Infrary__VMConfiguration": "{\"isMaster\": true, \"selfDestruct\": true, '
                                       r'\"cmdList\": [\"curl https://releases.rancher.com/install-docker/17.06.sh | '
                                       r'sh\", \"service ntp stop\", \"update-rc.d -f ntp remove\", \"fallocate -l 4G '
                                       r'/swapfile\", \"chmod 600 /swapfile\", \"mkswap /swapfile\",'
                                       r'\"swapon /swapfile\", \"echo \\\"/swapfile   none    swap    sw    0   0\\\" '
                                       r'>> /etc/fstab\", \"docker run -d --restart=unless-stopped -p 8080:8080 '
                                       r'rancher/server\", \"sleep 60\"]}",'
                                       r'"__Infrary__AccessToken": "24879haThis1$NoT\/3RyR3@L",'
                                       r'"__Infrary__Provider": "GoodServers Ltd.",'
                                       r'"__Infrary__SSHKeyFingerprint": '
                                       r'"92:aa:45:bb:a8:cc:dd:3d:ee:ff:a4:55:gg:33:aa:d0", '
                                       r'"__Infrary__IP": "127.0.0.1",'
                                       r'"__Infrary__ID": 123455,'
                                       r'"__Infrary__TempSSHKey": "aRealKeyHere"}')


# noinspection PyShadowingNames
@pytest.mark.parametrize("input_data, expected_code",
                         [
                             (VALID_SERVER_CONFIGURE_REQUEST_DATA, 200)

                         ] + autogen_tests(
                             (
                                     {"__Infrary__VMConfiguration": [[get_int(), get_float(), "", {}, []],
                                                                     json.loads(VALID_SERVER_CONFIGURE_REQUEST_DATA)
                                                                     ["__Infrary__VMConfiguration"]],
                                      "__Infrary__AccessToken": [[get_int(), get_float(), "", {}, []], "8hgfR32"],
                                      "__Infrary__SSHKeyFingerprint": [get_everything_but_not_empty_string_list(),
                                                                       "92:aa:45:bb:a8:cc:dd:3d:ee:ff:a4:55:gg:33:aa:d0"
                                                                       ],
                                      "__Infrary__IP": [[get_int(), get_float(), "", {}, []], "127.0.0.1"],
                                      "__Infrary__ID": [[get_string(), get_float(), {}, []], "123455"],
                                      "__Infrary__Provider": [[get_int(), get_float(), "", {}, []], "DO"],
                                      "__Infrary__TempSSHKey": [[get_int(), get_float(), "", {}, []], "ttr//A=-"]}
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
                             ('{"__Infrary__Provider": "GoodServers Ltd.", "__Infrary__ID": 123455}', 200),
                             ('{"__Infrary__Provider": "GoodServers Ltd.", "__Infrary__ID": 123455,'
                              ' "__Infrary__IsMaster": true}', 200),
                             ('{"__Infrary__Provider": "GoodServers Ltd.", "__Infrary__ID": 123455,'
                              ' "__Infrary__IsMaster": false}', 200),
                             ('{"__Infrary__Provider": "GoodServers Ltd.", "__Infrary__ID": 123455,'
                              ' "__Infrary__SelfDestruct": true}', 200),
                             ('{"__Infrary__Provider": "GoodServers Ltd.", "__Infrary__ID": 123455,'
                              ' "__Infrary__SelfDestruct": false}', 200),

                         ] + autogen_tests(
                             (
                                     {"__Infrary__ID": [get_everything_but_int_list(), 123455],
                                      "__Infrary__Provider": [get_everything_but_not_empty_string_list(), "DO"]}
                                     , 400)
                         ))
def test_server_initialise_input_filtering(monkeypatch, client, input_data, expected_code, auth_headers):
    monkeypatch.setattr('logic.Server.initialise', i_always_say_200)

    assert client.post(url_for('initialise_server'), content_type='application/json',
                       data=input_data, headers=auth_headers).status_code == expected_code
