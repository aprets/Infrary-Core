import jwt
import time
import json
from main import *


OCTOCORE_DOMAIN = '127.0.0.1'
OCTOCORE_PORT = 5000

timestamp = int(time.time())

expTime = timestamp + 60 * 60 #expire in an hour



payload = {'exp':expTime,'uid':'59f60945f36d28236307ef2c','admin':True}

jwtToken = jwt.encode(payload, 'totallysecure', 'HS256')

print jwtToken

headers = {'Authorization': 'Bearer ' + jwtToken, 'Content-Type': 'application/json'}
HTTPSClient = HTTPClient(headers, OCTOCORE_DOMAIN, OCTOCORE_PORT, False)

'''
ENV SERVER_PROVIDER DO
ENV ACCESS_TOKEN a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6
ENV SERVER_NAME "Infrary"
ENV SERVER_SIZE "512mb"
ENV SERVER_IMAGE "ubuntu-14-04-x64"
ENV SERVER_LOCATION "lon1"
ENV SSH_KEY "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3KVkFiPI+5RlTiTKsRkjEZr6ssjYFw9Tk0dzoLKYQH8NOWA13tpSo8r6wT7P+yxXG631wGSBfHyarCpuNO8X2sS7y1zWFVIiDvp1cT4sKGF3kfMPjmt5vrfrp+qEzxHDG9oQqCvnYv1NnhIsb+ZgLG+S56z7ssEx+CPpbUU2RE+27/RYxRNjSZQ7l3eNiQyyvBlPBnK+RK6uccUJhG8KfqWB1hOtlJ7H71Mx0RwiLA6as7OK5PuwqkCN5JhzJs48mRjtRE86R0VwKwny/LuPmTMyyz7JCg38C4PDgEXIJrAfuo/TJDcqiJnxPeX4+neDnmXEeVvUqMUnbVNlk8qZ+w=="
'''

serverProperties = {"SERVER_PROVIDER": "DO", "ACCESS_TOKEN": "a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6", "SERVER_NAME": "Infrary", "SERVER_SIZE": "512mb", "SERVER_IMAGE": "ubuntu-14-04-x64", "SERVER_LOCATION": "lon1", "SSH_KEY": "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3KVkFiPI+5RlTiTKsRkjEZr6ssjYFw9Tk0dzoLKYQH8NOWA13tpSo8r6wT7P+yxXG631wGSBfHyarCpuNO8X2sS7y1zWFVIiDvp1cT4sKGF3kfMPjmt5vrfrp+qEzxHDG9oQqCvnYv1NnhIsb+ZgLG+S56z7ssEx+CPpbUU2RE+27/RYxRNjSZQ7l3eNiQyyvBlPBnK+RK6uccUJhG8KfqWB1hOtlJ7H71Mx0RwiLA6as7OK5PuwqkCN5JhzJs48mRjtRE86R0VwKwny/LuPmTMyyz7JCg38C4PDgEXIJrAfuo/TJDcqiJnxPeX4+neDnmXEeVvUqMUnbVNlk8qZ+w=="}

VMConfiguration = {"cmdList": ["curl https://releases.rancher.com/install-docker/17.06.sh | sh","service ntp stop","update-rc.d -f ntp remove","echo hi >> /helloworld"]}

body = json.dumps({"serverProperties" : serverProperties, "VMConfiguration" : VMConfiguration})

response = HTTPSClient.post('/v0/servers/provision/create',body)

print response
