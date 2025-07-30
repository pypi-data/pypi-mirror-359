import pytest
from pydra import DataclassWrapper, PydanticWrapper, Config, apply_overrides
from pydantic import BaseModel, Field
from dataclasses import dataclass, field


@dataclass
class MyDataclass:
    a: int
    b: list[int] = field(default_factory=list)
    c: float = 4.0


class MyPydantic(BaseModel):
    a: int
    b: list[int] = Field(default_factory=list)
    c: float = 4.0


class MyConfig(Config):
    def __init__(self):
        self.wrapped_dataclass = DataclassWrapper(MyDataclass)
        self.wrapped_pydantic = PydanticWrapper(MyPydantic)


@pytest.fixture
def conf():
    return MyConfig()


def test_full_override_wrappers(conf):
    apply_overrides(
        conf,
        [
            "wrapped_dataclass.a=1",
            "wrapped_dataclass.b=[1,2]",
            "wrapped_dataclass.c=3",
            "wrapped_pydantic.a=4",
            "wrapped_pydantic.b=[5,6,7]",
            "wrapped_pydantic.c=8",
        ],
    )

    built_dataclass = conf.wrapped_dataclass.build()

    assert built_dataclass.a == 1
    assert built_dataclass.b == [1, 2]
    assert built_dataclass.c == 3

    built_pydantic = conf.wrapped_pydantic.build()

    assert built_pydantic.a == 4
    assert built_pydantic.b == [5, 6, 7]
    assert built_pydantic.c == 8


def test_default_values_wrappers(conf):
    apply_overrides(
        conf,
        [
            "wrapped_dataclass.a=1",
            "wrapped_dataclass.b=[1,2]",
            "wrapped_pydantic.a=4",
            "wrapped_pydantic.b=[5,6,7]",
        ],
    )

    built_dataclass = conf.wrapped_dataclass.build()
    assert built_dataclass.a == 1
    assert built_dataclass.b == [1, 2]
    assert built_dataclass.c == 4.0

    built_pydantic = conf.wrapped_pydantic.build()
    assert built_pydantic.a == 4
    assert built_pydantic.b == [5, 6, 7]
    assert built_pydantic.c == 4.0


def test_default_factory_wrappers(conf):
    apply_overrides(
        conf,
        [
            "wrapped_dataclass.a=1",
            "wrapped_dataclass.c=4",
            "wrapped_pydantic.a=4",
            "wrapped_pydantic.c=8",
        ],
    )

    built_dataclass = conf.wrapped_dataclass.build()
    assert built_dataclass.a == 1
    assert built_dataclass.b == []
    assert built_dataclass.c == 4.0

    built_pydantic = conf.wrapped_pydantic.build()
    assert built_pydantic.a == 4
    assert built_pydantic.b == []
    assert built_pydantic.c == 8.0


def test_missing_field_wrappers(conf):
    with pytest.raises(ValueError):
        conf.wrapped_dataclass.build()

    with pytest.raises(ValueError):
        conf.wrapped_pydantic.build()
