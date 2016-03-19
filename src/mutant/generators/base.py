import logging


logger = logging.getLogger(__name__)


class UnknownGenerator(KeyError):
    pass


class BaseGenerator(object):

    def render(self):
        raise NotImplemented()
