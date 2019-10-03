from fields import *

INVALID_VALIDATOR_ERROR = 'Only JSONValidator validators (must descend from Exists), OR(...) and AND(...) are supported'
NO_VALIDATORS_ERROR = 'No validators specified'


class _ORValidator(Field):
    def _start(self, *args):
        self.validators = None

    def validate(self, value):
        # We assume self.validators is correct as OR(...) must have checked it
        # Simple OR evaluation of contained fields
        for item in self.validators:
            if item.validate(value):
                return True
        return False


# noinspection PyPep8Naming
def OR(*args, **kwargs):
    """
    Returns an "metavalidator" which will be equivalent to a logical OR operation on validators listed in *args
    :param args: validators to run the operation on
    :param kwargs: optional and name as with any normal validator
    :return: OR metavalidator
    :rtype: _ORValidator
    """
    optional, custom_name = parse_field_kwargs(kwargs)
    if args:
        for arg in args:
            if not isinstance(arg, Field):
                raise AttributeError(INVALID_VALIDATOR_ERROR)

        combined_validator = _ORValidator(optional=optional, name=custom_name)
        # Since we just verified all *args are all valid instances of Field:
        combined_validator.validators = args
        return combined_validator

    else:
        raise AttributeError(NO_VALIDATORS_ERROR)


class _ANDValidator(Field):
    def _start(self, *args):
        self.validators = None

    def validate(self, value):
        # We assume self.validators is correct as AND(...) must have checked it
        # Simple AND evaluation of contained fields
        for item in self.validators:
            if not item.validate(value):
                return False
        return True


# noinspection PyPep8Naming
def AND(*args, **kwargs):
    """
    Returns an "metavalidator" which will be equivalent to a logical AND operation on validators listed in *args
    :param args: validators to run the operation on
    :param kwargs: optional and name as with any normal validator
    :return: AND metavalidator
    :rtype: _ANDValidator
    """
    optional, custom_name = parse_field_kwargs(kwargs)
    if args:
        for arg in args:
            if not isinstance(arg, Field):
                raise AttributeError(INVALID_VALIDATOR_ERROR)

        combined_validator = _ANDValidator(optional=optional, name=custom_name)
        # Since we just verified all *args are all valid instances of Field:
        combined_validator.validators = args
        return combined_validator

    else:
        raise AttributeError(NO_VALIDATORS_ERROR)


class JSONValidatorData(object):
    pass


KEY_BLACKLIST = ['validate', 'data', 'raw_data', 'errors']


class JSONValidator(object):
    """
    A parent class for JSON validation templates.
    Takes a python dict as *arg[0] or as self.raw_data
    Validates raw_data in accordance with defined validators (Descending from Field) on call to self.validate
    all errors are appended to self.errors list
    True is returned if all data is valid, False is returned otherwise.
    note: JSON commonly formats data into {"name":"value"} pairs. Here, the "name" part is referred to as "key"
    """

    def __init__(self, raw_data=None):
        """
        :param dict raw_data: Python dict with json data to validate
        """
        self.raw_data = raw_data
        self.errors = []
        self._data = {}
        self._required_keys = set()
        self._map = {}  # maps ("json") key name to (real) Field instance
        self._name_map = {}  # maps ("json") key name to python class property name (aka key in self._data)
        for prop_name in dir(self):
            if not prop_name.startswith('_') and prop_name not in KEY_BLACKLIST:
                prop = object.__getattribute__(self, prop_name)  # Avoid our faking __getattribute__ and use object
                if isinstance(prop, Field):
                    if prop.custom_name:
                        self._map[prop.custom_name] = prop
                        self._name_map[prop.custom_name] = prop_name
                        if not prop.optional:
                            self._required_keys.add(prop.custom_name)
                    else:
                        self._map[prop_name] = prop
                        self._name_map[prop_name] = prop_name
                        if not prop.optional:
                            self._required_keys.add(prop_name)

    def __getattribute__(self, item):
        """
        Process most requests through normal object.__getattribute__
        APART FROM:
        - If any fields are requested, their *processed* value (or None if not present) is returned
        - If 'data' is requested the data dict is returned
        """
        if item == 'data':
            return self._data
        prop = object.__getattribute__(self, item)
        if isinstance(prop, Field):
            # noinspection PyUnresolvedReferences
            return self._data.get(item)
        return prop

    def validate(self):
        """
        Check *all* fields and put all errors in self.errors. However, if ANY errors occur validation will fail
        (But all the fields will still be checked and all the errors will still be listed)
        (Done to simplify developers' lives)
        :return: True if all fields are valid, False otherwise
        :rtype: bool
        """
        failed = False

        # Yes it is shadowing outer scope, but it always = outer scope validator, so
        # noinspection PyShadowingNames
        def run_validator(validator, key_name, data):
            if validator.validate(data):
                return True
            else:
                if data == '':  # Just make it clear when we give user an error
                    data = '*emptystring*'
                self.errors.append('{} is an invalid value for key {}'.format(data, key_name))
                return False

        if not self.raw_data:
            self.errors.append('No valid json data provided')  # We get passed data from flask's get_json(),
            # but our errors are going directly to user, so we must refer to JSON.
            return False
        else:
            if not isinstance(self.raw_data, dict):
                self.errors.append('Data is not a valid json object')  # see above for the "JSON" deal
                return False

        # noinspection PyUnresolvedReferences
        required_keys_not_present = self._required_keys - set(self.raw_data.keys())
        if required_keys_not_present:
            # Make a more readable list of keys rather than just dumping the ugly str(set(...))
            required_keys_not_present_list_str = ','.join(
                ['{}'.format(key_name) for key_name in required_keys_not_present])
            self.errors.append(
                'The following keys are required, but not present: {}'.format(required_keys_not_present_list_str)
            )
            failed = True

        # noinspection PyTypeChecker
        for key_name, value in self.raw_data.viewitems():
            # Here extra care is taken to ensure we only touch Field instances
            # just in case a method or property slipped into ._map somehow

            # disabled as this (predictably) breaks keys starting with _ which can be in use
            # if key.startswith('_'):  # Do not even attempt resolving what could be a private/protected property
            #     # as this must be a reverse engineering attempt
            #     prop = None
            if key_name in KEY_BLACKLIST:
                prop = None
            else:
                # noinspection PyUnresolvedReferences
                prop = self._map.get(key_name)
            if prop:
                if isinstance(prop, Field):
                    if not run_validator(prop, key_name, value):
                        failed = True
                    else:
                        self._data[self._name_map[key_name]] = value
                else:
                    # Throw the same error to prevent reverse engineering
                    self.errors.append(
                        'Key {} is not recognised'.format(key_name))
                    failed = True
            else:
                # Throw the same error to prevent reverse engineering
                self.errors.append('Key {} is not recognised'.format(key_name))
                failed = True

        if failed:
            # This makes sure all of our virtual (fake) self.ValidatorName properties will return None
            self._data = {}

        return not failed


if __name__ == '__main__':
    class TestValidator(JSONValidator):
        bob = IntegerField()
        sob = AND(OR(IntegerField(), AND(StringField(), LimitedLengthField((0, 5)))), Field(), name='snob')

    # noinspection SpellCheckingInspection
    dl = ['invalid', {'bob': 1, 'sob': 1.0, '__init__': 3}, {'bob': 1, 'sob': 1.0}, {'bob': ''},
          {'bob': 5, 'sob': 3},
          {'bob': 5, 'snob': ''}, {'bob': 5, 'sob': '3345g4e35g45e3g3g34eg43g43g34g4343g'}]

    for d in dl:
        validator = TestValidator(d)
        if validator.validate():
            print 'Everything seems good'
        else:
            print validator.errors
