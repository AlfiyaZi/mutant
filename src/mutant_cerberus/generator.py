from __future__ import unicode_literals

import logging

from jinja2 import Template


logger = logging.getLogger(__name__)


FILE_TEMPLATE = Template("""
rules = {
    {%- for entity in entities %}
    {{ render_entity(entity) }}
    {%- endfor %}
}
""".lstrip())


ENTITY_TEMPLATE = Template("""
"{{ entity['name'] }}": {
    {%- for field in entity['fields'] %}
    {{ render_field(field) }}
    {%- endfor %}
},
""".strip())


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


TYPE_MAPPINGS = {
    'String': 'string',
    'Integer': 'integer',
    'Float': 'float',
    'Number': 'number',
    'Boolean': 'boolean',
    'Datetime': 'datetime',
    'List': 'list',

    'Email': 'string',
    'Text': 'string',
    # 'dict
    # 'set
}


class CerberusSchemaGenerator(object):
    def __init__(self, schema):
        self.entities = schema

    def render(self):
        return FILE_TEMPLATE.render(
            entities=self.entities,
            render_entity=self.render_entity,
        )

    def render_entity(self, entity):
        return ENTITY_TEMPLATE.render(
            entity=entity,
            render_field=self.render_field,
        )

    def render_field(self, field):
        PATTERN = '"{name}": {{{options}}},'
        f_options = [self.render_option('type', True, {'type': TYPE_MAPPINGS[field['type']]})]
        self.apply_triggers(field)
        for option, is_quoted in OPTIONS:
            f_option = self.render_option(option, is_quoted, field['options'])
            if f_option is not None:
                f_options.append(f_option)
        options = ', '.join(f_options)
        return PATTERN.format(name=field['name'], options=options)

    @staticmethod
    def apply_triggers(field):
        for trigger, option in TRIGGERS.items():
            if trigger in field['options']:
                field['options'].setdefault(option, field['options'][trigger])

    def render_option(self, option, is_quoted, field_options):
        OPT_PATTERN = '"{key}": {value}'
        if option in field_options:
            value = field_options[option]
            if is_quoted:
                value = '"{0}"'.format(value)
            elif option == 'schema' and field_options['type'] == 'List':
                value = self.render_entity(self.entities[field_options['schema']])
            return OPT_PATTERN.format(key=option, value=value)


def register(app):
    app.register_generator('cerberus', CerberusSchemaGenerator)
