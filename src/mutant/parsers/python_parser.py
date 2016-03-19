import logging
from collections import deque
from mutant.entity import Entity


logger = logging.getLogger(__name__)


class NotReady(Exception):
    pass


class PythonParser(object):
    def __init__(self, maker):
        self.maker = maker

    def set_field_types(self, field_types):
        self.field_types = field_types

    def parse(self, definition):
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
                self.field_types[entity] = self.maker(entity_obj)
        return schema

    def define_field(self, name, field_type):
        requisites = []
        if 'list_of' in field_type:
            requisites.append(field_type['list_of'])
        requisites.append(field_type['type'])
        for requisite in requisites:
            if requisite not in self.field_types:
                logger.debug("Field %s definition failed: unknown type %s", name, requisite)
                raise NotReady(requisite)
        options = dict(field_type)
        typename = options.pop('type')
        field_obj = self.field_types[typename](name=name, **options)
        return field_obj


def register(app):
    parser = PythonParser(app.field_maker)
    app.register_parser('python', parser)
