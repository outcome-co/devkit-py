"""Helper functions for writing test suites."""

from typing import Any, Callable, List, Protocol, Tuple, TypeVar, Union, cast

import pytest
from outcome.utils import env


class Mark(Protocol):
    name: str
    args: Tuple[Any, ...]


class Marked(Protocol):
    pytestmark: List[Mark]


# Taken from pytest
_Markable = TypeVar('_Markable', bound=Union[Callable[..., object], type])

# We cast to _Markable as pytest uses type overrides which obscure the real time


def skip_for_e2e(fn: _Markable) -> _Markable:
    decorated = pytest.mark.skipif(env.is_e2e(), reason='Skipped in e2e tests')(fn)
    return cast(_Markable, decorated)


def only_for_e2e(fn: _Markable) -> _Markable:
    decorated = pytest.mark.skipif(not env.is_e2e(), reason='Only for e2e tests')(fn)
    return cast(_Markable, decorated)


def skip_for_integration(fn: _Markable) -> _Markable:
    decorated = pytest.mark.skipif(env.is_integration(), reason='Skipped in integration tests')(fn)
    return cast(_Markable, decorated)


def only_for_integration(fn: _Markable) -> _Markable:
    decorated = pytest.mark.skipif(not env.is_integration(), reason='Only for integration tests')(fn)
    return cast(_Markable, decorated)


def skip_for_unit(fn: _Markable) -> _Markable:
    decorated = pytest.mark.skipif(env.is_test() and not env.is_integration(), reason='Skipped in unit tests')(fn)
    return cast(_Markable, decorated)


def only_for_unit(fn: _Markable) -> _Markable:
    decorated = pytest.mark.skipif(not env.is_test(), reason='Only for unit tests')(fn)
    return cast(_Markable, decorated)
