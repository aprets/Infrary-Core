import httplib
import json


class Server(object):
    def __init__(self):
        pass

    def provision(self):
        return True

    def destroy(self):
        return True


class Response(object):
    def __init__(self, headers, body, status, reason, http_ver):
        self.__headers = headers
        self.__body = body  # type: str
        self.__status = status
        self.__reason = reason  # type: str
        self.__httpVer = http_ver

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
    def http_ver(self):
        return float(self.__httpVer)

    def json_decode(self):
        self.__body = json.loads(self.__body)

    def __str__(self):
        out_str = 'HTTP v{httpVer} {status}({reason}):\n' \
                 '{body}\n' \
                 'Headers : {headers}'.format(httpVer=str(self.__httpVer),
                                              status=str(self.__status),
                                              reason=str(self.__reason),
                                              body=str(self.body),
                                              headers=str(self.headers))
        return out_str


class HTTPClient(object):
    def __init__(self, headers_dict, hostname, port=443, use_https=True):
        if use_https:
            self.__APIConnection = httplib.HTTPSConnection(hostname, port)
        else:
            self.__APIConnection = httplib.HTTPConnection(hostname, port)
        self.__headers = headers_dict

    def set_headers(self, headers_dict):
        self.__headers = headers_dict

    def make_request(self, request_type, path, body=''):
        self.__APIConnection.request(request_type, path, body, headers=self.__headers)  # todo: handle errors
        api_response = self.__APIConnection.getresponse()
        return Response(api_response.getheaders(), api_response.read(), api_response.status, api_response.reason,
                        api_response.version)

    def get(self, path):
        return self.make_request('GET', path)

    def post(self, path, body):
        return self.make_request('POST', path, body)

    def put(self, path, body):
        return self.make_request('PUT', path, body)

    def delete(self, path):
        return self.make_request('DELETE', path)


