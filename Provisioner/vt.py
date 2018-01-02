from main import *


class VtInstance(Server):
    def __init__(self, api_key=None, sub_id=None, status=None, label=None, date_created=None, dc_id=None, vps_plan_id=None,
                 os_id=None, raw_instance_dict=None):
        super(VtInstance, self).__init__()
        if os_id is None:
            os_id = {}
        self.__apiKey = api_key
        self.__headers = {'API-Key': self.__apiKey,
                          'Content-Type': 'application/x-www-form-urlencoded'}
        self.__HTTPSClient = HTTPClient(self.__headers, 'api.vultr.com')
        if raw_instance_dict:
            self.fill_properties_from_dict(raw_instance_dict)
        self.sub_id = sub_id
        self.status = status
        self.label = label
        self.date_created = date_created
        self.dc_id = dc_id
        self.vps_plan_id = vps_plan_id
        self.os_id = os_id

    def fill_properties_from_dict(self, inp_dict):
        for key, value in inp_dict.items():
            setattr(self, key, value)

    def provision(self):

        body = "DCID={}&OSID={}&VPSPLANID={}&label={}".format(self.dc_id, self.os_id, self.vps_plan_id, self.label)

        print 'About to create the following instance:'
        print body

        try:
            vt_response = {"SUBID": "10966178"}
        except Exception as e:
            print "Could not connect to API"
            print e.message
            return False, e.message
        print vt_response
        if True:
            self.fill_properties_from_dict(vt_response)
            print 'Waiting for the instance to become active'
            while self.status != 'active':
                print '...'
                self.update()
            return True, ''
        else:
            print "Failed to provision an instance! Response from API:"
            print vt_response
            return False, vt_response

    def update(self):
        try:
            vt_response = self.__HTTPSClient.get('/v1/server/list?SUBID={}'.format(self.sub_id))  # todo: handle no ip
        except Exception as e:
            print "Could not connect to API"
            print e.message
            return False, e.message
        if vt_response.status == 200:
            vt_response.json_decode()
            self.fill_properties_from_dict(vt_response.body)
            print self
            return True, ''
        else:
            print "Failed to update droplet information! Response from DO API:"
            print vt_response
            return False, vt_response

    def destroy(self):
        return self.__HTTPSClient.delete('/v2/droplets/{}'.format(self.sub_id))

    def __str__(self):
        return '\n'.join("%s=%s" % obj_property for obj_property in vars(self).items())


if __name__ == "__main__":
    myServer = VtInstance(api_key='VWU7R575JW3XWCKAJJJSZNTNM4LXFJ', dc_id=1, os_id=215, vps_plan_id=201)
    myServer.provision()
    print myServer
    # print myServer.destroy()
    # time.sleep(5)
    # myServer.update()
    # print myServer
