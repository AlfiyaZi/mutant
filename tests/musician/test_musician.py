import os
import unittest

from mutant.make_django_model import from_yaml, DJANGO_FILE_TEMPLATE


def here(*parts):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)


class MusicianTestCase(unittest.TestCase):
    def test_django_regression(self):
        with open(here("definition.yml")) as fp:
            schema = from_yaml(fp)
            print(DJANGO_FILE_TEMPLATE.render(entities=schema))
