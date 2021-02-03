"""A small fix for odd pactman behaviour."""

from pactman import Pact as OriginalPact


class Pact(OriginalPact):  # pragma: no cover
    def given(self, provider_state, **params):  # noqa: WPS231
        if provider_state is None:
            self._interactions.append({})
            return self

        if self.semver.major < 3:
            provider_state_key = 'providerState'
            if not isinstance(provider_state, str):
                raise ValueError('pact v2 provider states must be strings')
        else:
            provider_state_key = 'providerStates'
            if isinstance(provider_state, str):
                provider_state = [{'name': provider_state, 'params': params}]
            elif not isinstance(provider_state, list):
                raise ValueError('pact v3+ provider states must be lists of {name: "", params: {}} specs')
        self._interactions.append({provider_state_key: provider_state})
        return self
