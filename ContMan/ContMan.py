from flask import Flask, request
from functools import wraps
from constants import *
import os
import jwt
import docker
import logging


IS_WIN = (os.name == 'nt')

app = Flask(__name__)


def launch_container(image, cmd, env):

    auto_remove = not IS_DEBUG

    print 'docker run {} \n{}\n{}'.format(image, cmd, env)

    if not IS_WIN:
        try:
            os.system("docker-credential-gcr configure-docker")  # avoid threading for compatibility
        except:  # Not too crucial as we might still have valid tokens
            pass
        docker_client = docker.from_env()
    else:
        docker_client = docker.DockerClient(base_url='tcp://127.0.0.1:2375')
    if not IS_DEBUG:
        docker_client.images.pull(image)
    out = docker_client.containers.run(image, cmd, environment=env, auto_remove=auto_remove, detach=True)
    return out


def auth_required(f):
    @wraps(f)
    def do_auth(*args, **kwargs):
        logging.debug(request.headers)
        logging.debug(request.get_data())
        logging.debug(request.get_json())
        if request.method not in ["OPTIONS"]:
            try:
                supplied_auth_header = request.headers.get("Authorization")
                if not supplied_auth_header:
                    raise ValueError('No authorization token supplied.')
                if "Bearer" in supplied_auth_header:
                    token = supplied_auth_header.split(' ')[1]
                    try:
                        decoded_token = jwt.decode(token, SECRET_TOKEN_DEC_KEY, algorithm='RS512')
                    except jwt.InvalidTokenError as e:
                        raise ValueError('Authentication failed.')
                    else:
                        if decoded_token.get("admin"):
                            pass
                        else:
                            raise ValueError('Authentication failed.')
                else:
                    raise ValueError('No auth token supplied.')
            except Exception as e:
                return "Unauthorized: {}".format(e), 401
        return f(*args, **kwargs)
    return do_auth


@app.route('/', methods=['GET'])
def mock():
    return 'This is a page. This is not how you access the API though (C\'mon you\'re GETing).' \
           ' Please actually POST to this server.<br>Thanks,<br>ContMan.'


@app.route("/", methods=['POST'])
@auth_required
def main():
    request_dict = request.get_json()

    print(request_dict)

    if not isinstance(request_dict, dict):
        return "Bad request format", 400

    image = request_dict.get(IMAGE_KEY)
    cmd = request_dict.get(COMMAND_KEY)
    env = request_dict.get(ENVIRONMENT_KEY)

    if image and isinstance(image, basestring)\
            and isinstance(cmd, basestring) \
            and isinstance(env, dict):
        out = launch_container(image, cmd, env)
        if out:
            return "WOW", 200
        else:
            return out, 500
    else:
        return "Parameters invalid or empty", 400


if __name__ == '__main__':
    app.run(port=5555, host='0.0.0.0', debug=True)
