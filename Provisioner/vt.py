from main import *
import time

class vtInstance(server):

    def __init__(self, apiKey=None, SUBID=None, status=None, label=None, date_created=None, DCID=None, VPSPLANID=None, OSID={}, rawInstanceList=[]):
        self.__apiKey = apiKey
        self.__headers = {'API-Key': self.__apiKey, 'Content-Type': 'application/x-www-form-urlencoded'} #, 'Content-Type': 'application/x-www-form-urlencoded'
        self.__HTTPSClient = HTTPClient(self.__headers, 'api.vultr.com')
        if rawInstanceList != []:
            self.fillPropertiesFromDict(rawInstanceList)
        self.SUBID = SUBID
        self.status = status
        self.label = label
        self.date_created = date_created
        self.DCID = DCID
        self.VPSPLANID = VPSPLANID
        self.OSID = OSID

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

        # body = '''{
        #       "DCID": "%s",
        #       "OSID": "%s",
        #       "VPSPLANID": "%s",
        #       "label": "%s"
        #     }''' % (self.DCID, self.OSID, self.VPSPLANID, self.label) #todo: sanitize, different ways to set region/size/image

        body = "DCID={}&OSID={}&VPSPLANID={}&label={}".format(self.DCID, self.OSID, self.VPSPLANID, self.label)

        print 'About to create the following instance:'
        print body

        try:
            #response = self.__HTTPSClient.post('/v1/server/create', body)
            response = {"SUBID": "10966178"}
        except Exception as e:
            print "Could not connect to API"
            print e.message
            return False, e.message
        print response
        if True:#response.status == 202:
            #response.jsonDecode()
            self.fillPropertiesFromDict(response)#response.body)
            print 'Waiting for the instance to become active'
            while self.status != 'active':
                print '...'
                self.update()
            return True,''
        else:
            print "Failed to provision an instance! Response from API:"
            print response
            return False,response

    def update(self):
        try:
            response = self.__HTTPSClient.get('/v1/server/list?SUBID={}'.format(self.SUBID)) #todo: handle no ip
        except Exception as e:
            print "Could not connect to API"
            print e.message
            return False,e.message
        if response.status == 200:
            response.jsonDecode()
            self.fillPropertiesFromDict(response.body)
            print self
            return True,''
        else:
            print "Failed to update droplet information! Response from DO API:"
            print response
            return False,response

    def destroy(self):
        return self.__HTTPSClient.delete('/v2/droplets/{}'.format(self.SUBID))

    def __str__(self):
        return '\n'.join("%s=%s" % property for property in vars(self).items())









if __name__ == "__main__":
    myServer = vtInstance(apiKey='VWU7R575JW3XWCKAJJJSZNTNM4LXFJ',DCID=1,OSID=215,VPSPLANID=201)
    myServer.provision()
    print myServer
    # print myServer.destroy()
    # time.sleep(5)
    # myServer.update()
    # print myServer
