import logging
import sys

from mutant.parsers.python_parser import PythonParser


logger = logging.getLogger(__name__)


class MutantApp(object):
    """
    App stores all readers, parser middlewares generators.
    All plugins can register themselves on this instance.
    And finally it has `parse` and `mutate` methods, that executes mutation.
    """

    def __init__(self):
        self.readers = {}
        self.parser_middlewares = []
        self.generators = {}
        self.generator_extensions = {}
        self.parser = PythonParser()

    def register_reader(self, name, reader):
        self.readers[name] = reader

    def register_parser_middleware(self, middleware):
        self.parser_middlewares.append(middleware)

    def register_generator(self, generator_name, generator_class):
        self.generators[generator_name] = generator_class

    def extend_generator(self, generator_name, extension):
        self.generator_extensions.setdefault(generator_name, []).append(extension)

    def parse(self, reader_name, file_or_name):
        """
        Parsing contains 3 steps:
        1) Read input file;
        2) Apply middleware;
        3) Parse schema to internal format.
        """
        data = self._read(reader_name, file_or_name)
        for middleware in self.parser_middlewares:
            if hasattr(middleware, 'before_parse'):
                data = middleware.before_parse(data)
        schema = self.parser.parse(data)
        for middleware in reversed(self.parser_middlewares):
            if hasattr(middleware, 'after_parse'):
                schema = middleware.after_parse(schema)
        self.schema = schema
        return self.schema

    def mutate(self, generator_name):
        gen = self.generators[generator_name](self.schema)
        for ext in self.generator_extensions.get(generator_name, []):
            gen.register_extension(ext)
        return gen.render()

    def _read(self, reader_name, file_or_name):
        reader = self.readers[reader_name]
        if hasattr(file_or_name, 'read'):
            return reader.read(file_or_name)
        else:
            if file_or_name == '-':
                return reader.read(sys.stdin)
            else:
                with open(file_or_name) as fp:
                    return reader.read(fp)
