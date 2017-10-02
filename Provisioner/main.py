import httplib
import json


class server(object):
    def __init__(self,type = 'none', authDict = {}):
        self.__authDict = authDict

    def provision(self):
        return True

    def destroy(self):
        return True

class response(object):
    def __init__(self,headers,body,status,reason,httpVer):
        self.__headers = headers
        self.__body = body #type: str
        self.__status = status
        self.__reason = reason #type: str
        self.__httpVer = httpVer

    @property
    def headers(self):
        return dict(self.__headers)

    @property
    def body(self):
        return self.__body

    @property
    def status(self):
        return int(self.__status)

    @property
    def reason(self):
        return self.__reason.strip()

    @property
    def httpVer(self):
        return float(self.__httpVer)

    def jsonDecode(self):
        self.__body = json.loads(self.__body)

    def __str__(self):
        outStr = 'HTTP v{httpVer} {status}({reason}):\n' \
                 '{body}\n' \
                 'Headers : {headers}' \
                  .format(httpVer=str(self.__httpVer),status=str(self.__status),reason=str(self.__reason),body=str(self.body),headers = str(self.headers))
        return outStr


class RESTClient(object):
    def __init__(self,headersDict,hostname,port=443):
        self.__APIConnection = httplib.HTTPSConnection(hostname,port)
        self.__headers = headersDict

    def setHeaders(self,headersDict):
        self.__headers = headersDict

    def makeRequest(self,type,path,body=''):
        self.__APIConnection.request(type, path, body, headers=self.__headers)  # todo: handle errors
        APIresponse = self.__APIConnection.getresponse()
        return response(APIresponse.getheaders(),APIresponse.read(),APIresponse.status,APIresponse.reason,APIresponse.version)

    def get(self,path):
        return self.makeRequest('GET',path)

    def post(self,path,body):
        return self.makeRequest('POST', path, body)

    def delete(self,path):
        return self.makeRequest('DELETE', path)



if __name__ == "__main__":
    mabody = '''{
  "name": "manamajeff",
  "region": 0,
  "size": "512mb",
  "image": 16623283
}'''

    print mabody
    myRest = RESTClient({'Authorization':'Bearer a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6', 'Content-Type':'application/json'},'api.digitalocean.com')
    print myRest.post('/v2/droplets',mabody)