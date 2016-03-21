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
"{{ entity['name'] }}": {{ render_entity_body(entity) }},
""".strip())


ENTITY_BODY_TEMPLATE = Template("""
{
{%- for field in entity['fields'] %}
{{ render_field(field) }}
{%- endfor %}
}
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
    ('schema', False),
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


ALIASES = {
    'schema': 'entity',
}


FIELD_PATTERN = '"{name}": {{\n{options}\n}},'


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
            render_entity_body=lambda x: self.indent(self.render_entity_body(x)).lstrip(),
        )

    def render_entity_body(self, entity):
        return ENTITY_BODY_TEMPLATE.render(
            entity=entity,
            render_field=self.render_field,
        )

    def render_field(self, field):
        self.apply_triggers(field)
        full_options = dict(field['options'], type=field['type'])
        rendered_options = []
        for option, is_quoted in OPTIONS:
            rendered = self.render_option(option, is_quoted, full_options)
            if rendered is not None:
                rendered_options.append(rendered)
        return self.indent(
            FIELD_PATTERN.format(
                name=field['name'],
                options=self.indent('\n'.join(rendered_options)),
            )
        )

    @staticmethod
    def apply_triggers(field):
        for trigger, option in TRIGGERS.items():
            if trigger in field['options']:
                field['options'].setdefault(option, field['options'][trigger])

    def render_option(self, key, is_quoted, field_options):
        OPT_PATTERN = '"{key}": {value},'
        aliased = ALIASES.get(key, key)
        if aliased in field_options:
            value = field_options[aliased]
            if key == 'type':
                value = TYPE_MAPPINGS[value]
            if key == 'schema':
                if field_options['type'] == 'List':
                    value = self.embed_entity(field_options[aliased]).lstrip()
            elif is_quoted:
                value = '"{0}"'.format(value)
            return OPT_PATTERN.format(key=key, value=value)

    def embed_entity(self, entity_name):
        for entity in self.entities:
            if entity_name == entity['name']:
                return self.render_entity_body(entity)
        raise KeyError(entity_name)

    def indent(self, text):
        return '\n'.join([
            '    ' + line
            for line in text.splitlines()
        ])



def register(app):
    app.register_generator('cerberus', CerberusSchemaGenerator)
