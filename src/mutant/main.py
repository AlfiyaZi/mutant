import logging
import importlib
from mutant.app import MutantApp


logger = logging.getLogger(__name__)


def yaml_to_django(definition='definition.yml'):
    app = MutantApp()
    load_extension(app, 'short')
    load_extension(app, 'yaml')
    load_extension(app, 'django')
    app.parse('yaml', definition)
    return app.mutate('django')


def yaml_to_cerberus(definition='definition.yml'):
    app = MutantApp()
    load_extension(app, 'short')
    load_extension(app, 'yaml')
    load_extension(app, 'cerberus')
    app.parse('yaml', definition)
    return app.mutate('cerberus')


def load_extension(app, name):
    package_name = 'mutant_' + name
    package = importlib.import_module(package_name)
    package.register(app)


def load_entry_points(app):
    pass


def main(*args, **kwargs):
    logging.basicConfig(level=logging.DEBUG)
    print(yaml_to_django(*args, **kwargs))
