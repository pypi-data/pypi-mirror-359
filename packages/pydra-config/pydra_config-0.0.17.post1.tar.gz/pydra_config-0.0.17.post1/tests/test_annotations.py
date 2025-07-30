import pytest
from pathlib import Path
from typing import Optional

import pydra


class DoubleInt:
    def __init__(self, value: int):
        assert isinstance(value, int)
        self.value = value * 2


class ConfigWithAnnotations(pydra.Config):
    a: int = 4
    b: DoubleInt
    c: float = 6.0

    def __init__(self):
        super().__init__()
        self.d = "hi"


class ConfigWithOptional(pydra.Config):
    opt1: Optional[Path]


class DerivedConfigWithOptional(ConfigWithOptional):
    opt2: Path | None = None


class ConfigWithAnnotationsAndInit(pydra.Config):
    a: int = 4
    b: int = 1

    def __init__(self):
        super().__init__()
        self.a = 5


def test_annotations():
    config = ConfigWithAnnotations()

    pydra.apply_overrides(config, ["a=5.2", "b=11", "c=7.0", "d=bye"])

    assert config.a == 5
    assert isinstance(config.b, DoubleInt)
    assert config.b.value == 22
    assert config.c == 7.0
    assert config.d == "bye"


def test_annotations_with_missing():
    config = ConfigWithAnnotations()

    with pytest.raises(ValueError):
        pydra.apply_overrides(config, ["a=5.2", "c=7.0"])


def test_optional_annotations():
    config = DerivedConfigWithOptional()
    pydra.apply_overrides(config, ["opt1=hi", "opt2=bye"])
    assert config.opt1 == Path("hi")
    assert config.opt2 == Path("bye")

    pydra.apply_overrides(config, ["opt1=foo", "opt2=None"])
    assert config.opt1 == Path("foo")
    assert config.opt2 is None


def test_annotations_and_init():
    config = ConfigWithAnnotationsAndInit()
    pydra.apply_overrides(config, ["b=2"])
    assert config.a == 5
    assert config.b == 2
