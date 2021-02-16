"""Pact test helpers."""
from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, cast

from pactman import Pact as OriginalPact

if TYPE_CHECKING:  # pragma: no cover
    from pactman.mock.pact import V3Interaction  # noqa: WPS433


# This is a helper decorator that should be used on pact setup functions
# it automatically uses the pact context manager to in pytest fixtures
def with_pact(func: Callable[..., Pact]):  # pragma: no cover
    @wraps(func)
    def wrapped(*args: Any, **kwargs: Any):
        pact = func(*args, **kwargs)
        with pact:
            yield pact

    return wrapped


class Pact(OriginalPact):  # pragma: no cover
    # This is a fix - the official pactman library inserts new interactions at the beginning
    # of the _interactions array, but then uses the last item in the array when using `and_given`
    # This override addresses the index alignment issue.
    def and_given(self, provider_state: str, **params: str):

        self.semver

        if self.semver.major < 3:
            raise ValueError('pact v2 only allows a single provider state')
        elif not self._interactions:
            raise ValueError('only invoke and_given() after given()')

        # We know that we're dealing with V3
        most_recent_interaction = cast(V3Interaction, self._interactions[0])
        most_recent_interaction['providerStates'].append({'name': provider_state, 'params': params})
        return self


__all__ = ['Pact', 'with_pact']
