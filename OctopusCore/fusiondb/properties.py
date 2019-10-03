import datetime


class Property:
    def __init__(self, mapping=None):
        self.mapping = mapping

    @staticmethod
    def verify(value):
        return True


class IntegerProperty(Property):
    @staticmethod
    def verify(value):
        return isinstance(value, int)


class FloatProperty(Property):
    @staticmethod
    def verify(value):
        return isinstance(value, float)


class StringProperty(Property):
    @staticmethod
    def verify(value):
        return isinstance(value, basestring)


class BooleanProperty(Property):
    @staticmethod
    def verify(value):
        return isinstance(value, bool)


class DictProperty(Property):
    @staticmethod
    def verify(value):
        return isinstance(value, dict)


class ListProperty(Property):
    @staticmethod
    def verify(value):
        return isinstance(value, list)


class DateTimeProperty(Property):
    @staticmethod
    def verify(value):
        return isinstance(value, datetime.datetime)
