from main import *
import time

class doDroplet(server):

    def __init__(self, accessToken=None, id=None, status=None, name=None, created_at=None, size={}, networks={}, image={}, region={}, rawDropletList=[]):
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

    def fillPropertiesFromDict(self,dict):
        for key, value in dict.items():
            setattr(self, key, value)

    def provision(self):

        # All of this is currently pointless as defaults are defined in Dockerfile
        #
        # # Set default name
        #
        # if self.name == "" or self.name is None:
        #     self.name = 'Example'
        #
        # # Set default region
        #
        # if 'slug' not in self.region:
        #     self.region = {'slug':''}
        #
        # if self.region['slug'] == '':
        #     self.region['slug'] = 'lon1'
        #
        # # Set default image
        #
        # if 'slug' not in self.image:
        #     self.image = {'slug': ''}
        #
        # if self.image['slug'] == '':
        #     self.image['slug'] = 'ubuntu-14-04-x64'
        #
        # # Set default size
        #
        # if 'slug' not in self.size:
        #     self.size = {'slug': ''}
        #
        # if self.size['slug'] == '':
        #     self.size['slug'] = '512mb'

        # Define request body

        body = '''{
              "name": "%s",
              "region": "%s",
              "size": "%s",
              "image": "%s"
            }''' % (self.name, self.region['slug'], self.size['slug'], self.image['slug']) #todo: sanitize, different ways to set region/size/image

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
