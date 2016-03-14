import logging


logger = logging.getLogger(__name__)


class BaseGenerator(object):
    def __init__(self, field):
        self.field = field
        self.options = {}

    def render(self, template):
        logger.debug(dict(field_name=self.name, field_type=self.options))
        options = self.options.copy()
        options.update(self.field.options)
        return template.render(field_name=self.field.name, field_type=options)
