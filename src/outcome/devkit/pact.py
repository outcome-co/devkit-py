"""Pact test helpers."""
from __future__ import annotations

import urllib.parse
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, cast

from pactman import Pact as OriginalPact
from pactman.mock.mock_urlopen import MockURLOpenHandler as OriginalMockURLOpenHandler
from pactman.mock.pact_request_handler import RecordResult, Request
from pactman.verifier.verify import RequestVerifier
from urllib3.response import HTTPResponse

if TYPE_CHECKING:  # pragma: no cover
    from pactman.mock.pact import V3Interaction  # noqa: WPS433
else:
    V3Interaction = Any  # noqa: WPS440


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

    # We need to override the `OriginalPact` `start_mocking` method to use our custom `MockURLOpenHandler`
    # that changes the way Pactman gets interactions.
    def start_mocking(self):
        if self.use_mocking_server:
            super().start_mocking()
        else:
            # Pactman comment: ain't no port, we're monkey-patching (but the URLs we generate still need to look correct)
            self._mock_handler = MockURLOpenHandler(self)


class MockURLOpenHandler(OriginalMockURLOpenHandler):
    def validate_request(self, method: str) -> HTTPResponse:  # pragma: no cover
        url_parts = urllib.parse.urlparse(self.path)

        # Only modification from the original `validate_request`: we add the `method` arg to `get_interaction`
        interaction = self.get_interaction_from_path(method=method, path=url_parts.path)

        body = self.get_body()

        request = Request(method, url_parts.path, url_parts.query, self.headers, body)
        result = RecordResult()
        RequestVerifier(self.pact, interaction['request'], result).verify(request)

        if not result.success:
            return self.handle_failure(result.reason)
        self.handle_success(interaction)
        if self.pact.file_write_mode != 'never':
            self.write_pact(interaction)
        return self.respond_for_interaction(interaction)

    def get_interaction_from_path(self, method: str, path: str):
        # This is our custom way to `get_interaction` to improve the original way (which is `self.interactions.pop()`)
        matched_interactions = []

        for interaction in self.interactions:
            interaction_method = interaction['request']['method'].lower()
            interaction_path = interaction['request']['path'].lower()
            if interaction_method == method.lower() and interaction_path == path.lower():
                matched_interactions.append(interaction)

        if len(matched_interactions) > 1:
            raise AssertionError(f'Request {method} at {path} received, several interactions matching')
        elif not matched_interactions:
            raise AssertionError(f'Request {method} at {path} received, no interaction matching')
        return matched_interactions[0]


__all__ = ['Pact', 'with_pact']
