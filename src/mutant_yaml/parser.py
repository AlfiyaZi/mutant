import yaml
import logging
import collections
from six import string_types
from mutant.parsers.python_parser import PythonParser


logger = logging.getLogger(__name__)


class YamlParser(object):
    def __init__(self, *args, **kwargs):
        self.real_parser = PythonParser(*args, **kwargs)

    def parse(self, stream):
        definition = self.normalize_schema(yaml.load(stream))
        return self.real_parser.parse(definition)

    @classmethod
    def normalize_schema(cls, entities):
        custom_types = entities.keys()
        return {
            entity: cls.normalize_fields(fields, custom_types)
            for entity, fields in entities.items()
        }

    @classmethod
    def normalize_fields(cls, fields, custom_types):
        if isinstance(fields, collections.Mapping):
            return sorted([cls.normalize_field({name: field}, custom_types)
                           for name, field in fields.items()])
        else:
            return [cls.normalize_field(field, custom_types)
                    for field in fields]

    @classmethod
    def normalize_field(cls, field_def, custom_types):
        if isinstance(field_def, collections.Mapping):
            field_name, field = next(iter(field_def.items()))
        else:
            field_name, field = field_def, 'String'
        if isinstance(field, string_types):
            field = {'type': field}
        n_field = {
            cls.normalize_option_name(name): value
            for name, value in field.items()
        }
        if 'list_of' in n_field:
            assert 'type' not in n_field, 'Keys `list-of` and `type` can not be used simultaneosly in field definition'
            n_field['type'] = 'List'
            n_field.update({
                'type': 'List',
                'entity': n_field.pop('list_of'),
            })
        assert 'type' in n_field, 'Key `type` must be defined for field %s' % (field_name)
        if n_field['type'] in custom_types:
            n_field.update({
                'type': 'Link',
                'entity': n_field['type'],
            })
        return {field_name: n_field}

    @staticmethod
    def normalize_option_name(name):
        return name.replace("-", "_").lower()


def register(app):
    parser = YamlParser()
    app.register_parser('yaml', parser)
