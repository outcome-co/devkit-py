"""Helper functions for writing test suites."""

from typing import Callable

import pytest
from outcome.utils import env


def skip_for_e2e(fn: Callable) -> Callable:
    """Marks a unit test or test class as skippable during e2e tests.

    Args:
        fn (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """
    decorator = pytest.mark.skipif(env.is_e2e(), reason='Skipped in e2e tests')
    return decorator(fn)


def only_for_e2e(fn: Callable) -> Callable:
    """Marks a unit test or test class as skippable during e2e tests.

    Args:
        fn (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """
    decorator = pytest.mark.skipif(not env.is_e2e(), reason='Only for e2e tests')
    return decorator(fn)


def skip_for_integration(fn: Callable) -> Callable:
    """Marks a unit test or test class as skippable during integration tests.

    Args:
        fn (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """
    decorator = pytest.mark.skipif(env.is_integration(), reason='Skipped in integration tests')
    return decorator(fn)


def only_for_integration(fn: Callable) -> Callable:
    """Marks a unit test or test class as skippable during integration tests.

    Args:
        fn (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """
    decorator = pytest.mark.skipif(not env.is_integration(), reason='Only for integration tests')
    return decorator(fn)


def skip_for_unit(fn: Callable) -> Callable:
    """Marks a unit test or test class as skippable during unit tests.

    Args:
        fn (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """
    decorator = pytest.mark.skipif(env.is_test() and not env.is_integration(), reason='Skipped in unit tests')
    return decorator(fn)


def only_for_unit(fn: Callable) -> Callable:
    """Marks a unit test or test class as skippable during unit tests.

    Args:
        fn (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """
    decorator = pytest.mark.skipif(not env.is_test(), reason='Only for unit tests')
    return decorator(fn)
