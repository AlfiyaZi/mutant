from mutant_django.generator import DjangoBase


def register(app):
    app.extend_generator('django', django_json_field)


def django_json_field(gen):
    gen.field_generators['JSON'] = JSONField


class JSONField(DjangoBase):
    DJANGO_FIELD = 'JSONField'

    def render_imports(self):
        return ['from jsonfield import JSONField']
