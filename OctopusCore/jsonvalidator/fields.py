def parse_field_kwargs(kwargs):
    """
    Common function to parse, validate kwargs sent to a Field (, OR(...) or AND(...) as they pretend to be Fields)
    :param dict kwargs: **kwargs passed to a Field
    :return: (optional, custom_name)
    :rtype: tuple
    """
    optional = False
    custom_name = None

    # optional and custom_name must be specified
    if len(kwargs) == 2:
        # noinspection PyUnresolvedReferences
        keys = kwargs.keys()
        if 'optional' in keys and 'name' in keys:
            # kwargs['name'] is None means use the python property name aka the default. Used by metafields
            if isinstance(kwargs['optional'], bool) and (isinstance(kwargs['name'], str) or kwargs['name'] is None):
                optional = kwargs['optional']
                custom_name = kwargs['name']
            else:
                raise AttributeError('Invalid **kwargs')
    # only optional or custom_name
    elif len(kwargs) == 1:
        # noinspection PyUnresolvedReferences
        keys = kwargs.keys()
        if 'optional' in keys:
            if isinstance(kwargs['optional'], bool):
                optional = kwargs['optional']
            else:
                raise AttributeError('Invalid **kwargs')
        elif 'name' in keys:
            # kwargs['name'] is None means use the python property name aka the default. Used by metafields
            if isinstance(kwargs['name'], str) or kwargs['name'] is None:
                custom_name = kwargs['name']
            else:
                raise AttributeError('Invalid **kwargs')
        else:
            raise AttributeError('Invalid **kwargs')
    # specifying nothing is ok as well
    elif len(kwargs) == 0:
        pass
    # No junk kwargs allowed!
    else:
        raise AttributeError('Invalid **kwargs')
    return optional, custom_name


class Field:
    def _start(self, *args):
        """
        allows for custom additions to __init__ by children
        """
        pass

    def __init__(self, *args, **kwargs):
        """
        Passes all *args to _start and processes **kwargs via parse_field_kwargs
        """
        self.optional, self.custom_name = parse_field_kwargs(kwargs)
        self._start(*args)

    def validate(self, value):
        """
        Validates provided value for compliance with certain conditions (eg. for IntegerField it must be int)
        Always return True as default
        :param value: Value to run validator on
        :return: True if value is valid, False otherwise
        :rtype: bool
        """
        return True


class IntegerField(Field):
    def validate(self, value):
        return isinstance(value, int)


class FloatField(Field):
    def validate(self, value):
        return isinstance(value, float)


class StringField(Field):
    def validate(self, value):
        return isinstance(value, basestring) and value


class LimitedLengthField(Field):
    def _start(self, length_tuple):
        self.length_tuple = length_tuple

    def validate(self, value):
        # make sure we can do gte or lte without earring out
        if isinstance(value, list) or isinstance(value, dict) or isinstance(value, basestring):
            return self.length_tuple[0] <= len(value) <= self.length_tuple[1]
        # False if instance is incomparable
        else:
            return False


class BooleanField(Field):
    def validate(self, value):
        return isinstance(value, bool)


class DictField(Field):
    def validate(self, value):
        return isinstance(value, dict)


class ListField(Field):
    def validate(self, value):
        return isinstance(value, list)


class InListField(Field):
    # noinspection PyShadowingBuiltins
    def _start(self, list):
        self.list = list

    def validate(self, value):
        return value in self.list
