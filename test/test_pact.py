# To include it in the coverage
from pathlib import Path
from typing import Iterator

import pytest
import requests
from outcome.devkit.pact import Pact
from pactman import Consumer, Provider

pact_dir = 'pacts/providers'

hostname = 'localhost'
port = 8000
success_status = 200

path = '/any/path'
other_path = '/other/path'
wrong_path = '/wrong/path'

url = f'http://{hostname}:{port}{path}'
other_url = f'http://{hostname}:{port}{other_path}'
wrong_url = f'http://{hostname}:{port}{wrong_path}'

body = {'response': 'Interaction - Matched'}
other_body = {'response': 'Interaction other path - Matched'}


@pytest.fixture
def pact_api() -> Iterator[Pact]:
    Path(pact_dir).mkdir(parents=True, exist_ok=True)

    pact_api = Consumer('consumer', service_cls=Pact).has_pact_with(
        Provider('provider'), host_name=hostname, port=port, pact_dir=pact_dir, version='3.0.0',
    )

    with pact_api:
        yield pact_api


@pytest.fixture
def interaction(pact_api: Pact):
    pact_api.given('Test interaction')
    pact_api.upon_receiving('Test request')
    pact_api.with_request(method='GET', path=path)
    pact_api.will_respond_with(status=success_status, body=body)


@pytest.fixture
def interaction_other_path(pact_api: Pact):
    pact_api.given('Test interaction on other path')
    pact_api.upon_receiving('Test request on other path')
    pact_api.with_request(method='GET', path=other_path)
    pact_api.will_respond_with(status=success_status, body=other_body)


@pytest.fixture
def other_interaction_on_same_path(pact_api: Pact):
    pact_api.given('Other Test Interaction')
    pact_api.upon_receiving('Another Test Request')
    pact_api.with_request(method='GET', path=path)
    pact_api.will_respond_with(status=success_status, body=body)


class PytestRequest:
    param: str

    def getfixturevalue(self, interaction: str) -> None:
        ...


@pytest.fixture(params=[['interaction', 'interaction_other_path'], ['interaction_other_path', 'interaction']])
def interactions_parametrized_order(request: PytestRequest):
    for interaction in request.param:
        request.getfixturevalue(interaction)


class TestMockURLOpenHandler:
    @pytest.mark.usefixtures('interaction')
    def test_get_interaction_from_path(self):
        response = requests.get(url=url)
        assert response.status_code == success_status
        assert response.json() == body

    @pytest.mark.usefixtures('interaction_other_path')
    def test_get_other_interaction_from_path(self):
        response = requests.get(url=other_url)
        assert response.status_code == success_status
        assert response.json() == other_body

    @pytest.mark.usefixtures('interactions_parametrized_order')
    def test_get_multiple_interactions_from_paths(self):
        response = requests.get(url=url)
        assert response.status_code == success_status
        assert response.json() == body

        response = requests.get(url=other_url)
        assert response.status_code == success_status
        assert response.json() == other_body

    @pytest.mark.usefixtures('interaction', 'other_interaction_on_same_path')
    def test_get_interaction_from_path_fail_several(self):
        with pytest.raises(AssertionError, match='several interactions matching'):
            requests.get(url=url)

    @pytest.mark.usefixtures('interaction')
    def test_get_interaction_from_path_fail_wrong_path(self):
        with pytest.raises(AssertionError, match='no interaction matching'):
            requests.get(url=wrong_url)

    @pytest.mark.usefixtures('pact_api')
    def test_get_interaction_from_path_fail_none(self):
        with pytest.raises(AssertionError, match='no interaction matching'):
            requests.get(url=url)
