import logging


logger = logging.getLogger(__name__)


def make_custom_field_type(entity):
    return type('ForeignKey', (ForeignKeyBase,), dict(entity=entity))


class BaseField(object):
    typename = None

    def __init__(self, name, **kwargs):
        super(BaseField, self).__init__()
        self.name = name
        self.options = kwargs

    def __repr__(self):
        return u'<{0} {1}>'.format(self.__class__.__name__, self.name)


class ForeignKeyBase(BaseField):
    typename = "ForeignKey"

    def __init__(self, **kwargs):
        kwargs.setdefault('entity', self.entity.name)
        super(ForeignKeyBase, self).__init__(**kwargs)


class StringField(BaseField):
    typename = "String"


class EmailField(StringField):
    typename = "Email"


class TextField(BaseField):
    typename = "Text"


class IntegerField(BaseField):
    typename = "Integer"


class DateField(BaseField):
    typename = "Date"


class ListField(BaseField):
    typename = "List"


def register(app):
    for cls in (StringField, EmailField, TextField, IntegerField, DateField, ListField):
        app.register_field(cls.typename, cls)
    app.register_field('ForeignKey', ForeignKeyBase)
    app.register_field_maker(make_custom_field_type)
