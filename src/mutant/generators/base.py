import logging


logger = logging.getLogger(__name__)


class BaseGenerator(object):
    def __init__(self, name, options=None):
        self.name = name
        self.options = options or {}

    @classmethod
    def for_field(cls, field):
        return cls(name=field.name, options=field.options)

    def render(self, template):
        return template.render(field_name=self.name, field_type=self.options)
