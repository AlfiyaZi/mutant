import os
import unittest

from mutant.main import yaml_to_django


def here(*parts):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)


class YamlToDjangoRegressionTestCase(unittest.TestCase):
    def test_author(self):
        self.yaml_to_model("author")

    def test_musician(self):
        self.yaml_to_model("musician")

    def test_blog(self):
        self.yaml_to_model("blog")

    def yaml_to_model(self, dirname):
        models = yaml_to_django(here(dirname, "definition.yml"))
        with open(here(dirname, "models.py")) as fp:
            expect = fp.read()
        assert models == expect
