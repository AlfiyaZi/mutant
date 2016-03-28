from mutant_short.middleware import ShorthandMiddleware


def test_yaml_normalization():
    human_friendly = {
        'Department': [
            'title',
            {'employees': {'list-of': ['first_name']}},
        ],
    }
    high_level = {
        'Department': [
            {'title': {'type': 'String'}},
            {'employees': {'type': 'List', 'entity': 'Employee', 'own': True}},
        ],
        'Employee': [
            {'first_name': {'type': 'String'}},
        ],
    }
    middleware = ShorthandMiddleware()
    result = middleware.before_parse(human_friendly)
    assert result == high_level
