import logging


logger = logging.getLogger(__name__)


def make_custom_field_type(entity):
    return type('ForeignKey', (MUTANT_FIELDS['ForeignKey'],), dict(entity=entity))


class BaseField(object):
    def __init__(self, name, **kwargs):
        super(BaseField, self).__init__()
        self.name = name
        self.options = kwargs

    # def render(self, template):
    #     logger.debug(dict(field_name=self.name, field_type=self.options))
    #     return template.render(field_name=self.name, field_type=self.options)

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


class IntegerField(BaseField):
    pass


class DateField(BaseField):
    pass


class ListField(BaseField):
    pass


MUTANT_FIELDS = {
    'String': StringField,
    'Email': EmailField,
    'Integer': IntegerField,
    'Date': DateField,
    'ForeignKey': ForeignKeyBase,
    'List': ListField,
}
