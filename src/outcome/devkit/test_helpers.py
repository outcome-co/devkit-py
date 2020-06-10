"""Helper functions for writing test suites."""

from typing import Callable

import pytest
from outcome.utils import env


def skip_for_integration(fn: Callable) -> Callable:
    """Marks a unit test or test class as skippable during integration tests.

    Args:
        fn (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """
    decorator = pytest.mark.skipif(env.is_integration(), reason='Skipped in integration tests')
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