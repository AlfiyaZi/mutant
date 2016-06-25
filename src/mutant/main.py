import sys
import argparse
import logging
import importlib
from mutant.app import MutantApp


logger = logging.getLogger(__name__)


def main(*args, **kwargs):
    logging.basicConfig(level=logging.DEBUG)
    options = parse_cli_options()
    app = create_app(options.reader, options.writer, *options.extension)
    app.parse(options.reader, options.definition)
    sys.stdout.write(app.mutate(options.writer))


def create_app(*extension_names):
    app = MutantApp()
    load_extension(app, 'short')
    for name in extension_names:
        load_extension(app, name)
    return app


def load_extension(app, name):
    package_name = 'mutant_' + name
    package = importlib.import_module(package_name)
    print(package.register)
    package.register(app)


def parse_cli_options():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '--reader',
        default='yaml',
        help='Name of reader to parse input file (default: yaml)',
    )
    parser.add_argument(
        'writer',
        help='Name of writer to generate output file',
    )
    parser.add_argument(
        'definition',
        help='Definition file name or "-" for stdin',
    )
    parser.add_argument(
        '-e', '--extension', nargs='+',
        help='Name of extension',
    )
    return parser.parse_args()


def yaml_to_django(definition='definition.yml'):
    app = MutantApp()
    app = create_app('yaml', 'django')
    app.parse('yaml', definition)
    return app.mutate('django')


def yaml_to_cerberus(definition='definition.yml'):
    app = create_app('yaml', 'cerberus')
    app.parse('yaml', definition)
    return app.mutate('cerberus')
