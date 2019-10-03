import yaml


class InfraryComposeParser(object):
    def __init__(self, raw_data=None):
        self.raw_data = None
        self.parsed_data = None
        self._master = None
        self._servers = []
        self._stacks = []
        self.error = None
        if raw_data:
            self.raw_data = raw_data

    @property
    def master(self):
        if not self.error:
            return self._master
        else:
            return None

    @property
    def servers(self):
        if not self.error:
            return self._servers
        else:
            return None

    @property
    def stacks(self):
        if not self.error:
            return self._stacks
        else:
            return None

    def _parse_yaml(self):
        try:
            if not self.raw_data:
                self.error = 'YAML empty!'
                return False
            self.parsed_data = yaml.safe_load(self.raw_data)
            return True
        except yaml.YAMLError as e:
            self.error = str(e)
            return False

    def parse(self):

        self.__init__(raw_data=self.raw_data)

        try:

            def verify_blocks(data, block_names, wanted_class=dict, allow_empty=False):
                """

                :param data:
                :param block_names:
                :param object wanted_class:
                :param allow_empty:
                :return:
                """
                for block_name in block_names:
                    block = data.get(block_name)
                    # noinspection PyTypeChecker
                    if not isinstance(block, wanted_class):
                        self.error = 'Cannot parse {}'.format(block_name)
                        return False
                    else:
                        if not block and not allow_empty:
                            self.error = '{} is empty'.format(block_name)
                            return False

            if not self._parse_yaml():
                return False

            if self.parsed_data.get('version') != '0':
                self.error = 'Invalid compose version'
                return False

            verify_blocks(self.parsed_data, ['servers', 'stacks'])

            for server_name, server in self.parsed_data['servers'].viewitems():
                verify_blocks(server, ['properties', 'configuration'])
                verify_blocks(
                    server['properties'],
                    ['provider', 'token', 'size', 'image', 'location', 'ssh_key'],
                    basestring
                )
                verify_blocks(server['configuration'], ['is_master', 'self_destruct'], bool, allow_empty=True)
                verify_blocks(server['configuration'], ['cmd_list'], list, allow_empty=True)
                if server['configuration']['is_master']:
                    server['properties']['name'] = server_name
                    self._master = server
                else:
                    server['properties']['name'] = server_name
                    self._servers.append(server)

            if not self._master:
                self.error = 'No master server specified!'
                return False

            for stack_name, stack in self.parsed_data['stacks'].viewitems():
                verify_blocks(stack, ['docker-compose', 'rancher-compose'])
                stack['name'] = stack_name
                self._stacks.append(stack)

            return True

        except (AttributeError, ValueError):
            self.error = 'Unknown error parsing infrary-compose'
            return False
