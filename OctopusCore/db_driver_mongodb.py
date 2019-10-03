import database_mongodb as mongo_db
import fusiondb_schema

USERS_COLLECTION_NAME = 'users'
SERVERS_COLLECTION_NAME = 'servers'


class User(fusiondb_schema.User):
    def _start(self):
        self.__key = ''

    def _attempt_setting_key(self, data):
        if 'email' in data:
            self.__key = data['email']

    def _pull(self, data):
        self._attempt_setting_key(data)
        if not self.__key:
            raise AttributeError('Insufficient information to pull')
        db_user = mongo_db.find_one_if_exists({'email': self.__key}, USERS_COLLECTION_NAME)
        if db_user is None:
            raise AttributeError('Pull failed. Is your key valid?')
        db_user.pop('_id')
        return db_user

    def _push(self, new_data, data):
        self._attempt_setting_key(data)
        if not self.__key:
            raise AttributeError('Specify identifying props to push')
        if new_data:
            return mongo_db.update_one_document_values({'email': self.__key}, new_data, USERS_COLLECTION_NAME)
        else:
            return True

    def _create(self, data):
        self._attempt_setting_key(data)
        if not self.__key:
            raise AttributeError('User must have email set to create')
        if mongo_db.create_document(data, USERS_COLLECTION_NAME):
            return True
        else:
            return False

    def _exists(self, data):
        self._attempt_setting_key(data)
        if not self.__key:
            raise AttributeError('Set email to check existence')
        return mongo_db.exists_once_or_not({'email': self.__key}, USERS_COLLECTION_NAME)


class Server(fusiondb_schema.Server):
    def _start(self):
        self.__key = ''

    def _attempt_setting_key(self, data):
        if 'owner_email' in data and 'provider' in data and 'id' in data:
            self.__key = data['owner_email'] + ';' + data['provider'] + ';' + data['id']

    def _pull(self, data):
        self._attempt_setting_key(data)
        if not self.__key:
            raise AttributeError('Insufficient information to pull')
        db_server = mongo_db.find_one_if_exists({'key': self.__key}, SERVERS_COLLECTION_NAME)
        if db_server is None:
            raise AttributeError('Pull failed. Is your key valid?')
        split_key = db_server['key'].split(';')
        db_server['owner_email'] = split_key[0]
        db_server['provider'] = split_key[1]
        db_server['id'] = split_key[2]
        db_server.pop('_id')
        db_server.pop('key')
        return db_server

    def _push(self, new_data, data):
        self._attempt_setting_key(data)
        if not self.__key:
            raise AttributeError('Specify identifying props to push')
        if new_data:
            return mongo_db.update_one_document_values({'key': self.__key}, new_data, SERVERS_COLLECTION_NAME)
        else:
            return True

    def _create(self, data):
        self._attempt_setting_key(data)
        # Refer to Datastore driver for description of logic here.
        owner_email = data['owner_email']
        provider = data["provider"]
        server_id = str(data['id'])
        data.pop('owner_email')
        data.pop('provider')
        data.pop('id')
        if not self.__key:
            raise AttributeError('Server must have owner_email, provider and id set to create')
        data['key'] = self.__key
        if mongo_db.create_document(data, SERVERS_COLLECTION_NAME):
            owner = User(email=owner_email)
            owner.pull()
            owner.servers.append([provider, server_id])
            if owner.push():
                return True
            else:
                return False
        else:
            return False

    def _delete(self, data):
        self._attempt_setting_key(data)
        # The usual .delete, but we have to remove the reference we added to User.servers before
        if not self.__key:
            raise AttributeError('Set owner_email, provider and id to delete')

        mongo_db.delete_one_document({'key': self.__key}, SERVERS_COLLECTION_NAME)

        # Now fetch user and remove the reference
        owner = User(email=data['owner_email'])
        owner.pull()
        try:
            owner.servers.remove([data['provider'], data['id']])
        except ValueError:  # This is more of an internal endpoint. Provisioner should have already checked
            return False  # So just fail
        return owner.push()

    def _exists(self, data):
        self._attempt_setting_key(data)
        if not self.__key:
            raise AttributeError('Set owner_email, provider and id to check existence')
        return mongo_db.exists_once_or_not({'key': self.__key}, SERVERS_COLLECTION_NAME)
