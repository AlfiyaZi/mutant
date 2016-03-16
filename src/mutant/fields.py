import logging


logger = logging.getLogger(__name__)


def make_custom_field_type(entity):
    return type('ForeignKey', (ForeignKeyBase,), dict(entity=entity))


class BaseField(object):
    def __init__(self, name, **kwargs):
        super(BaseField, self).__init__()
        self.name = name
        self.options = kwargs

    def __repr__(self):
        return u'<{0} {1}>'.format(self.__class__.__name__, self.name)


class ForeignKeyBase(BaseField):
    def __init__(self, **kwargs):
        super(ForeignKeyBase, self).__init__(**kwargs)
        self.options['entity'] = self.entity.name


class StringField(BaseField):
    pass


class EmailField(StringField):
    pass


class TextField(BaseField):
    pass


class IntegerField(BaseField):
    pass


class DateField(BaseField):
    pass


class ListField(BaseField):
    pass


def register(app):
    fields = {
        'String': StringField,
        'Text': TextField,
        'Email': EmailField,
        'Integer': IntegerField,
        'Date': DateField,
        'ForeignKey': ForeignKeyBase,
        'List': ListField,
    }
    for name, field in fields.items():
        app.register_field(name, field)
