"""Helper to get/cache various variables to be used during invoke tasks.

Provides a mechansim to declare keys, and how to determine the value of those keys.
The values are only resolved once, and can refer to other values in a form of informal graph.

For example:

from outcome.devkit.invoke import env

# The most basic scenario is to declare a value
env.declare('my_key', 'my constant')


# Or you can declare a value based on a function. The name of the function will be the key.
@env.add
def my_key(e: env.Env) -> str:
    return 'my static value'


# Functions can refer to other env keys, creating a graph - be careful of loops!
@env.add
def my_graph_key(e: env.Env) -> str:
    return e.read('my_key')


# As a shortcut, you can just refer to an environment variable
env.from_os('MY_ENV_VAR')
env.from_os('my_alias', os_key='MY_ENV_VAR')


# Then, you can read the value wherever
def my_func():
    val = env.read('my_key')
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Callable, Dict, Optional, Union, cast, overload

SourceFn = Callable[['Env'], Optional[str]]
Source = Union[SourceFn, str]
ReadKey = Union[str, 'EnvItem']


class EnvItem:
    """An EnvItem represents a specific key and value, and how to calculate that value.

    You shouldn't have to explicitly access EnvItem objects.
    """

    name: str
    run: bool
    value: Optional[str]
    source: Source
    env: Env
    required: bool

    def __init__(self, name: str, source: Source, env: Env, required: bool) -> None:
        self.name = name
        self.run = False
        self.value = None
        self.source = source
        self.env = env
        self.required = required

    def read(self) -> Optional[str]:
        if not self.run:
            if callable(self.source):
                self.value = self.source(self.env)
            else:
                self.value = self.source

            self.run = True

        if self.required and self.value is None:
            raise RuntimeError(f"Env item '{self.name}' is required!")

        return self.value


@contextmanager
def as_required(e: EnvItem):
    previous = e.required
    e.required = True
    yield
    e.required = previous


class Env:  # noqa: WPS214
    items: Dict[str, EnvItem]

    def __init__(self):
        self.reset()

    @overload
    def add(self, required: bool, key: Optional[str] = None) -> Callable[[SourceFn], EnvItem]:  # pragma: no cover
        ...

    @overload
    def add(self, fn: SourceFn, required: bool = True, key: Optional[str] = None) -> EnvItem:  # pragma: no cover
        ...

    def add(
        self, fn: Optional[SourceFn] = None, required: bool = True, key: Optional[str] = None,
    ) -> Union[EnvItem, Callable[[SourceFn], EnvItem]]:
        # This can be used as a straight decorator, or a parameterized decorator
        #
        # @env.add
        # def foo() -> str: ...  # noqa: E800
        #
        # @env.add(required=False)
        # def bar() -> Optional[str]: ...  # noqa: E800

        if callable(fn):
            key = key or fn.__name__
            return self._add(key, fn, required)

        def decorator(f: SourceFn) -> EnvItem:
            return self.add(f, required=required, key=key)

        return decorator

    def read(self, key: ReadKey, require: bool = False) -> Optional[str]:
        if isinstance(key, EnvItem):
            key = key.name

        try:
            item = self.items[key]

            if require:
                with as_required(item):
                    return item.read()
            else:
                return item.read()

        except KeyError:
            raise ValueError(f'Unknown env item! {key}')

    def strict_read(self, key: ReadKey) -> str:
        return cast(str, self.read(key, require=True))

    def from_os(self, key: str, os_key: Optional[str] = None, required: bool = True) -> EnvItem:
        effective_os_key = os_key or key

        def read_from_os(env: Env) -> Optional[str]:
            return os.environ.get(effective_os_key, None)

        return self.add(read_from_os, required=required, key=key)

    def declare(self, key: str, value: str) -> EnvItem:
        return self._add(key, value, required=True)

    def reset(self):
        self.items = {}

    def _add(self, key: str, source: Source, required: bool) -> EnvItem:
        if key in self.items:
            raise ValueError(f'Duplicate env item! {key}')

        self.items[key] = EnvItem(key, source, self, required)

        return self.items[key]


env = Env()


read = r = env.strict_read  # noqa: WPS429
nullable_read = env.read
add = env.add
from_os = env.from_os
declare = env.declare
reset = env.reset
