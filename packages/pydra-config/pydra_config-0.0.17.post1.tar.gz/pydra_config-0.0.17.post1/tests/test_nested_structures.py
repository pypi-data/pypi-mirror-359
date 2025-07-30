import pytest

from pydra import Config, apply_overrides
from pydra.parser import parse_value


class NestedStructConfig(Config):
    def __init__(self):
        self.simple_list = []
        self.nested_list = []
        self.dict_value = {}
        self.mixed_structure = None
        self.tuple_value = None


# Tests for parse_value function
def test_parse_value_nested_lists():
    assert parse_value("[[1,2],[3,4]]") == [[1, 2], [3, 4]]
    assert parse_value("[[[1,2],3],[4,[5,6]]]") == [[[1, 2], 3], [4, [5, 6]]]


def test_parse_value_nested_dicts():
    assert parse_value('{"a": 1, "b": 2}') == {"a": 1, "b": 2}
    assert parse_value('{"a": [1,2,3], "b": {"nested": True}}') == {
        "a": [1, 2, 3],
        "b": {"nested": True},
    }


def test_parse_value_mixed_structures():
    assert parse_value('[(1,2), (3,4,5), {"key": (6,7)}]') == [
        (1, 2),
        (3, 4, 5),
        {"key": (6, 7)},
    ]
    assert parse_value('[{"a": [1,2]}, {"b": [3,4]}]') == [
        {"a": [1, 2]},
        {"b": [3, 4]},
    ]


def test_parse_value_tuples():
    assert parse_value("(1,2,3)") == (1, 2, 3)
    assert parse_value("((1,2),(3,4))") == ((1, 2), (3, 4))


def test_parse_value_complex_expressions():
    # Expressions in parentheses use eval
    assert parse_value("([1,2] + [3,4])") == [1, 2, 3, 4]
    assert parse_value("(2 ** 3)") == 8
    assert list(parse_value('({"a": 1, "b": 2}.keys())')) == ["a", "b"]


# End-to-end tests with Config objects
@pytest.fixture
def config():
    return NestedStructConfig()


def test_simple_nested_list_override(config):
    args = ["nested_list=[[1,2],[3,4]]"]
    apply_overrides(config, args)
    assert config.nested_list == [[1, 2], [3, 4]]


def test_deeply_nested_list_override(config):
    args = ["nested_list=[[[1,2],3],[4,[5,6]]]"]
    apply_overrides(config, args)
    assert config.nested_list == [[[1, 2], 3], [4, [5, 6]]]


def test_dict_override(config):
    args = ['dict_value={"a": 1, "b": 2, "c": [1,2,3]}']
    apply_overrides(config, args)
    assert config.dict_value == {"a": 1, "b": 2, "c": [1, 2, 3]}


def test_nested_dict_override(config):
    args = ['dict_value={"outer": {"inner": [1,2,3], "flag": True}}']
    apply_overrides(config, args)
    assert config.dict_value == {"outer": {"inner": [1, 2, 3], "flag": True}}


def test_mixed_structure_override(config):
    args = [
        'mixed_structure=[{"name": "item1", "values": [1,2,3]}, {"name": "item2", "values": [4,5,6]}]'
    ]
    apply_overrides(config, args)
    assert config.mixed_structure == [
        {"name": "item1", "values": [1, 2, 3]},
        {"name": "item2", "values": [4, 5, 6]},
    ]


def test_tuple_override(config):
    args = ["tuple_value=(1,2,3)"]
    apply_overrides(config, args)
    assert config.tuple_value == (1, 2, 3)


def test_multiple_nested_overrides(config):
    args = [
        "simple_list=[1,2,3]",
        "nested_list=[[1,2],[3,4]]",
        'dict_value={"a": [1,2], "b": {"nested": True}}',
        "tuple_value=((1,2),(3,4))",
    ]
    apply_overrides(config, args)
    assert config.simple_list == [1, 2, 3]
    assert config.nested_list == [[1, 2], [3, 4]]
    assert config.dict_value == {"a": [1, 2], "b": {"nested": True}}
    assert config.tuple_value == ((1, 2), (3, 4))


def test_expression_in_parentheses(config):
    args = [
        "simple_list=([1,2] + [3,4])",
        'mixed_structure=({"a": 1, "b": 2}.items())',
    ]
    apply_overrides(config, args)
    assert config.simple_list == [1, 2, 3, 4]
    assert list(config.mixed_structure) == [("a", 1), ("b", 2)]
