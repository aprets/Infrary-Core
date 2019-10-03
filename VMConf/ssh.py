import paramiko

try:
    from cStringIO import StringIO  # Python 2
except ImportError:
    from io import StringIO

import logging

logger = logging.getLogger('vmconf')


class SSHClient(object):
    kck = None

    def __init__(self, hostname, port, username, key_str):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.__ssh_key = paramiko.RSAKey.from_private_key(StringIO(key_str))
        self.__port = port
        self.__hostname = hostname
        self.__username = username

    def __del__(self):
        self.close()

    def connect(self):
        try:
            self.client.connect(self.__hostname, self.__port, self.__username, pkey=self.__ssh_key, timeout=10)
        except paramiko.BadHostKeyException:
            logger.error("The server's host key could not be verified")
            return False
        except paramiko.AuthenticationException:
            logger.error("Authentication failed")
            return False
        except paramiko.SSHException:
            logger.error("There was any other error connecting or establishing an SSH session")
            return False
        except paramiko.client.socket.error:
            logger.error("Socket error occurred while connecting")
            return False

        return True

    def close(self):
        self.client.close()

    def execute_command(self, command):
        if self.client:
            cmd_exec_log = '\n'
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Log data when available
                if stdout.channel.recv_ready():
                    received_data = stdout.channel.recv(1024)
                    cur_data = b"1"
                    while cur_data:
                        cur_data = stdout.channel.recv(1024)
                        received_data += cur_data

                    cmd_exec_log += str(received_data)

                if stderr.channel.recv_stderr_ready():
                    received_data = stdout.channel.recv_stderr(1024)
                    cur_data = b"1"
                    while cur_data:
                        cur_data = stdout.channel.recv_stderr(1024)
                        received_data += cur_data

                    cmd_exec_log += str(received_data)
            logger.info(cmd_exec_log)
            return True
        else:
            logger.exception("Connection not opened.")
            return False
