import yaml
import logging
from six import string_types
from mutant.parsers.python_parser import PythonParser


logger = logging.getLogger(__name__)


class YamlParser(object):
    def __init__(self, maker):
        self.real_parser = PythonParser(maker)

    def set_field_types(self, field_types):
        self.real_parser.set_field_types(field_types)

    def parse(self, stream):
        definition = self.normalize_schema(yaml.load(stream))
        return self.real_parser.parse(definition)

    @classmethod
    def normalize_schema(cls, entities):
        return {
            entity: list(map(cls.normalize_field, fields))
            for entity, fields in entities.items()
        }

    @classmethod
    def normalize_field(cls, field_def):
        field_name, field = next(iter(field_def.items()))
        if isinstance(field, string_types):
            field = {'type': field}
        n_field = {
            cls.normalize_option_name(name): value
            for name, value in field.items()
        }
        if 'list_of' in n_field:
            assert 'type' not in n_field, 'Keys `list-of` and `type` can not be used simultaneosly in field definition'
            n_field['type'] = 'List'
        assert 'type' in n_field, 'Key `type` must be defined for field %s' % (field_name)
        return {field_name: n_field}

    @staticmethod
    def normalize_option_name(name):
        return name.replace("-", "_").lower()


def register(app):
    parser = YamlParser(app.field_maker)
    app.register_parser('yaml', parser)
