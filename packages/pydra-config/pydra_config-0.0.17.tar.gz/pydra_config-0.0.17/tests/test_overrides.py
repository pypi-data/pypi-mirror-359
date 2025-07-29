import pytest
from dataclasses import dataclass

from pydra import REQUIRED, Alias, Config, DataclassWrapper, apply_overrides


class TestConfig(Config):
    def __init__(self):
        self.foo1 = 1
        self.foo2 = "two"

    def bar1(self):
        self.foo1 = 10

    def inc_foo1(self, increment, extra_decrement=0):
        self.foo1 += increment - extra_decrement


@pytest.fixture
def test_config():
    return TestConfig()


def test_empty_args(test_config):
    args = []
    show = apply_overrides(test_config, args)
    assert not show
    assert test_config.foo1 == 1
    assert test_config.foo2 == "two"


def test_basic(test_config):
    args = ["foo1=12", "foo2=hi"]
    show = apply_overrides(test_config, args)
    assert not show
    assert test_config.foo1 == 12
    assert test_config.foo2 == "hi"


def test_lists(test_config):
    args = ["foo1=[True,2,'a']", "foo2=['a',None,1.0]"]
    apply_overrides(test_config, args)
    assert test_config.foo1 == [True, 2, "a"]
    assert test_config.foo2 == ["a", None, 1.0]


def test_mixed(test_config):
    args = ["foo1=12", "foo2=None", "foo1=[1,2,3]"]
    apply_overrides(test_config, args)
    assert test_config.foo1 == [1, 2, 3]
    assert test_config.foo2 is None


def test_show_flag(test_config):
    args = ["foo1=12", "--show", "foo2=three"]
    show = apply_overrides(test_config, args)
    assert show


def test_method_call(test_config):
    args = [".bar1"]
    apply_overrides(test_config, args)
    assert test_config.foo1 == 10


def test_method_call_with_args(test_config):
    args = [".inc_foo1(5)"]
    apply_overrides(test_config, args)
    assert test_config.foo1 == 6


def test_method_kwargs(test_config):
    args = [".inc_foo1(increment=5)"]
    apply_overrides(test_config, args)
    assert test_config.foo1 == 6


def test_method_args_kwargs(test_config):
    args = [".inc_foo1(5,extra_decrement=1)"]
    apply_overrides(test_config, args)
    assert test_config.foo1 == 5


def test_field_doesnt_exist(test_config):
    args = ["foo3=3"]
    with pytest.raises(AttributeError):
        apply_overrides(test_config, args)


class NestedConfig(Config):
    def __init__(self):
        self.nested_value = "original"
        self.long_name = 15
        self.short_name = Alias("long_name")


class ComplexTestConfig(Config):
    def __init__(self):
        self.nested = NestedConfig()
        self.normal_dict = {"a": 1, "b": 2}

        self.long_name = 5
        self.short_name = Alias("long_name")

        self.alias_nest = Alias("nested")


@pytest.fixture
def complex_config():
    return ComplexTestConfig()


def test_normal_dict_assignment(complex_config):
    args = ["normal_dict.a=3"]
    apply_overrides(complex_config, args)
    assert complex_config.normal_dict == {"a": 3, "b": 2}


def test_local_alias_assignment(complex_config):
    args = ["short_name=20"]
    apply_overrides(complex_config, args)
    assert complex_config.long_name == 20


def test_nested_local_alias_assignment(complex_config):
    args = ["nested.short_name=25"]
    apply_overrides(complex_config, args)
    assert complex_config.nested.long_name == 25


def test_nested_alias_assignment(complex_config):
    args = ["alias_nest.long_name=30"]
    apply_overrides(complex_config, args)
    assert complex_config.nested.long_name == 30


def test_mixed_alias_assignments(complex_config):
    args = ["short_name=40", "nested.short_name=35"]
    apply_overrides(complex_config, args)
    assert complex_config.long_name == 40
    assert complex_config.nested.long_name == 35


def test_alias_short_then_long(complex_config):
    args = ["short_name=40", "long_name=2"]
    apply_overrides(complex_config, args)
    assert complex_config.long_name == 2


def test_alias_long_then_short(complex_config):
    args = ["long_name=2", "short_name=40"]
    apply_overrides(complex_config, args)
    assert complex_config.long_name == 40


def test_double_alias(complex_config):
    args = ["alias_nest.short_name=45"]
    apply_overrides(complex_config, args)
    assert complex_config.nested.long_name == 45


def test_alias_with_scope(complex_config):
    args = ["--in", "nested", "short_name=45", "in--"]
    apply_overrides(complex_config, args)
    assert complex_config.nested.long_name == 45


@dataclass
class MyDataclass:
    x: int
    y: str
    z: float = 1.0


class DC_Config(Config):
    def __init__(self):
        self.dc = DataclassWrapper(MyDataclass)

    def finalize(self):
        self.built_dc = self.dc.build()


@pytest.fixture
def dc_config():
    return DC_Config()


def test_dataclass_assignment(dc_config):
    args = ["dc.x=3", "dc.y=hi", "dc.z=2.0"]
    apply_overrides(dc_config, args)
    assert dc_config.built_dc == MyDataclass(3, "hi", 2.0)


def test_dataclass_assignment_with_defaults(dc_config):
    args = ["dc.x=3", "dc.y=hi"]
    apply_overrides(dc_config, args)
    assert dc_config.built_dc == MyDataclass(3, "hi")


def test_dataclass_missing_field(dc_config):
    args = ["dc.x=3"]
    with pytest.raises(ValueError):
        apply_overrides(dc_config, args)


def test_assign_nonexistent_field(dc_config):
    args = ["dc.w=3"]
    with pytest.raises(AttributeError):
        apply_overrides(dc_config, args)


class NestedToSerialize(Config):
    def __init__(self):
        self.nested_foo = "nested_bar"


class ConfigToSerialize(Config):
    def __init__(self):
        self.foo = 1
        self.bar = "two"
        self.baz = 3.0
        self.qux = [1, 2, 3]
        self.qux_tuple = (1, 2, 3)
        self.quux = {"a": 1, "b": 2}
        self.nested = NestedToSerialize()


@pytest.fixture
def config_to_serialize():
    return ConfigToSerialize()


def test_serialization(config_to_serialize):
    args = [
        "foo=12",
        "bar=hi",
    ]
    apply_overrides(config_to_serialize, args)
    serialized = config_to_serialize.to_dict()
    expected = {
        "foo": 12,
        "bar": "hi",
        "baz": 3.0,
        "qux": [1, 2, 3],
        "qux_tuple": [1, 2, 3],
        "quux": {"a": 1, "b": 2},
        "nested": {"nested_foo": "nested_bar"},
    }
    assert serialized == expected


class ConfigWithRequired(Config):
    def __init__(self):
        self.required = REQUIRED
        self.optional = 5
        self.final_val = None

    def finalize(self):
        self.final_val = self.required + 1


@pytest.fixture
def config_with_required():
    return ConfigWithRequired()


def test_required_missing(config_with_required):
    with pytest.raises(ValueError):
        apply_overrides(config_with_required, ["optional=10"])


def test_required_present(config_with_required):
    apply_overrides(config_with_required, ["required=10"])
    assert config_with_required.required == 10


def test_finalize(config_with_required):
    apply_overrides(config_with_required, ["required=10"])
    assert config_with_required.final_val == 11


class FurtherInnerConfig(Config):
    x: int = 10
    y: int = 20

    def further_inner_method(self):
        self.x = 11


class InnerConfig(Config):
    a: int = 1
    b: int = 2

    def __init__(self):
        super().__init__()
        self.further_inner = FurtherInnerConfig()

    def inner_method(self):
        self.a = 3


class OuterConfig(Config):
    def __init__(self):
        super().__init__()
        self.inner = InnerConfig()


@pytest.fixture
def outer_config():
    return OuterConfig()


def test_nested_methods(outer_config):
    apply_overrides(
        outer_config,
        [".inner.inner_method", ".inner.further_inner.further_inner_method"],
    )
    assert outer_config.inner.a == 3
    assert outer_config.inner.further_inner.x == 11
