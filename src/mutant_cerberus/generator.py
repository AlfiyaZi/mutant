from __future__ import unicode_literals

import logging

from jinja2 import Template


logger = logging.getLogger(__name__)


FILE_TEMPLATE = Template("""
rules = {
    {%- for entity in entities %}
    "{{ entity['name'] }}": {
      {%- for field in entity['fields'] %}
        "{{ field['name'] }}": {"type": "{{ field['type'] }}"},
      {%- endfor %}
    },
    {%- endfor %}
}
""".lstrip())


class CerberusSchemaGenerator(object):
    def __init__(self, schema):
        self.entities = schema

    def render(self):
        return FILE_TEMPLATE.render(entities=self.entities)


def register(app):
    app.register_generator('cerberus', CerberusSchemaGenerator)
