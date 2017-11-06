from main import *
import time
import base64
import hashlib

class doDroplet(server):

    def __init__(self, accessToken=None, id=None, status=None, name=None, created_at=None, size={}, networks={}, image={}, region={}, rawDropletList=[], sshKey = None): #TODO force ssh key to be passed
        self.__accessToken = accessToken
        self.__headers = {'Authorization': 'Bearer ' + self.__accessToken, 'Content-Type': 'application/json'}
        self.__HTTPSClient = HTTPClient(self.__headers, 'api.digitalocean.com')
        if rawDropletList != []:
            self.fillPropertiesFromDict(rawDropletList)
        self.id = id
        self.status = status
        self.name = name
        self.created_at = created_at
        self.size = size
        self.networks = networks
        self.image = image
        self.region = region
        self.__SSHKey = sshKey
        self.SSHFingerprint = self.RSAPublicKeyStrToFingerprint(self.__SSHKey)

    def fillPropertiesFromDict(self,dict):
        for key, value in dict.items():
            setattr(self, key, value)

    def RSAPublicKeyStrToFingerprint(self, publicKeyStr):
        key = base64.b64decode(publicKeyStr.strip().split()[1].encode('ascii'))
        fingerPrint = hashlib.md5(key).hexdigest()
        return ':'.join(a + b for a, b in zip(fingerPrint[::2], fingerPrint[1::2]))

    def AddKeyIfNonExistant(self):
        print ('Assigning a Public Key')
        try:
            DOresponse = self.__HTTPSClient.get('/v2/account/keys')
        except Exception as e:
            print "Could not connect to DO API"
            print e.message
            return False, e.message
        DOresponse.jsonDecode()
        accountSSHKeys = DOresponse.body["ssh_keys"]
        if not any(key['fingerprint'] == self.SSHFingerprint for key in accountSSHKeys):
            print ('The key is not registered with DO, creating it...')
            body = '''{
                          "name": "%s",
                          "public_key": "%s"
                        }''' % ('A key for {}'.format(self.name),self.__SSHKey)  # todo: sanitize, different ways to set region/size/image

            print 'About to create the following key:'
            print body

            try:
                DOresponse = self.__HTTPSClient.post('/v2/account/keys', body)
            except Exception as e:
                print "Could not connect to DO API"
                print e.message
                return False, e.message
            DOresponse.jsonDecode()
            print DOresponse.status
            if DOresponse.status == 201:
                print ('Key successfully created!')
                return True, ''
            else:
                print "Failed to create a key! Response from DO API:"
                print DOresponse
                return False, DOresponse
        else:
            print ('The key already exists!')
            return True, ''




    def provision(self):

        # Define request body
        status,message = self.AddKeyIfNonExistant()
        if not status:
            print ("SSH Key error:")
            print message
            exit(1)


        body = '''{
              "name": "%s",
              "region": "%s",
              "size": "%s",
              "image": "%s",
              "ssh_keys": ["%s"]
            }''' % (self.name, self.region['slug'], self.size['slug'], self.image['slug'], self.SSHFingerprint) #todo: sanitize, different ways to set region/size/image

        print 'About to create the following droplet:'
        print body

        try:
            DOresponse = self.__HTTPSClient.post('/v2/droplets', body)
        except Exception as e:
            print "Could not connect to DO API"
            print e.message
            return False, e.message
        DOresponse.jsonDecode()
        if DOresponse.status == 202:
            self.fillPropertiesFromDict(DOresponse.body['droplet'])
            print 'Waiting for the droplet to become active'
            while self.status != 'active':
                print '...'
                self.update()
            return True,''
        else:
            print "Failed to provision a droplet! Response from DO API:"
            print DOresponse
            return False,DOresponse

    def update(self):
        try:
            DOresponse = self.__HTTPSClient.get('/v2/droplets/{}'.format(self.id)) #todo: handle no ip
        except Exception as e:
            print "Could not connect to DO API"
            print e.message
            return False,e.message
        if DOresponse.status == 200:
            DOresponse.jsonDecode()
            self.fillPropertiesFromDict(DOresponse.body['droplet'])
            return True,''
        else:
            print "Failed to update droplet information! Response from DO API:"
            print DOresponse
            return False,DOresponse

    def destroy(self):
        return self.__HTTPSClient.delete('/v2/droplets/{}'.format(self.id))

    def __str__(self):
        return '\n'.join("%s=%s" % property for property in vars(self).items())








#
# if __name__ == "__main__":
#     myDroplet = doDroplet(accessToken='a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6')
#     myDroplet.provision()
#     print myDroplet
#     print myDroplet.destroy()
#     time.sleep(5)
#     myDroplet.update()
#     print myDroplet
