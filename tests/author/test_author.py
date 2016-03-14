import os
import unittest

from mutant.app import yaml_to_django


def here(*parts):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)


class AuthorTestCase(unittest.TestCase):
    def test_django_regression(self):
        models = yaml_to_django(here("definition.yml"))
        with open(here("models.py")) as fp:
            expect = fp.read()
        assert models == expect
