# import copy
import yaml
import logging
from collections import deque
from jinja2 import Template
from six import string_types


logger = logging.getLogger(__name__)


DJANGO_FILE_TEMPLATE = Template("""
from django.db import models


{% for entity in entities -%}
{{ entity.render_django() }}{% if not loop.last %}

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
      {%- for name, value in field_type.django_attributes -%}
        {{ name }}={{ value }}
        {%- if not loop.last %}, {% endif -%}
      {%- endfor -%}
    )
""")


class BaseType(object):
    def __init__(self, name, fields):
        super(BaseType, self).__init__()
        self.name = name
        self.fields = fields

    def render(self, template):
        logger.debug(dict(name=self.name, fields=self.fields))
        return template.render(name=self.name, fields=self.fields)

    def render_django(self):
        return self.render(DJANGO_MODEL_TEMPLATE)


def make_custom_field_type(entity):
    return type('CustomField', (ForeignKey,), dict(foreign_model=entity))


class BaseField(object):
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

    def __init__(self, name, **kwargs):
        super(BaseField, self).__init__()
        self.name = name
        self.options = dict(
            {'django_field': self.DJANGO_FIELD},
        )
        self.options.update([
            (key, kwargs[key])
            for key, _ in self.DJANGO_ATTRIBUTES
            if key in kwargs
        ])

    def render(self, template):
        logger.debug(dict(field_name=self.name, field_type=self.options))
        return template.render(field_name=self.name, field_type=self.options)

    def render_django(self):
        self.options['django_attributes'] = self.django_attributes()
        return self.render(DJANGO_FIELD_TEMPLATE)

    def django_attributes(self):
        return [
            (key, self.options[key])
            for key, default_value in self.DJANGO_ATTRIBUTES
            if key in self.options and self.options[key] != default_value
        ]

    @staticmethod
    def normalize_option_name(name):
        return name.replace("-", "_").lower()


class ForeignKey(BaseField):
    DJANGO_FIELD = "ForeignKey"
    DJANGO_ATTRIBUTES = BaseField.DJANGO_ATTRIBUTES + (
        ('on_delete', 'CASCADE'),
        ('othermodel', None),
    )

    def __init__(self, **kwargs):
        super(ForeignKey, self).__init__(**kwargs)
        self.options.update(
            othermodel="'{0}'".format(self.foreign_model.name),
        )


class StringField(BaseField):
    DJANGO_ATTRIBUTES = BaseField.DJANGO_ATTRIBUTES + (
        ('max_length', None),
    )
    DJANGO_FIELD = "CharField"

    def __init__(self, max_length=255, **kwargs):
        super(StringField, self).__init__(**kwargs)
        self.options['max_length'] = max_length
        self.options['django_field'] = "CharField"


class EmailField(StringField):
    DJANGO_FIELD = "EmailField"


class IntegerField(BaseField):
    DJANGO_FIELD = "IntegerField"


class DateField(BaseField):
    DJANGO_FIELD = "DateField"


class NotReady(Exception):
    pass


def from_yaml(stream):
    definition = yaml.load(stream)
    logger.debug(definition)

    schema = []
    entities = deque(definition.items())
    fails_count = 0
    while entities:
        entity, field_defs = entities.popleft()
        fields = []
        for data in field_defs:
            assert len(data) == 1
            name, field_type = next(iter(data.items()))
            try:
                fields.append(define_field(name, field_type))
            except NotReady:
                entities.append((entity, field_defs))
                fails_count += 1
                if fails_count > 10:
                    raise
                else:
                    break
        else:
            entity_obj = BaseType(name=entity, fields=fields)
            schema.append(entity_obj)
            mutant_field_types[entity] = make_custom_field_type(entity_obj)
    return schema


def define_field(name, field_type):
    if isinstance(field_type, string_types):
        field_type = {"type": field_type}
    n_field_type = {
        BaseField.normalize_option_name(name): value
        for name, value in field_type.items()
    }
    typename = n_field_type.pop("type")
    if typename not in mutant_field_types:
        logger.debug("Field %s definition failed: unknown type %s", name, typename)
        raise NotReady
    field_obj = mutant_field_types[typename](name=name, **n_field_type)
    return field_obj


def repeat_failing(items):
    repeat = deque(items)
    while repeat:
        item = repeat.popleft()
        try:
            yield item
        except NotReady:
            items.appendright(item)


def main():
    logging.basicConfig(level=logging.INFO)
    with open("definition.yml") as fp:
        schema = from_yaml(fp)
        print(DJANGO_FILE_TEMPLATE.render(entities=schema))
        # for entity_obj in schema:
        #     print(entity_obj.render_django())


mutant_field_types = {
    'String': StringField,
    'Email': EmailField,
    'Integer': IntegerField,
    'Date': DateField,
}


if __name__ == '__main__':
    main()
