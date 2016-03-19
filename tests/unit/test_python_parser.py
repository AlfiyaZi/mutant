from mutant.parsers.python_parser import PythonParser


def test_python_parser_sample():
    high_level = {
        'Department': [
            {'title': {'type': 'String'}},
            {'employee': {'type': 'List', 'entity': 'Employee'}},
        ],
        'Employee': [
            {'first_name': {'type': 'String'}},
        ],
    }
    expected = [
        {
            'name': 'Department',
            'fields': [
                {'name': 'title', 'type': 'String', 'options': {}},
                {'name': 'employee', 'type': 'List', 'options': {'entity': 'Employee'}},
            ],
            'options': {},
        },
        {
            'name': 'Employee',
            'fields': [
                {'name': 'first_name', 'type': 'String', 'options': {}},
            ],
            'options': {},
        },
    ]
    parser = PythonParser()
    result = parser.parse(high_level)
    assert result == expected
