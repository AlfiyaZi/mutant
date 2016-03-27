import logging


logger = logging.getLogger(__name__)


class NotReady(Exception):
    pass


class PythonParser(object):
    """
    Converts high level human friendly schema definition to low level:
    Example input:

        {
            'Department': [
                {'title': {'type': 'String'}},
                {'employee': {'type': 'List', 'entity': 'Employee'}},
            ],
            'Employee': [
                {'first_name': {'type': 'String'}},
            ],
        }

    Output:

        [
            {
                'name': 'Department',
                'fields': [
                    {'name': 'title', 'type': 'String'},
                    {'name': 'employee', 'type': 'List', 'options': {'entity': 'Employee'}},
                ],
                'options': {},
            },
            {
                'name': 'Employee',
                'fields': [
                    {'name': 'first_name', 'type': 'String'},
                ],
                'options': {},
            },
        ]
    """
    def __init__(self):
        self.hooks = {
            'pre': {
                'schema': [],
                'entity': [],
                'field': [],
            },
            'post': {
                'schema': [],
                'entity': [],
                'field': [],
            },
        }

    def register_pre_hook(self, kind, hook):
        self.hooks['pre'][kind].append(hook)

    def register_post_hook(self, kind, hook):
        self.hooks['post'][kind].append(hook)

    def parse(self, definition):
        logger.debug(definition)

        schema = []
        for entity_name, field_defs in definition.items():
            schema.append(self.define_entity(entity_name, field_defs))
        return self.pipe_through_hooks('schema', self.order_by_requisites(schema))

    def define_entity(self, entity_name, field_defs):
        fields = []
        for data in field_defs:
            assert len(data) == 1
            name, parameters = next(iter(data.items()))
            fields.append(self.define_field(name, parameters))
        return self.pipe_through_hooks('entity', {
            "name": entity_name,
            "fields": fields,
            "options": {},
        })

    def define_field(self, name, parameters):
        options = dict(parameters)
        typename = options.pop('type')
        return self.pipe(self.hooks['post']['field'], {
            "type": typename,
            "name": name,
            "options": options,
        })

    @staticmethod
    def pipe(funcs, arg):
        for func in funcs:
            arg = func(arg)
        return arg

    @classmethod
    def order_by_requisites(cls, schema):
        requisites = cls.collect_requisites(schema)
        return sorted(schema, key=cmp_by_requisites(requisites))

    @staticmethod
    def collect_requisites(schema):
        requisites = {}
        for entity in schema:
            for field in entity['fields']:
                master = field['type']
                dependant = entity['name']
                requisites.setdefault(dependant, set()).add(master)
                if 'entity' in field['options']:
                    if field['type'] == 'Link':
                        master = field['options']['entity']
                        dependant = entity['name']
                    elif field['type'] == 'List':
                        master = entity['name']
                        dependant = field['options']['entity']
                    requisites.setdefault(dependant, set()).add(master)
        return requisites


def cmp_by_requisites(requisites):
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            a, b = self.obj['name'], other.obj['name']
            logger.debug('Compare %s to %s', a, b)
            if b in recursive_requisites(a):
                return False
            elif a in recursive_requisites(b):
                return True
            else:
                return a < b

    def recursive_requisites(name):
        result = requisites.get(name, set())
        more = set()
        for subname in result:
            more.update(recursive_requisites(subname))
        return result | more

    return K


def register(app):
    parser = PythonParser()
    app.register_parser('python', parser)
