import logging


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
        self.fields[name] = field_class

    def register_field_maker(self, field_maker):
        self.field_maker = field_maker

    def register_parser(self, name, parser):
        self.parsers[name] = parser

    def register_generator(self, generator_name, generator_class):
        self.generators[generator_name] = generator_class

    def parse(self, parser_name, file_or_name):
        parser = self.parsers[parser_name]
        parser.set_field_types(self.fields)
        if hasattr(file_or_name, 'read'):
            self.schema = parser.parse(file_or_name)
        else:
            with open(file_or_name) as fp:
                self.schema = parser.parse(fp)
        return self.schema

    def mutate(self, generator_name):
        return self.generators[generator_name](self.schema, self.fields).render()
