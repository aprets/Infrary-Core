from main import *
import base64
import hashlib


class DoDroplet(Server):
    def __init__(self, access_token=None, server_id=None, status=None, name=None, created_at=None, size=None,
                 networks=None,
                 image=None, region=None, raw_droplet_dict=None, ssh_keys=None):  # TODO force ssh key to be passed
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
        self.__HTTPSClient = HTTPClient(self.__headers, 'api.digitalocean.com')
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

    @staticmethod
    def rsa_public_key_str_to_fingerprint(public_key_str):
        key = base64.b64decode(public_key_str.strip().split()[1].encode('ascii'))  # todo COMMENTITALL
        finger_print = hashlib.md5(key).hexdigest()
        return ':'.join(left + right for left, right in zip(finger_print[::2], finger_print[1::2]))

    def add_key_if_non_existent(self, key, fingerprint):
        print ('Assigning a Public Key')
        print key, fingerprint

        body = '''{
                      "name": "%s",
                      "public_key": "%s"
                    }''' % (
            'A key for {}'.format(self.name), key)  # todo: sanitize, different ways to set region/size/image

        print 'About to create the following key:'
        print body

        try:
            do_response = self.__HTTPSClient.post('/v2/account/keys', body)
        except Exception as e:
            print "Could not connect to DO API"
            print e.message
            return False, e.message
        do_response.json_decode()
        if do_response.status == 201:
            print ('Key successfully created!')
            return True, ''
        elif do_response.status == 422 and do_response.body.get(
                "message") == u'SSH Key is already in use on your account':
            print ('Key already exists!')
            return True, ''
        else:
            print "Failed to create a key! Response from DO API:"
            print do_response
            return False, do_response

    def provision(self):
        for keyInd in range(len(self.__SSHKeys)):
            status, message = self.add_key_if_non_existent(self.__SSHKeys[keyInd], self.SSHFingerprints[keyInd])
            if not status:
                print ("SSH Key error:")
                print message
                exit(1)

        # Define request body
        body = '''{
              "name": "%s",
              "region": "%s",
              "size": "%s",
              "image": "%s",
              "ssh_keys": %s
            }''' % (self.name, self.region['slug'], self.size['slug'], self.image['slug'],
                    str(self.SSHFingerprints).replace('\'',
                                                      '"'))  # todo: sanitize, different ways to set region/size/image

        print 'About to create the following droplet:'
        print body

        try:
            do_response = self.__HTTPSClient.post('/v2/droplets', body)
        except Exception as e:
            print "Could not connect to DO API"
            print e.message
            return False, e.message
        do_response.json_decode()
        if do_response.status == 202:
            self.fill_properties_from_dict(do_response.body['droplet'])
            print 'Waiting for the droplet to become active'
            while self.status != 'active':
                print '...'
                self.update()
            return True, ''
        else:
            print "Failed to provision a droplet! Response from DO API:"
            print do_response
            return False, do_response

    def update(self):
        try:
            do_response = self.__HTTPSClient.get('/v2/droplets/{}'.format(self.id))  # todo: handle no ip
        except Exception as e:
            print "Could not connect to DO API"
            print e.message
            return False, e.message
        if do_response.status == 200:
            do_response.json_decode()
            self.fill_properties_from_dict(do_response.body['droplet'])
            return True, ''
        else:
            print "Failed to update droplet information! Response from DO API:"
            print do_response
            return False, do_response

    def destroy(self):
        return self.__HTTPSClient.delete('/v2/droplets/{}'.format(self.id))

    def __str__(self):
        return '\n'.join("%s=%s" % obj_property for obj_property in vars(self).items())

#
# if __name__ == "__main__":
#     myDroplet = doDroplet(accessToken='a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6')
#     myDroplet.provision()
#     print myDroplet
#     print myDroplet.destroy()
#     time.sleep(5)
#     myDroplet.update()
#     print myDroplet
