import base64
import json
import logging
import random
import string
import time

import requests
import yaml

from constants import *

logger = logging.getLogger('vmconf')


class RancherCommError(Exception):
    def __init__(self, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "An error occurred communicating with rancher:\n    {}".format(msg)
        super(RancherCommError, self).__init__(msg)


class Rancher(object):

    def __init__(self, hostname, stacks=[], port=8080):
        self.hostname = hostname
        self.port = port
        self.stacks = stacks
        self.session = requests.Session()

    def connect(self, log_submit_func=lambda: None):
        try_counter = 1
        is_rancher_alive = False
        while not is_rancher_alive:
            if try_counter == 20:
                logger.error('Rancher not responding')
                return False
            logger.info('Attempting to connect to Rancher (Attempt {})'.format(str(try_counter)))
            try_counter += 1
            try:
                rancher_response = self.session.get('http://{}:{}/'.format(self.hostname, self.port, retries=False))
                if rancher_response.status_code == 200:
                    is_rancher_alive = True
                    logger.info("Rancher is up!")
            except requests.exceptions.ConnectionError:
                log_submit_func()
                time.sleep(10)

        return True

    def configure(self):
        # Create API Key for future use
        rancher_key_secret = ''.join(
            random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(50)
        )
        rancher_response = self.session.post(
            "http://{}:{}{}".format(self.hostname, self.port, '/v2-beta/apiKeys'),
            json=
            {
                "description": "Do Not Delete Infrary API KEY",
                "name": "Infrary API KEY",
                "publicValue": "InfraryAPIKey",
                "secretValue": rancher_key_secret
            }
        )
        if rancher_response.status_code != 201:
            raise RancherCommError("Error creating apiKeys:\n{}".format(rancher_response.text))
        auth_str = base64.b64encode('InfraryAPIKey:{}'.format(rancher_key_secret))
        self.session.headers.update({'Authorization': 'Basic {}'.format(auth_str)})

        # Enable auth

        rancher_user = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
        rancher_pass = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(50))
        rancher_response = self.session.post(
            "http://{}:{}{}".format(self.hostname, self.port, '/v2-beta/localauthconfig'),
            json=
            {
                "enabled": True,
                "name": "Infrary User",
                "password": rancher_pass,
                "username": rancher_user
            }
        )
        if rancher_response.status_code != 201:
            raise RancherCommError("Error enabling auth:\n{}".format(rancher_response.text))

        rancher_conf_dict = \
            {
                MASTERCONF_HOST_KEY: '{}:{}'.format(self.hostname, self.port),
                MASTERCONF_USER_KEY: rancher_user,
                MASTERCONF_PASSWORD_KEY: rancher_pass,
                MASTERCONF_SECRET_KEY: rancher_key_secret
            }

        # Launch compose stacks

        time.sleep(10)

        rancher_response = requests.get(
            "http://{}:{}{}".format(self.hostname, self.port, '/v2-beta/projects/1a5/stacks'))

        logger.debug(rancher_response.text)

        if self.stacks:
            for stack in self.stacks:
                name = stack['name']
                docker_compose = yaml.safe_dump(stack['docker-compose'], default_flow_style=False)
                rancher_compose = yaml.safe_dump(stack['rancher-compose'], default_flow_style=False)

                logger.debug('\n'.join([name, docker_compose, rancher_compose]))

                rancher_response = self.session.post(
                    "http://{}:{}{}".format(self.hostname, self.port, '/v2-beta/projects/1a5/stacks'),
                    json=
                    {
                        "name": name,
                        "dockerCompose": docker_compose,
                        "rancherCompose": rancher_compose,
                        "binding": None,
                        "system": False,
                        "startOnCreate": True
                    }
                )
                if rancher_response.status_code != 201:
                    raise RancherCommError("Error creating stack {}:\n{}".format(name, rancher_response.text))
                logger.debug(rancher_response.text)

        return rancher_conf_dict

    @staticmethod
    def fetch_slave_cmds(master_conf):
        url = "http://{}/v2-beta/projects/1a5/registrationTokens".format(
            master_conf[MASTERCONF_HOST_KEY])
        auth_tuple = ('InfraryAPIKey', master_conf[MASTERCONF_SECRET_KEY])
        logger.debug("Submit:\n" + str(url) + "\n" + str(auth_tuple))
        response = requests.post(url, auth=auth_tuple)
        logger.debug("Response:\n" + str(response.status_code) + "\n" + response.text)
        response_json = json.loads(response.text)
        logger.debug("Submit:\n" + str(response_json) + "\n" + str(response_json['links']['self']))
        response = requests.get(response_json['links']['self'], auth=auth_tuple)
        logger.debug("Response:\n" + str(response.text) + "\n" + response.text)
        response_json = json.loads(response.text)
        return ["curl https://releases.rancher.com/install-docker/17.12.sh | sh", response_json['command']]
