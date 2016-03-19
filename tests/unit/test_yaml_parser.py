from mutant.parsers.yaml_parser import YamlParser


def test_yaml_normalization():
    human_friendly = {
        'Department': [
            {'title': 'String'},
            {'employee': {'list-of': 'Employee'}},
        ],
        'Employee': [
            {'first_name': 'String'},
        ],
    }
    high_level = {
        'Department': [
            {'title': {'type': 'String'}},
            {'employee': {'type': 'List', 'entity': 'Employee'}},
        ],
        'Employee': [
            {'first_name': {'type': 'String'}},
        ],
    }
    result = YamlParser.normalize_schema(human_friendly)
    assert result == high_level
