import logging


logger = logging.getLogger(__name__)


class JinjaFieldGenerator(object):
    template = None

    def __init__(self, name, options=None):
        self.name = name
        self.options = options or {}

    @classmethod
    def for_field(cls, field):
        return cls(name=field.name, options=field.options)

    def render(self):
        return self.template.render(field_name=self.name, field_type=self.options)
