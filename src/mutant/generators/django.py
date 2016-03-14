# import copy
import logging
from jinja2 import Template
from mutant.generators.base import BaseGenerator


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


def render_schema(entities, maker):
    renderers = [
        DjangoEntity(entity, maker)
        for entity in entities
    ]
    return DJANGO_FILE_TEMPLATE.render(entities=renderers)


class DjangoEntity(object):
    def __init__(self, entity, make_generator):
        self.entity = entity
        self.fields = [make_generator(field)
                       for field in entity.fields]

    def render(self):
        logger.debug(self.entity.__dict__)
        return DJANGO_MODEL_TEMPLATE.render(
            name=self.entity.name,
            fields=self.fields,
            options=self.entity.options
        )


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
    DJANGO_FIELD = None
    MUTANT_DEFAULTS = ()

    def __init__(self, field):
        super(DjangoBase, self).__init__(field)
        self.options.update([
            (key, self.field.options[key])
            for key, _ in self.DJANGO_ATTRIBUTES
            if key in self.field.options
        ])
        for key, value in self.MUTANT_DEFAULTS:
            self.options.setdefault(key, value)
        self.options.update({
            'django_field': self.DJANGO_FIELD,
            'django_positional': self.django_positional(),
            'django_attributes': self.django_attributes(),
        })

    @property
    def name(self):
        return self.field.name

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


class DjangoForeignKey(DjangoBase):
    DJANGO_FIELD = "ForeignKey"
    DJANGO_ATTRIBUTES = DjangoBase.DJANGO_ATTRIBUTES + (
        ('on_delete', None),
    )
    MUTANT_DEFAULTS = DjangoBase.MUTANT_DEFAULTS + (
        ('on_delete', 'CASCADE'),
    )

    def django_attributes(self):
        self.options['on_delete'] = "models.{0}".format(self.options['on_delete'])
        return super(DjangoForeignKey, self).django_attributes()

    def django_positional(self):
        return [
            "'{0}'".format(self.field.options['model']),
        ]


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
    MUTANT_DEFAULTS = (
        ('max_length', None),
    ) + DjangoString.MUTANT_DEFAULTS


class DjangoInteger(DjangoBase):
    DJANGO_FIELD = "IntegerField"


class DjangoDate(DjangoBase):
    DJANGO_FIELD = "DateField"


def register():
    return {
        'String': DjangoString,
        'Email': DjangoEmail,
        'Integer': DjangoInteger,
        'Date': DjangoDate,
        'ForeignKey': DjangoForeignKey,
    }
