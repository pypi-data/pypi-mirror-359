import pickle
import pytest
from copy import deepcopy
from dataclasses import dataclass

import pydra


@dataclass
class MyClass:
    x: int
    y: str = "hello"


class TestConfig(pydra.Config):
    def __init__(self):
        self.foo1 = 1
        self.foo2 = "two"
        self.inner = pydra.DataclassWrapper(MyClass)


def test_pickle():
    conf = TestConfig()

    pydra.apply_overrides(
        conf,
        [
            "foo1=10",
            "foo2=astring",
            "inner.x=11",
            "inner.y=bstring",
        ],
    )

    pkl = pickle.dumps(conf)
    _ = pickle.loads(pkl)

    assert conf.foo1 == 10
    assert conf.foo2 == "astring"

    inner = conf.inner.build()
    assert inner.x == 11
    assert inner.y == "bstring"


def test_deepcopy():
    conf = TestConfig()

    pydra.apply_overrides(
        conf,
        [
            "foo1=10",
            "foo2=astring",
            "inner.x=11",
            "inner.y=bstring",
        ],
    )

    conf_copy = deepcopy(conf)

    pydra.apply_overrides(
        conf_copy,
        [
            "foo1=100",
            "inner.x=111",
        ],
    )

    assert conf.foo1 == 10
    assert conf.foo2 == "astring"

    assert conf_copy.foo1 == 100
    assert conf_copy.foo2 == "astring"

    inner = conf.inner.build()
    assert inner.x == 11
    assert inner.y == "bstring"

    inner_copy = conf_copy.inner.build()
    assert inner_copy.x == 111
    assert inner_copy.y == "bstring"
