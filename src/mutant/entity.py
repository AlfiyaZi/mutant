import logging


logger = logging.getLogger(__name__)


class Entity(object):
    def __init__(self, name, fields, options=None):
        super(Entity, self).__init__()
        self.name = name
        self.fields = fields
        self.options = options or {}

    def __repr__(self):
        return u'<{0} {1}>'.format(self.__class__.__name__, self.name)
