import yaml


class YamlReader(object):

    def read(self, stream):
        return yaml.load(stream)


def register(app):
    reader = YamlReader()
    app.register_reader('yaml', reader)
