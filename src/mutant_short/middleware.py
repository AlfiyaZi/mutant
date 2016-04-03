import itertools
import logging
import collections
from six import string_types
import inflect


logger = logging.getLogger(__name__)


class ShorthandMiddleware(object):
    def __init__(self, *args, **kwargs):
        self.embedded = {}

    def before_parse(self, definition):
        return self.normalize_schema(definition)

    def after_parse(self, result):
        return result

    def normalize_schema(self, entities):
        self.custom_types = entities.keys()
        self.shorthand_fields = entities.pop('SHORTHANDS', {})
        result = [
            self.normalize_entity(entity, fields)
            for entity, fields in entities.items()
        ]
        result.append(self.embedded)
        return dict(itertools.chain.from_iterable(
            x.items() for x in result
        ))

    def normalize_entity(self, entity, fields):
        result = {
            entity: self.normalize_fields(fields)
        }
        return result

    def normalize_fields(self, fields):
        if isinstance(fields, collections.Mapping):
            return sorted([self.normalize_field({name: field})
                           for name, field in fields.items()],
                          key=lambda x: list(x.keys()))
        else:
            return [self.normalize_field(field)
                    for field in fields]

    def normalize_field(self, field_def):
        if isinstance(field_def, collections.Mapping):
            field_name, field = next(iter(field_def.items()))
        else:
            field_name, field = field_def, 'String'
        if isinstance(field, string_types):
            field = {'type': field}
        n_field = {
            self.normalize_option_name(name): value
            for name, value in field.items()
        }
        if 'list_of' in n_field:
            assert 'type' not in n_field, 'Keys `list-of` and `type` can not be used simultaneosly in field definition'
            n_field['type'] = 'List'
            linked_type = n_field.pop('list_of')
            if not isinstance(linked_type, string_types):
                new_entity_name = self.make_entity_name(field_name)
                self.embedded.update(
                    self.normalize_entity(new_entity_name, linked_type)
                )
                linked_type = new_entity_name
                n_field['own'] = True
            n_field.update({
                'type': 'List',
                'entity': linked_type,
            })
        assert 'type' in n_field, 'Key `type` must be defined for field %s' % (field_name)
        if n_field['type'] in self.shorthand_fields:
            s_field = self.shorthand_fields[n_field['type']]
            for key, value in s_field.items():
                n_field.setdefault(key, value)
            n_field['type'] = s_field['type']
        if n_field['type'] in self.custom_types:
            n_field.update({
                'type': 'Link',
                'entity': n_field['type'],
            })
        return {field_name: n_field}

    @staticmethod
    def normalize_option_name(name):
        return name.replace("-", "_").lower()

    @staticmethod
    def make_entity_name(field_name):
        inflector = inflect.engine()
        return (inflector.singular_noun(field_name) or field_name).title()


def register(app):
    middleware = ShorthandMiddleware()
    app.register_parser_middleware(middleware)
