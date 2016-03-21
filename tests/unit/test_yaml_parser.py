from mutant_yaml.parser import YamlParser


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
    parser = YamlParser()
    result = parser.normalize_schema(human_friendly)
    assert result == high_level
