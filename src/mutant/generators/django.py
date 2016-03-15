import itertools
import logging

from jinja2 import Template
from mutant.generators.base import BaseGenerator
import inflect


logger = logging.getLogger(__name__)


DJANGO_FILE_TEMPLATE = Template("""
from django.db import models


{% for entity in entities -%}
{{ entity.render() }}{% if not loop.last %}

{% endif%}
{% endfor -%}
""".lstrip())


DJANGO_MODEL_TEMPLATE = Template("""
class {{ name }}(models.Model):
  {%- for field in fields -%}
    {{ field.render_django() }}
  {%- endfor -%}
""".lstrip())


DJANGO_FIELD_TEMPLATE = Template("""
    {{ field_name }} = models.{{ field_type.django_field }}(
      {%- for value in field_type.django_positional -%}
        {{ value }}
        {%- if not loop.last %}, {% endif -%}
      {%- endfor -%}
      {%- for name, value in field_type.django_attributes -%}
        {%- if loop.first and field_type.django_positional %}, {% endif -%}
        {{ name }}={{ value }}
        {%- if not loop.last %}, {% endif -%}
      {%- endfor -%}
    )
""")


class DjangoSchema(object):
    def __init__(self, entities, field_factory):
        self.entities = entities
        self.field_factory = field_factory

    def render(self):
        renderers = [
            DjangoEntity.for_entity(entity, self.field_factory)
            for entity in self.entities
        ]
        for renderer in list(renderers):
            renderers.extend(renderer.additional_renderers())
        return DJANGO_FILE_TEMPLATE.render(entities=renderers)


class DjangoEntity(object):
    def __init__(self, entity_name, fields, factory=None):
        self.entity_name = entity_name
        self.fields = fields
        self.factory = factory

    @classmethod
    def for_entity(cls, entity, factory):
        fields = [factory(field)
                  for field in entity.fields]
        return DjangoEntity(
            entity_name=entity.name,
            fields=fields,
            factory=factory,
        )

    def render(self):
        logger.debug(self.__dict__)
        return DJANGO_MODEL_TEMPLATE.render(
            name=self.entity_name,
            fields=self.fields,
            # options=self.entity_options
        )

    def additional_renderers(self):
        new_entities = itertools.chain.from_iterable(
            field.additional_renderers(self.entity_name)
            for field in self.fields
        )
        return new_entities


class DjangoBase(BaseGenerator):
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
        self.options.update({
            'django_field': self.DJANGO_FIELD,
            'django_positional': self.django_positional(),
            'django_attributes': self.django_attributes(),
        })

    @classmethod
    def for_field(cls, field):
        options = {
            key: field.options[key]
            for key, default_value in (cls.DJANGO_ATTRIBUTES + cls.PROXY_ATTRIBUTES)
            if key in field.options
        }
        return cls(name=field.name, options=options)

    def render_django(self):
        return self.render(DJANGO_FIELD_TEMPLATE)

    def django_positional(self):
        return []

    def django_attributes(self):
        return [
            (key, self.options[key])
            for key, default_value in self.DJANGO_ATTRIBUTES
            if key in self.options and self.options[key] != default_value
        ]

    def additional_renderers(self, *args, **kwargs):
        return []


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
        return [
            "'{0}'".format(self.options['entity']),
        ]


class DjangoList(DjangoBase):
    DJANGO_FIELD = None
    DJANGO_ATTRIBUTES = DjangoBase.DJANGO_ATTRIBUTES + (
        ('on_delete', None),
    )
    PROXY_ATTRIBUTES = (
        ('list_of', None),
    )
    MUTANT_DEFAULTS = DjangoBase.MUTANT_DEFAULTS + (
        ('on_delete', 'CASCADE'),
    )

    def render_django(self):
        return ''

    def additional_renderers(self, entity):
        return [self.many_to_many(entity)]

    def many_to_many(self, entity_name):
        inflector = inflect.engine()
        from_name = entity_name.lower()
        to_name = inflector.singular_noun(self.name)
        m2m_from = DjangoForeignKey(from_name, {'entity': entity_name})
        m2m_to = DjangoForeignKey(to_name, {'entity': self.options['list_of']})
        return DjangoEntity(
            entity_name=entity_name + self.options['list_of'],
            fields=[m2m_from, m2m_to],
        )


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


class DjangoInteger(DjangoBase):
    DJANGO_FIELD = "IntegerField"


class DjangoDate(DjangoBase):
    DJANGO_FIELD = "DateField"


class DerivedEntity(object):
    def __init__(self, name, fields, options=None):
        self.name = name
        self.fields = fields
        self.options = options or {}


class DerivedField(object):
    def __init__(self, name, options=None):
        self.name = name
        self.options = options or {}


def register():
    return {
        'String': DjangoString,
        'Email': DjangoEmail,
        'Integer': DjangoInteger,
        'Date': DjangoDate,
        'ForeignKey': DjangoForeignKey,
        'List': DjangoList,
    }
