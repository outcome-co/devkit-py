"""Utility to hide imports during tests."""

import sys
from contextlib import contextmanager


@contextmanager
def without_modules(*modules: str):
    """Run the code inside the context manager without the specified modules.

    Args:
        modules (*str): The names of the modules to hide from import.

    Yields:
        None
    """
    # Get all currently loaded modules
    excluded_modules = [m for m in sys.modules.keys() if any(m.startswith(ex_m) for ex_m in modules)]

    extracted_modules = {}

    # Delete them from the sys.modules
    # Setting them to None triggers an ImportError on attempted
    # import
    for m in excluded_modules:
        extracted_modules[m] = sys.modules[m]
        sys.modules[m] = None  # type: ignore

    yield

    # Clear the None so we can re-import if necessary
    for n in excluded_modules:
        sys.modules[n] = extracted_modules[n]
