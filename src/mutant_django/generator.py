import itertools
import logging

import inflect
from six import string_types

from mutant.generators.base import BaseGenerator
from mutant.generators.utils import JinjaFieldGenerator
from .templates import DJANGO_FILE_TEMPLATE, DJANGO_MODEL_TEMPLATE, DJANGO_FIELD_TEMPLATE


logger = logging.getLogger(__name__)


SIMPLE_MAPPINGS = (
    'Auto',
    'BigInteger',
    'Binary',
    'Boolean',
    'Char',
    'CommaSeparatedInteger',
    'Date',
    'Decimal',
    'Duration',
    'Email',
    'File',
    'FilePath',
    'Float',
    'GenericIPAddress',
    'Image',
    'Integer',
    'NullBoolean',
    'PositiveInteger',
    'PositiveSmallInteger',
    'Slug',
    'SmallInteger',
    'Text',
    'Time',
    'URL',
    'UUID',
)


class DjangoSchemaGenerator(BaseGenerator):
    def __init__(self, schema, *args, **kwargs):
        self.entities = schema
        super(DjangoSchemaGenerator, self).__init__(*args, **kwargs)
        self.field_generators = {
            'String': DjangoString,
            'Email': DjangoEmail,
            'Link': DjangoForeignKey,
            'List': DjangoList,
            'Datetime': DjangoDatetime,
        }
        self.field_generators.update({
            typename: create_simple_mapping_field(typename)
            for typename in SIMPLE_MAPPINGS
        })

    def render(self):
        return DJANGO_FILE_TEMPLATE.render(entities=self._renderers())

    def _renderers(self):
        entity_renderers = self.create_field_generators()
        self.create_additional_renderers(entity_renderers)
        self.transfer_foreign_keys(entity_renderers)
        return entity_renderers

    def create_field_generators(self):
        entity_renderers = []
        for entity in self.entities:
            fgs = []
            for field in entity['fields']:
                if field['type'] in self.field_generators:
                    fgs.append(self.field_generators[field['type']].for_field(field))
                else:
                    raise KeyError("Unknown Django field type '{0}': {1} in entity {2}"
                                   .format(field['type'], field, entity['name']))
            entity_renderers.append(DjangoEntity(entity['name'], fgs, entity['options']))
        return entity_renderers

    def create_additional_renderers(self, entity_renderers):
        for renderer in list(entity_renderers):
            entity_renderers.extend(renderer.additional_renderers())

    def transfer_foreign_keys(self, entity_renderers):
        transfers = []
        for renderer in entity_renderers:
            transfers.extend(renderer.transfer_foreign_keys())
        for entity_name, new_field in transfers:
            for renderer in entity_renderers:
                if renderer.entity_name == entity_name:
                    renderer.fields.append(new_field)
                    break


class DjangoEntity(object):
    def __init__(self, entity_name, fields, options=None):
        self.entity_name = entity_name
        self.fields = fields
        self.options = options or []

    def render(self):
        logger.debug(self.__dict__)
        return DJANGO_MODEL_TEMPLATE.render(
            name=self.entity_name,
            fields=self.fields,
            model_meta=self.model_meta(),
            # options=self.entity_options
        )

    def additional_renderers(self):
        return itertools.chain.from_iterable(
            field.additional_renderers(self.entity_name)
            for field in self.fields
        )

    def transfer_foreign_keys(self):
        return itertools.chain.from_iterable(
            field.transfer_foreign_keys(self.entity_name)
            for field in self.fields
        )

    def model_meta(self):
        lines = []
        for option in self.options:
            if 'verbose_name_plural' in option:
                break
        else:
            self.options.append({'verbose_name_plural': plural(self.entity_name)})
        for option in self.options:
            name, values = next(iter(option.items()))
            if name == 'unique_together':
                lines.append('{0} = {1}'.format(name, values))
            elif name == 'verbose_name_plural':
                lines.append('{0} = "{1}"'.format(name, values))
        return lines

    def __repr__(self):
        return u'<{0} {1}>'.format(self.__class__.__name__, self.entity_name)


class DjangoBase(JinjaFieldGenerator):
    template = DJANGO_FIELD_TEMPLATE
    DJANGO_ATTRIBUTES = (
        ('primary_key', False),
        ('null', False),
        ('blank', False),
        ('choices', False),
        ('db_column', None),
        ('db_index', None),
        ('db_tablespace', None),
        ('default', None),
        ('editable', True),
        ('error_messages', None),
        ('help_text', None),
        ('unique', False),
        ('unique_for_date', False),
        ('unique_for_month', False),
        ('unique_for_year', False),
        ('verbose_name', None),
    )
    PROXY_ATTRIBUTES = ()
    DJANGO_FIELD = None
    MUTANT_DEFAULTS = ()

    def __init__(self, name, options=None):
        super(DjangoBase, self).__init__(name, options)
        for key, value in dict(self.MUTANT_DEFAULTS).items():
            self.options.setdefault(key, value)
        if 'choices' in self.options:
            self.choices = DjangoChoices(name, self.options)
            self.options['choices'] = self.choices.attribute_value()
        self.options.update({
            'django_field': self.DJANGO_FIELD,
            'django_positional': self.django_positional(),
            'django_attributes': self.django_attributes(),
        })

    @classmethod
    def for_field(cls, field):
        options = {
            key: field['options'][key]
            for key, default_value in (cls.DJANGO_ATTRIBUTES + cls.PROXY_ATTRIBUTES)
            if key in field['options']
        }
        return cls(name=field['name'], options=options)

    @staticmethod
    def quote(key, value):
        if isinstance(value, string_types):
            if key in ('on_delete', 'choices'):
                return value
            else:
                return '"{0}"'.format(value)
        else:
            return value

    def django_positional(self):
        return []

    def django_attributes(self):
        return [
            (key, self.quote(key, self.options[key]))
            for key, default_value in self.DJANGO_ATTRIBUTES
            if key in self.options and self.options[key] != default_value
        ]

    def additional_renderers(self, *args, **kwargs):
        return []

    def transfer_foreign_keys(self, *args, **kwargs):
        return []

    def render_choices(self):
        if hasattr(self, 'choices'):
            return self.choices.render_choices()
        else:
            return ''


class DjangoChoices(object):
    def __init__(self, name, options):
        self.name = name
        self.choices = options['choices']
        self.plural_name = plural(self.name).upper()

    def render_choices(self):
        name = self.name.upper()
        result = []
        for choice in self.choices:
            result.append('{0}_{1} = "{1}"'.format(name, choice.replace(' ', '_').upper()))
        result.append("{0} = (".format(self.plural_name))
        for choice in self.choices:
            result.append('    ({0}_{1}, "{2}"),'.format(name, choice.replace(' ', '_').upper(), choice))
        result.append(")")
        return ''.join(['    ' + line + '\n'
                        for line in result])

    def attribute_value(self):
        return self.plural_name


class DjangoForeignKey(DjangoBase):
    DJANGO_FIELD = "ForeignKey"
    DJANGO_ATTRIBUTES = DjangoBase.DJANGO_ATTRIBUTES + (
        ('on_delete', None),
        # ('model', None),
    )
    PROXY_ATTRIBUTES = (
        ('entity', None),
    )
    MUTANT_DEFAULTS = DjangoBase.MUTANT_DEFAULTS + (
        ('on_delete', 'CASCADE'),
    )

    def django_attributes(self):
        self.options['on_delete'] = "models.{0}".format(self.options['on_delete'])
        return super(DjangoForeignKey, self).django_attributes()

    def django_positional(self):
        return [self.quote(None, self.options['entity'])]


class DjangoList(DjangoBase):
    DJANGO_FIELD = None
    DJANGO_ATTRIBUTES = DjangoBase.DJANGO_ATTRIBUTES + (
        ('on_delete', None),
    )
    PROXY_ATTRIBUTES = (
        ('entity', None),
        ('own', False),
    )
    MUTANT_DEFAULTS = DjangoBase.MUTANT_DEFAULTS + (
        ('on_delete', 'CASCADE'),
    )

    def render(self):
        return ''

    def additional_renderers(self, entity):
        if self.options.get('own'):
            return []
        else:
            return [self.many_to_many(entity)]

    def many_to_many(self, entity_name):
        from_name = entity_name.lower()
        to_name = singular(self.name)
        m2m_from = DjangoForeignKey(from_name, {'entity': entity_name, 'primary_key': True})
        m2m_to = DjangoForeignKey(to_name, {'entity': self.options['entity'], 'primary_key': True})
        return DjangoEntity(
            entity_name=entity_name + self.options['entity'],
            fields=[m2m_from, m2m_to],
        )

    def transfer_foreign_keys(self, entity_name):
        if self.options.get('own'):
            return [self.one_to_many(entity_name)]
        else:
            return []

    def one_to_many(self, entity_name):
        to_name = entity_name.lower()
        new_field = DjangoForeignKey(to_name, {'entity': entity_name})
        return self.options['entity'], new_field


class DjangoString(DjangoBase):
    DJANGO_ATTRIBUTES = DjangoBase.DJANGO_ATTRIBUTES + (
        ('max_length', None),
    )
    DJANGO_FIELD = "CharField"
    MUTANT_DEFAULTS = DjangoBase.MUTANT_DEFAULTS + (
        ('max_length', 255),
    )


class DjangoEmail(DjangoString):
    DJANGO_FIELD = "EmailField"
    MUTANT_DEFAULTS = DjangoString.MUTANT_DEFAULTS + (
        ('max_length', None),
    )


class DjangoDatetime(DjangoBase):
    DJANGO_FIELD = "DateTimeField"


def create_simple_mapping_field(typename):
    return type('Django' + typename, (DjangoBase,), {'DJANGO_FIELD': typename + 'Field'})


class DerivedEntity(object):
    def __init__(self, name, fields, options=None):
        self.name = name
        self.fields = fields
        self.options = options or {}


class DerivedField(object):
    def __init__(self, name, options=None):
        self.name = name
        self.options = options or {}


__inflector = None


def inflector():
    global __inflector
    if __inflector is None:
        __inflector = inflect.engine()
    return __inflector


def singular(word):
    return inflector().singular_noun(word)


def plural(word):
    return inflector().plural_noun(word)


def register(app):
    app.register_generator('django', DjangoSchemaGenerator)
