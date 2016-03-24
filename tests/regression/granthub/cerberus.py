PID_RULE = {'type': 'string', 'maxlength': 100, 'required': True, 'empty': False, 'coerce': 'int'}
PID_OPTIONAL_RULE = {'type': 'string', 'maxlength': 100, 'coerce': 'int'}
ID_RULE = {'type': 'integer', 'min': 0}
EMAIL_RULE = {'type': 'string', 'validator': 'email', 'maxlength': 254}
DATETIME_STRING_RULE = {'type': 'string', 'regex': '^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})*$'}
ATTRIBUTES_RULE = {
    'type': 'dict',
    'propertyschema': {
        'anyof': [
            {'type': 'string'},
            {'type': 'integer'}
        ]
    },
    'valueschema': {
        'anyof': [
            {'type': 'string'},
            {'type': 'integer'}
        ]
    }
}


rules = {
    'Account': {
        'pid': PID_RULE,
        'email': EMAIL_RULE,
        'username': {'type': 'string', 'maxlength': 100},
        'attributes': ATTRIBUTES_RULE,
        'person_id': {'type': 'integer', 'required': True},
    },
    'Person': {
        'pid': PID_RULE,
        'first_name': {'type': 'string', 'maxlength': 100},
        'given_names': {'type': 'string', 'maxlength': 256},
        'last_name': {'type': 'string', 'maxlength': 100},
        'accounts': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': 'Account',
            },
        },
    },
    'Awardee': {
        'pid': PID_RULE,
        'name': {'type': 'string', 'maxlength': 256, 'required': True, 'empty': False},
        'attributes': ATTRIBUTES_RULE,
        'award_id': {'type': 'integer'}
    },
    'Award': {
        'pid': PID_RULE,
        'number': {'type': 'string', 'maxlength': 64, 'required': True},
        'full_number': {'type': 'string'},
        'project_start': DATETIME_STRING_RULE,
        'project_end': DATETIME_STRING_RULE,
        'fiscal_year': {'type': 'string', 'regex': '^\d{4}$', 'coerce': 'int'},
        'budget_start': DATETIME_STRING_RULE,
        'budget_end': DATETIME_STRING_RULE,
        'title': {'type': 'string', 'maxlength': 256},
        'awardees': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': 'Awardee',
            },
        },
        'persons': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': 'Person',
            },
        },
        'funding_institution': {'type': 'string', 'maxlength': 50, 'required': True},
        'attributes': ATTRIBUTES_RULE
    },
}
