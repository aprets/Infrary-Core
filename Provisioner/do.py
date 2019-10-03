import base64
import hashlib
import json
import logging
import time

import requests

logger = logging.getLogger('provisioner')


class DoDroplet(object):
    def __init__(self, access_token=None, server_id=None, status=None, name=None, created_at=None, size=None,
                 networks=None,
                 image=None, region=None, raw_droplet_dict=None, ssh_keys=None, fail_func=lambda: None):
        self.fail_func = fail_func
        super(DoDroplet, self).__init__()
        if size is None:
            size = {}
        if networks is None:
            networks = {}
        if image is None:
            image = {}
        if region is None:
            region = {}
        self.__accessToken = access_token
        self.__headers = {'Authorization': 'Bearer ' + self.__accessToken, 'Content-Type': 'application/json'}
        self.__base_url = "https://api.digitalocean.com"
        self.__session = requests.Session()
        self.__session.headers.update(self.__headers)
        if raw_droplet_dict:
            self.fill_properties_from_dict(raw_droplet_dict)
        self.id = server_id
        self.status = status
        self.name = name
        self.created_at = created_at
        self.size = size
        self.networks = networks
        self.image = image
        self.region = region
        self.__SSHKeys = ssh_keys
        if ssh_keys is not None:
            self.SSHFingerprints = []
            for key in self.__SSHKeys:
                self.SSHFingerprints.append(self.rsa_public_key_str_to_fingerprint(key))

    def fill_properties_from_dict(self, inp_dict):
        for key, value in inp_dict.items():
            setattr(self, key, value)

    def rsa_public_key_str_to_fingerprint(self, public_key_str):
        try:
            key = base64.b64decode(public_key_str.strip().split()[1].encode('ascii'))
        except:
            self.fail_func('Critical provisioning error: Bad SSH key!')
        finger_print = hashlib.md5(key).hexdigest()
        return ':'.join(left + right for left, right in zip(finger_print[::2], finger_print[1::2]))

    def add_key_if_non_existent(self, key, fingerprint):
        logger.debug('Assigning a Public Key \n{}\n{}'.format(key, fingerprint))

        body = json.dumps(
            {
                'name': self.name,
                'public_key': key
            }
        )

        logger.debug('About to create the following key:{}'.format(body))

        try:
            do_response = self.__session.post(self.__base_url + '/v2/account/keys', data=body)
        except Exception as e:
            return False, "Could not connect to DO API: {}".format(e.message)
        if do_response.status_code == 201:
            logger.info('DO: Public key successfully created!')
            return True, ''
        elif do_response.status_code == 422 and do_response.json().get(
                "message") == u'SSH Key is already in use on your account':
            logger.info('DO: Public key already exists!')
            return True, ''
        else:
            return False, "Failed to create a key! Response from DO API: {}".format(do_response.text)

    def provision(self):
        for keyInd in range(len(self.__SSHKeys)):
            status, message = self.add_key_if_non_existent(self.__SSHKeys[keyInd], self.SSHFingerprints[keyInd])
            if not status:
                return False, "SSH Key error: {}".format(message)

        body = json.dumps(
            {
                'name': self.name,
                'region': self.region['slug'],  # ['slug'] is always set by start.py, so its okay not to .get(...)
                'size': self.size['slug'],
                'image': self.image['slug'],
                'ssh_keys': self.SSHFingerprints
            }
        )

        logger.info('DO: About to create the following droplet:\n{}'.format(body))

        def request_provisioning():
            try:
                return True, self.__session.post(self.__base_url + '/v2/droplets', data=body)
            except Exception as e:
                return False, "Could not connect to DO API: {}".format(e.message)

        success, do_response = request_provisioning()

        if not success:
            return success, do_response

        if do_response.status_code == 403:
            logger.warning('DO responded with 403: {}! Will retry...'.format(do_response.text))
            retry_count = 0
            while retry_count < 15 and do_response.status_code != 202:
                time.sleep(10)
                success, do_response = request_provisioning()
                logger.warning(
                    'DO responded with 403: {}! This was attempt {}'.format(do_response.text, str(retry_count))
                )
                retry_count += 1
                if not success:
                    return success, do_response

        if do_response.status_code == 202:
            self.fill_properties_from_dict(do_response.json()['droplet'])
            logger.info('DO: Waiting for the droplet to become active')
            t = 0
            while self.status != 'active':
                time.sleep(2)
                t += 2
                logger.info('DO: Server still inactive. Waiting...'.format(str(t)))
                self.update()
            return True, ''
        else:
            return False, "Failed to provision a droplet! Response from DO API: {}".format(do_response.text)

    def update(self):
        try:
            do_response = self.__session.get(self.__base_url + '/v2/droplets/{}'.format(self.id))
        except Exception as e:
            return False, "Could not connect to DO API"
        if do_response.status_code == 200:
            self.fill_properties_from_dict(do_response.json()['droplet'])
            return True, ''
        else:
            return False, "Failed to update droplet information! Response from DO API: {}".format(do_response.text)

    def destroy(self):
        return self.__session.delete(self.__base_url + '/v2/droplets/{}'.format(self.id))

    def __str__(self):
        return '\n'.join("%s=%s" % obj_property for obj_property in vars(self).items())

#
# if __name__ == "__main__":
#     myDroplet = doDroplet(accessToken='a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6')
#     myDroplet.provision()
#     logger.info(myDroplet)
#     logger.info(myDroplet.destroy())
#     time.sleep(5)
#     m
