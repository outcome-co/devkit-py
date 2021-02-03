"""A small fix for odd pactman behaviour."""

from pactman import Pact as OriginalPact


class Pact(OriginalPact):  # pragma: no cover
    def and_given(self, provider_state, **params):
        if self.semver.major < 3:
            raise ValueError('pact v2 only allows a single provider state')
        elif not self._interactions:
            raise ValueError('only invoke and_given() after given()')
        self._interactions[0]['providerStates'].append({'name': provider_state, 'params': params})
        return self
