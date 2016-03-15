import logging
from mutant.fields import MUTANT_FIELDS
from mutant.generators import django
from mutant.parsers.yaml_parser import YamlParser


logger = logging.getLogger(__name__)


class MutantApp(object):
    """
    App stores all parsers, fields and generators.
    All plugins can register themselves on this instance.
    And finally it has `run` method, that executes mutation.
    """

    def __init__(self):
        self.fields = {}
        self.parsers = {}
        self.generators = {}

    def register_field(self, name, field_class):
        self.field[name] = field_class

    def register_parser(self, name, parser_class):
        self.parsers[name] = parser_class

    def register_generator(self, generator_name, field_name, generator_class):
        self.generators.setdefault(generator_name, {})[field_name] = generator_class

    def generator_factory(self, generator_name):
        keys = set(self.fields.keys()).intersection(self.generators[generator_name].keys())
        mapping = {
            self.fields[key]: self.generators[key]
            for key in keys
        }

        def generator_factory(field):
            if field.__class__ in mapping:
                return mapping[field.__class__].for_field(field)
            else:
                # Hack for dynamically created ForeignKey class
                for superclass in mapping.keys():
                    if isinstance(field, superclass):
                        return mapping[superclass].for_field(field)
            raise UnknownGenerator(field)

        return generator_factory

    def parse(self, parser_name, *args, **kwargs):
        parser = self.parsers[parser_name](self.fields)
        self.schema = parser.parse(*args, **kwargs)
        return self.schema

    def mutate(self, generator_name):
        return self.generators


class UnknownGenerator(KeyError):
    pass


def load_parsers():
    return {
        'yaml': YamlParser,
    }


def load_fields():
    base_fields = MUTANT_FIELDS
    return base_fields


def load_generators():
    return django.register()


def generators_for_field(fields, generators):
    keys = set(fields.keys()).intersection(generators.keys())
    mapping = {
        fields[key]: generators[key]
        for key in keys
    }

    def generator_factory(field):
        if field.__class__ in mapping:
            return mapping[field.__class__].for_field(field)
        else:
            # Hack for dynamically created ForeignKey class
            for superclass in mapping.keys():
                if isinstance(field, superclass):
                    return mapping[superclass].for_field(field)
        raise UnknownGenerator(field)

    return generator_factory


def yaml_to_django(definition='definition.yml'):
    fields = load_fields()
    generator_factory = generators_for_field(fields, load_generators())
    parsers = load_parsers()
    with open(definition) as fp:
        schema = parsers['yaml'](fields).parse(fp)
    models = django.DjangoSchema(schema, generator_factory).render()
    return models


def main(*args, **kwargs):
    logging.basicConfig(level=logging.DEBUG)
    print(yaml_to_django(*args, **kwargs))
