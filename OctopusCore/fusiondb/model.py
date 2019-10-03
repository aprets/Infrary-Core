import copy
from properties import Property


class Model(object):
    """
    Parent model from which all FusionDB models and drivers descend
    Properties are set on Model (which descends from this)
    eg: name = StringProperty()
    Drivers descend from models and define _pull, _push and optionally:
    _start, _query, _create, _delete, _exists
    User calls methods without _ which ensure "data" dict containing all property data
    is passed to the _methods of the driver
    """
    _mapped = False
    data = {}  # Not the real property (see __getattribute__), just here for correct type hinting

    # noinspection PyArgumentList
    def __new__(cls, *args, **kwargs):
        """
        Map all defined properties and their names.
        Additionally set all **kwargs as properties on self (ie Fill in Properties from **kwargs)
        """
        # using __new__ allows __init__ to be customised
        # it also allows models to seamlessly share mappings:
        if not cls._mapped:
            cls._mapped = True
            cls._map = {}
            cls._inv_map = {}
            for prop_name in dir(cls):
                if not prop_name.startswith('_') and prop_name not in [
                    'get_data', 'pull', 'push', 'find', 'fill_properties_from_dict', 'delete', 'create', 'exists'
                ]:
                    prop = getattr(cls, prop_name)
                    if isinstance(prop, Property):
                        if prop.mapping:
                            cls._map[prop_name] = prop.mapping
                            cls._inv_map[prop.mapping] = prop_name

        # noinspection PyArgumentList
        return object.__new__(cls, *args, **kwargs)

    def _start(self):
        """
        Allows fur custom additions to __init__
        """
        pass

    # noinspection PyTypeChecker
    def __init__(self, **kwargs):
        self._data = {}
        self._last_data = {}
        for key, value in kwargs.viewitems():
            setattr(self, key, value)
        self._start()

    # WARNING! WARNING! ALL kwargs passed to int will be set as properties by the time __init__ is called!!!

    def _verify_property(self, name, value, prop=None):
        """
        Error out if supplied value is invalid for the property
        :param str name: prop name
        :param value: value
        :param Property prop: Property instance (Optional)
        :return: None
        :rtype: None
        """
        if prop is None:
            prop = object.__getattribute__(self, name)
        if not prop.verify(value):
            raise ValueError(
                'In {}: {} {} is not supported by {}'.format(name, value, type(value), prop.__class__.__name__))

    def __setattr__(self, name, value):
        """
        Intercept __setattr__ calls for existing properties which are instances of Property
        when we catch those, we apply them to the ._data dict instead
        this way a user can write fdb_model.property = something
        and we will set something as our ._data[property] value. Mind that mapping may apply so _data key != property
        """

        try:
            prop = object.__getattribute__(self, name)  # Again, ignore our __getattribute__
        except AttributeError:
            object.__setattr__(self, name, value)  # Handle in default way
        else:
            if isinstance(prop, Property):
                self._verify_property(name, value, prop=prop)  # Aka error out if value invalid
                self._data[name] = value
            else:
                object.__setattr__(self, name, value)

    def get_data(self):  # analogous to self.data (see __getattribute__)
        """
        Returns internal data as dict
        :return: model data as dict
        :rtype: dict
        """
        return self._data

    def __getattribute__(self, item):
        """
        Intercept __getattribute__ calls for existing properties which are instances of Property
        when we catch those, we apply them to the ._data dict instead
        this way a user can write something = fdb_model.property and we will get property value from ._data
        returns None if _data value not (yet) present
        """
        if item == 'data':
            return self.get_data()
        prop = object.__getattribute__(self, item)
        if isinstance(prop, Property):
            # noinspection PyUnresolvedReferences
            return self._data.get(item)
        return prop

    def fill_properties_from_dict(self, inp_dict, do_reverse_mapping=False):
        """
        The name is very indicative... maps dict[key] = value to self.key = value
        :param dict inp_dict: Dict to map
        :param bool do_reverse_mapping: if True, keys will be ran through ._inv_map
        :return: None (Always)
        :rtype: None
        """
        # noinspection PyTypeChecker
        for key, value in inp_dict.viewitems():
            if not do_reverse_mapping or not self._inv_map:
                setattr(self, key, value)
            else:
                # noinspection PyUnresolvedReferences
                translated_key = self._inv_map.get(key)
                if translated_key:
                    setattr(self, translated_key, value)
                else:
                    setattr(self, key, value)

    @staticmethod
    def _dict_diff(new, old):
        """
        Return the difference between new and old dicts
        A difference is considered:
         - A missing key
         - A key with a new value
        :param dict new: dict which is the origin of the diff (ie containing newest data)
        :param old: dict which is a previous state of new
        :return: diff of new and old
        :rtype: dict
        """
        diff_dict = {}
        for key, value in new.viewitems():
            if key in old:
                if not old[key] == value:
                    diff_dict[key] = value
            else:
                diff_dict[key] = value
        return diff_dict

    def _translate_data(self, data):
        """
        Translates key names if DB driver facing key names are different from python
        """
        if not self._map:
            translated = data
        else:
            translated = {}
            if data:
                for key, value in data.viewitems():
                    # noinspection PyUnresolvedReferences
                    translated_key = self._map.get(key)
                    if translated_key:
                        translated[translated_key] = value
                    else:
                        translated[key] = value
        return translated

    # noinspection PyTypeChecker
    def _get_translated_commit(self):
        # noinspection PyTypeChecker
        diffed_commit = self._dict_diff(self._data, self._last_data)
        return self._translate_data(diffed_commit)

    def _get_translated_data(self):
        return self._translate_data(self._data)

    def _pull(self, data):
        raise AttributeError('Base model does not support pull')

    # noinspection PyAttributeOutsideInit
    def pull(self):
        """
        Fetch data about self from database
        Will fail if not enough identifying info is set
        """
        raw_data = self._pull(self._get_translated_data())
        translated_data = {}
        if self._inv_map:
            for key, value in raw_data.viewitems():
                # noinspection PyUnresolvedReferences
                translated_key = self._inv_map.get(key)
                if translated_key:
                    translated_data[translated_key] = value
                    self._verify_property(translated_key, value)
                else:
                    translated_data[key] = value
                    self._verify_property(key, value)
        else:
            for key, value in raw_data.viewitems():
                self._verify_property(key, value)
            translated_data = raw_data
        self._data = translated_data
        self._last_data = copy.deepcopy(self._data)

    def _push(self, new_data, data):
        raise AttributeError('Base model does not support push')

    def push(self):
        """
        Push all the changes in model to DB
        Will fail if not enough identifying info is set
        :return: if push succeeded
        :rtype: bool
        """
        result = self._push(self._get_translated_commit(), self._get_translated_data())
        if result:
            # noinspection PyAttributeOutsideInit
            self._last_data = copy.deepcopy(self._data)
        return result

    def _find(self, **kwargs):
        raise AttributeError('Find is not supported')

    # noinspection PyArgumentList
    def find(self, **kwargs):
        # noinspection PyUnresolvedReferences
        if not kwargs or (len(kwargs) == 1 and 'pull' in kwargs.keys()):
            raise AttributeError('Please specify a property')
        return self._find(**kwargs)

    def _create(self, data):
        raise AttributeError('Create is not supported')

    def create(self):
        """
        Will fail if not enough identifying info is set
        :return: True if entity created successfully
        :rtype: bool
        """
        return self._create(self._get_translated_data())

    def _delete(self, data):
        raise AttributeError('Delete is not supported')

    def delete(self):
        """
        Will fail if not enough identifying info is set
        :return: True if entity deleted successfully
        :rtype: bool
        """
        return self._delete(self._get_translated_data())

    def _exists(self, data):
        raise AttributeError('Exists is not supported')

    def exists(self):
        """
        Will fail if not enough identifying info is set
        :return: True if entity exists in db
        :rtype: bool
        """
        return self._exists(self._get_translated_data())
