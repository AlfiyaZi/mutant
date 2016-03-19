import logging
import functools


logger = logging.getLogger(__name__)


def make_field(typename, name, **options):
    return {
        "typename": typename,
        "name": name,
        "options": options,
    }


def make_custom_field_type(entity):
    def make_custom_field(name, **options):
        options.update(entity=entity)
        return make_field('Link', name, **options)

    return make_custom_field


def register(app):
    for typename in ('String', 'List', 'Number', 'Dict', 'Link'):
        app.register(typename, functools.partial(make_field, typename))
    app.register_field_maker(make_custom_field_type)
