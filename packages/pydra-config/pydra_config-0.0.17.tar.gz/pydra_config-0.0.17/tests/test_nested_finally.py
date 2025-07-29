import pytest

from pydra import Config, run


class InnerConfig(Config):
    def __init__(self):
        self.x = 1
        self.y = 2

    def finalize(self):
        self.x = 10
        self.y = 20


class MiddleConfig(Config):
    def __init__(self):
        self.x = 1
        self.y = 2
        self.inner = InnerConfig()

    def finalize(self):
        self.x = 10
        self.y = 20


class OutermostConfig(Config):
    def __init__(self):
        self.x = 1
        self.y = 2

        self.configs = [MiddleConfig(), MiddleConfig()]

    def finalize(self):
        self.x = 10
        self.y = 20


def helper_function(config: OutermostConfig):
    return (
        config.x,
        config.y,
        config.configs[0].x,
        config.configs[0].y,
        config.configs[0].inner.x,
        config.configs[0].inner.y,
        config.configs[1].x,
        config.configs[1].y,
        config.configs[1].inner.x,
        config.configs[1].inner.y,
    )


def test_nested_finally():
    result = run(helper_function, [])
    assert result == (
        10,
        20,
        10,
        20,
        10,
        20,
        10,
        20,
        10,
        20,
    )
