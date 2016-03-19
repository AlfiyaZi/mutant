from __future__ import unicode_literals

import logging

from jinja2 import Template


logger = logging.getLogger(__name__)


FILE_TEMPLATE = Template("""
rules = {
    {%- for entity in entities %}
    "{{ entity['name'] }}": {
      {%- for field in entity['fields'] %}
        {{ render_field(field) }}
      {%- endfor %}
    },
    {%- endfor %}
}
""".lstrip())


OPTIONS = (
    ('type', True),
    ('required', False),
    ('readonly', False),
    ('nullable', False),
    ('minlength', True),
    ('maxlength', True),
    ('min', True),
    ('max', True),
    ('allowed', False),
    ('empty', False),
    ('items', True),
    ('schema', True),
    ('valueschema', True),
    ('propertyschema', True),
    ('regex', True),
    ('dependencies', True),
    ('anyof', True),
    ('allof', True),
    ('noneof', True),
    ('oneof', True),
)


TRIGGERS = {
    'primary_key': 'required',
}


class CerberusSchemaGenerator(object):
    def __init__(self, schema):
        self.entities = schema

    def render(self):
        return FILE_TEMPLATE.render(
            entities=self.entities,
            render_field=self.render_field,
        )

    @classmethod
    def render_field(cls, field):
        PATTERN = '"{name}": {{{options}}},'
        f_options = [cls.render_option('type', True, field)]
        for trigger, option in TRIGGERS.items():
            if trigger in field['options']:
                field['options'].setdefault(option, field['options'][trigger])
        for option, is_quoted in OPTIONS:
            f_option = cls.render_option(option, is_quoted, field['options'])
            if f_option is not None:
                f_options.append(f_option)
        options = ', '.join(f_options)
        return PATTERN.format(name=field['name'], options=options)

    @staticmethod
    def render_option(option, is_quoted, field_options):
        OPT_PATTERN = '"{key}": {value}'
        if option in field_options:
            value = field_options[option]
            if is_quoted:
                value = '"{0}"'.format(value)
            return OPT_PATTERN.format(key=option, value=value)


def register(app):
    app.register_generator('cerberus', CerberusSchemaGenerator)
