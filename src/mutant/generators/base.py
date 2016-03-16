import logging


logger = logging.getLogger(__name__)


class UnknownGenerator(KeyError):
    pass


class BaseGenerator(object):
    field_generators = {}

    def __init__(self, entities, fields):
        self.entities = entities
        self.fields = fields

    def render(self):
        raise NotImplemented()
