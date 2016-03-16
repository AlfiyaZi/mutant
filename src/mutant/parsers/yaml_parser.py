import yaml
import logging
from collections import deque
from six import string_types
from mutant.fields import make_custom_field_type
from mutant.entity import Entity


logger = logging.getLogger(__name__)


def normalize_option_name(name):
    return name.replace("-", "_").lower()


class NotReady(Exception):
    pass


class YamlParser(object):
    def __init__(self, field_types):
        self.field_types = field_types

    def parse(self, stream):
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
                    fields.append(self.define_field(name, field_type))
                except NotReady:
                    entities.append((entity, field_defs))
                    fails_count += 1
                    if fails_count > 10:
                        raise
                    else:
                        break
            else:
                entity_obj = Entity(name=entity, fields=fields)
                schema.append(entity_obj)
                self.field_types[entity] = make_custom_field_type(entity_obj)
        return schema

    def define_field(self, name, field_type):
        if isinstance(field_type, string_types):
            field_type = {"type": field_type}
        n_field_type = {
            normalize_option_name(name): value
            for name, value in field_type.items()
        }
        requisites = []
        if 'list_of' in n_field_type:
            n_field_type['type'] = 'List'
            requisites.append(n_field_type['list_of'])
        typename = n_field_type.pop("type")
        requisites.append(typename)
        for requisite in requisites:
            if requisite not in self.field_types:
                logger.debug("Field %s definition failed: unknown type %s", name, requisite)
                raise NotReady(requisite)
        field_obj = self.field_types[typename](name=name, **n_field_type)
        return field_obj


def register(app):
    app.register_parser('yaml', YamlParser)
