import logging
from mutant.fields import classy as builtin_fields
from mutant.generators import django
from mutant.parsers import yaml_parser
from mutant.parsers import python_parser
from mutant.app import MutantApp


logger = logging.getLogger(__name__)


def attach_builtins(app):
    builtin_fields.register(app)
    python_parser.register(app)
    yaml_parser.register(app)
    django.register(app)


def yaml_to_django(definition='definition.yml'):
    app = MutantApp()
    attach_builtins(app)
    app.parse('yaml', definition)
    return app.mutate('django')


def main(*args, **kwargs):
    logging.basicConfig(level=logging.DEBUG)
    print(yaml_to_django(*args, **kwargs))
