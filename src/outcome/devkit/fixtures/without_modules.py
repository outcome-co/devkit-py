"""A fixture to hide modules from import during tests.

For example, you want to test the following code:

```
try:
    import peewee
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
```

You can write the following test:
```
@pytest.mark.parametrize('modules_to_hide', [['peewee']])
@pytest.mark.usefixtures('with_hidden_modules')
def test_has_no_peewee():
    assert not my_mod.HAS_DATABASE
"""

import sys
from contextlib import contextmanager
from typing import List

import pytest


@pytest.fixture
def modules_to_hide() -> List[str]:  # pragma: no cover
    return []


@pytest.fixture
def with_hidden_modules(modules_to_hide: List[str]):
    with _hide_modules(*modules_to_hide):
        yield


@contextmanager
def _hide_modules(*modules: str):
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
