from unittest.mock import Mock, patch

import pytest
from outcome.devkit.invoke import env
from outcome.utils.config import Config


@pytest.fixture(autouse=True)
def reset():
    env.reset()


def test_declare():
    env.declare('my_key', 'value')
    assert env.r('my_key') == 'value'


def test_from_os():
    with patch.dict('os.environ', {'MY_KEY': 'val'}):
        env.from_os('MY_KEY')
        assert env.read('MY_KEY') == 'val'


def test_cache_env_item():
    fn = Mock()
    fn.return_value = '123'
    fn.__name__ = 'my_key'  # noqa: WPS125

    env.add(fn)

    assert env.r('my_key') == '123'
    assert env.r('my_key') == '123'

    fn.assert_called_once()


def test_read_unknown():
    with pytest.raises(ValueError):
        env.r('unknown')


def test_add_duplicate():
    def my_key(e: env.Env) -> str:
        return 'other'

    with pytest.raises(ValueError):
        env.declare('my_key', 'val')
        env.add(my_key)


def test_read_from_env():
    i = env.declare('my_key', 'val')

    assert env.r('my_key') == env.r(i)


def test_read_none_for_required():
    def my_none(e: env.Env) -> None:
        return  # noqa: WPS324

    env.add(my_none)

    with pytest.raises(RuntimeError):
        env.r('my_none')


def test_optional_read():
    def my_none(e: env.Env) -> None:
        return  # noqa: WPS324

    i = env.add(my_none, required=False)

    assert env.env.read(i, require=False) is None


def test_parameterized_decorator():
    @env.add(required=False, key='my_key')
    def my_func(e: env.Env) -> str:
        return 'foo'

    assert my_func.required is False
    assert my_func.name == 'my_key'


def test_config():
    config = Config(defaults={'MY_KEY': 'var'})
    i = env.from_config('MY_KEY', config=config)
    assert env.r(i) == 'var'
