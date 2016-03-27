import os
import logging
import unittest

from mutant.main import yaml_to_django, yaml_to_cerberus


def here(*parts):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)


class YamlToDjangoRegressionTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_author(self):
        self.yaml_to_django("author")
        self.yaml_to_cerberus("author")

    def test_musician(self):
        self.yaml_to_django("musician")
        self.yaml_to_cerberus("musician")

    def test_blog(self):
        self.yaml_to_django("blog")
        self.yaml_to_cerberus("blog")

    def test_granthub(self):
        self.yaml_to_django("granthub")
        self.yaml_to_cerberus("granthub")

    def yaml_to_django(self, dirname):
        models = yaml_to_django(here(dirname, "definition.yml"))
        with open(here(dirname, "models.py")) as fp:
            expect = fp.read()
        assert expect == models

    def yaml_to_cerberus(self, dirname):
        schema = yaml_to_cerberus(here(dirname, "definition.yml"))
        with open(here(dirname, "cerberus.py")) as fp:
            expect = fp.read().rstrip()
        assert expect == schema
