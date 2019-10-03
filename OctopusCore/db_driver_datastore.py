import datetime

import database_datastore
import fusiondb_schema
from database_datastore import ndb as ndb


class User(fusiondb_schema.User):
    def _start(self):
        # This is an instance of Google Datastore NextDB "model" (Acts similar to ORM instance)
        # We just set it to None to indicate we never pulled yet and there is no active model
        self.__ndb_ent = None

    def _pull(self, data):
        if self.__ndb_ent:
            # Google does not like multiple pulls, so we just reuse the NDB model
            # (Since NDB will do diffing and caching anyway.)
            pass
        elif 'email' in data:
            # Pull by key aka email
            self.__ndb_ent = ndb.Key(database_datastore.User, str(data['email'])).get()
            if self.__ndb_ent is None:
                raise AttributeError('Pull failed. Is your key valid?')
        else:
            raise AttributeError('Insufficient information to pull')
        new_data = self.__ndb_ent.to_dict()
        # Since .to_dict() does not include keys
        new_data['email'] = self.__ndb_ent.key.string_id()
        return new_data

    def _push(self, new_data, data):
        if not self.__ndb_ent:
            # NDB cannot "push" without fetching the data, so just do a pull and directly call self with new_data
            # since we know it will be the only change (so no need to diff) [NDB will diff itself anyway]
            self.pull()
            return self._push(new_data, data)
        else:
            if 'email' in new_data:
                new_data.pop('email')  # Email is a key so we remove it from properties we will set
            for key, value in new_data.viewitems():
                setattr(self.__ndb_ent, key, value)  # Don't mess with NDB's internal ._data etc. this is safer
            return self.__ndb_ent.put()  # Equivalent to our .push()

    def _create(self, data):
        if 'email' not in data:
            raise AttributeError('User must have email set to create')
        # This will fetch the user aka give us the same model instance as with Key(...).get()
        self.__ndb_ent = database_datastore.User(id=data['email'])
        # Again email is a key so is not going to properties
        data.pop('email')
        for key, value in data.viewitems():
            setattr(self.__ndb_ent, key, value)
        if self.__ndb_ent.put():
            return True
        else:
            return False

    def _exists(self, data):
        if 'email' not in data:
            raise AttributeError('Set email to check existence')
        # By setting self.__ndb_ent if a pull is ever done on us again the model will be reused so no 2nd fetch will
        # happen
        try:
            self.__ndb_ent = ndb.Key(database_datastore.User, str(data['email'])).get()
        except:
            return False
        return self.__ndb_ent is not None


class Server(fusiondb_schema.Server):
    def _start(self):
        # Exactly the same as in User
        self.__ndb_ent = None

    def _pull(self, data):
        if self.__ndb_ent:
            # Again, just like in User we avoid repulling the model
            pass
        # We need all 3 as they all combine to make our user key
        # This way no queries are ever needed as we can always know exactly what the unique server key is
        elif 'owner_email' in data and 'provider' in data and 'id' in data:
            self.__ndb_ent = ndb.Key(
                # This is one of the ways to create a "combo" key.
                # referred to by Google as "Using the ancestor path in the key"
                # See:
                # https://cloud.google.com/appengine/docs/standard/python/ndb
                # /creating-entity-keys#using_the_ancestor_path_in_the_key
                # So here we use a sequence of kind-identifier pairs  to get the whole key
                'User', data['owner_email'],
                'Provider', data['provider'],
                'Server', str(data['id'])
            ).get()
            if self.__ndb_ent is None:
                raise AttributeError('Pull failed. Is your key valid?')
        else:
            raise AttributeError('Insufficient information to pull')
        new_data = self.__ndb_ent.to_dict()
        # Again, put parts of key back into new_data as .to_dict() will not give them to us
        new_data['owner_email'] = self.__ndb_ent.key.flat()[1]
        new_data['provider'] = self.__ndb_ent.key.flat()[3]
        new_data['id'] = self.__ndb_ent.key.string_id()
        return new_data

    def _push(self, new_data, data):
        # Virtually the same as User only more key parts to remove from properties
        if not self.__ndb_ent:
            self.pull()
            return self._push(new_data, data)
        else:
            if 'owner_email' in new_data:
                new_data.pop('owner_email')
            if 'provider' in new_data:
                new_data.pop('provider')
            if 'id' in new_data:
                new_data.pop('id')
            for key, value in new_data.viewitems():
                setattr(self.__ndb_ent, key, value)
            return self.__ndb_ent.put()

    def _create(self, data):
        if 'owner_email' not in data or 'provider' not in data or 'id' not in data:
            raise AttributeError('Server must have owner_email, provider and id set to create')

        # This is a bit different to User. Driver is schema-aware and hides us having to add new servers to User.servers
        # as there is no inherent link between User.servers and actual Server entities
        # even though Server uses key of User as part of its own key.
        # It's much better saving server "references" to User.servers than running a query every time
        # which is much more expensive (in all senses) in datastore.
        # We persist our key parts here as we try creating Server first and if everything goes ok, we add a reference
        # to User (as you notice key parts = user key + reference (provider + server_id) )
        # This is much safer as:
        # 1. Things are much more likely to go wrong here (more complexity, new key)
        # 2. If no reference exists, the app is oblivious to server's existence rather than freaking out
        owner_email = data['owner_email']
        provider = data["provider"]
        server_id = str(data['id'])
        data.pop('owner_email')
        data.pop('provider')
        data.pop('id')

        # Usual Server creation using the "combo" key
        user_key = ndb.Key(database_datastore.User, owner_email)
        provider_key = ndb.Key('Provider', provider, parent=user_key)
        self.__ndb_ent = database_datastore.Server(id=server_id, parent=provider_key)
        for key, value in data.viewitems():
            setattr(self.__ndb_ent, key, value)
        if self.__ndb_ent.put():
            # Now if everything went right, we get owner and add the server reference
            owner = User(email=owner_email)
            # This pull would usually be bad (especially when logic repeats it straight away),
            # but NDB auto-caches (And even auto-batches) extensively so it is not a problem.
            owner.pull()
            owner.servers.append([provider, server_id])
            if owner.push():
                return True
            else:
                return False
        else:
            return False

    def _delete(self, data):
        # The usual .delete, but we have to remove the reference we added to User.servers before
        if 'owner_email' not in data or 'provider' not in data or 'id' not in data:
            raise AttributeError('Set owner_email, provider and id to delete')
        ndb.Key('User', data['owner_email'], 'Provider', data['provider'], 'Server',
                str(data['id'])).delete()
        # Now fetch user and remove the reference
        owner = User(email=data['owner_email'])
        # Again same story with the pull() as before
        owner.pull()
        try:
            owner.servers.remove([data['provider'], data['id']])
        except ValueError:  # This is more of an internal endpoint. Provisioner should have already checked
            return False
        return owner.push()

    def _exists(self, data):
        # Exactly the same as in User. Just more key parts...
        if 'owner_email' not in data or 'provider' not in data or 'id' not in data:
            raise AttributeError('Set owner_email, provider and id to check existence')
        try:
            self.__ndb_ent = ndb.Key('User', data['owner_email'], 'Provider', data['provider'], 'Server',
                                     str(data['id'])).get()
        except:
            return False
        return self.__ndb_ent is not None


# noinspection PyPep8
def tmp_user_cleanup():
    # noinspection PyPep8 as this in not really going to be compared by Python, but by ndb (which does not support "is")
    list_of_keys = database_datastore.User.query(
        ndb.AND(
            database_datastore.User.created_at <= (datetime.datetime.utcnow() - datetime.timedelta(hours=2)),
            database_datastore.User.is_active == False
        )
    ).fetch(keys_only=True)
    if list_of_keys:
        if ndb.delete_multi(list_of_keys):
            return True
        else:
            return False
    else:
        return True
