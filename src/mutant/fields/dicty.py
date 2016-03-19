import logging
import functools


logger = logging.getLogger(__name__)


class TypeField(object):
    def __init__(self, typename, name, **options):
        self.typename = typename
        self.name = name
        self.options = options


def make_field(typename, name, **options):
    return TypeField(typename, name, **options)


def make_custom_field_type(entity):
    def make_custom_field(name, **options):
        options.update(entity=entity)
        return make_field('Link', name, **options)

    return make_custom_field


def register(app):
    for typename in ('String', 'List', 'Number', 'Dict', 'Link', 'Date', 'Integer', 'Email', 'Text'):
        app.register_field(typename, functools.partial(make_field, typename))
    app.register_field_maker(make_custom_field_type)
