from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from invoke import Context, Result
from outcome.devkit.invoke import docker
from syrupy.assertion import SnapshotAssertion


@pytest.fixture
def mocked_context():
    return Mock(spec=Context)


@patch('outcome.devkit.invoke.docker.container_exists', return_value=False)
def test_create_container_with_detach(mock_container_exists: Mock, mocked_context: Mock, snapshot: SnapshotAssertion):
    environment = {'MY_VAR': 'MY_VAR_VALUE', 'MY_OTHER_VAR': 'MY_OTHER_VAR_VALUE'}
    port = 80

    docker.create_container(mocked_context, 'my-container', 'my-image', environment=environment, port=port, detach=True)

    assert mocked_context.mock_calls == snapshot


@patch('outcome.devkit.invoke.docker.container_exists', return_value=False)
def test_create_container_without_detach(mock_container_exists: Mock, mocked_context: Mock, snapshot: SnapshotAssertion):
    environment = {'MY_VAR': 'MY_VAR_VALUE', 'MY_OTHER_VAR': 'MY_OTHER_VAR_VALUE'}

    docker.create_container(mocked_context, 'my-container', 'my-image', environment=environment, detach=False)

    assert mocked_context.mock_calls == snapshot


@patch('outcome.devkit.invoke.docker.container_exists', return_value=True)
def test_create_container_existing_container(mock_container_exists: Mock, mocked_context: Mock, snapshot: SnapshotAssertion):
    with pytest.raises(docker.DuplicateContainer):
        docker.create_container(mocked_context, 'my-container', 'my-image')


@patch('outcome.devkit.invoke.docker.container_exists', return_value=False)
def test_create_container_with_volume(mock_container_exists: Mock, mocked_context: Mock, snapshot: SnapshotAssertion):
    docker.create_container(mocked_context, 'my-container', 'my-image', volumes=[('example', 'volume')])

    assert mocked_context.mock_calls == snapshot


@patch('outcome.devkit.invoke.docker.container_exists', return_value=False)
def test_create_container_with_workdir(mock_container_exists: Mock, mocked_context: Mock, snapshot: SnapshotAssertion):
    docker.create_container(mocked_context, 'my-container', 'my-image', workdir='example_workdir')

    assert mocked_context.mock_calls == snapshot


@patch('outcome.devkit.invoke.docker.container_exists', return_value=False)
def test_create_container_with_command(mock_container_exists: Mock, mocked_context: Mock, snapshot: SnapshotAssertion):
    docker.create_container(mocked_context, 'my-container', 'my-image', command='my-command')

    assert mocked_context.mock_calls == snapshot


@patch('outcome.devkit.invoke.docker.container_exists', return_value=False)
def test_create_container_with_command_and_args(mock_container_exists: Mock, mocked_context: Mock, snapshot: SnapshotAssertion):
    docker.create_container(
        mocked_context, 'my-container', 'my-image', command='my-command', command_args=[('--flag',), ('--tag', '1.2.3')],
    )

    assert mocked_context.mock_calls == snapshot


def test_start_non_existant_container(mocked_context: Mock):
    with patch('outcome.devkit.invoke.docker.container_exists', return_value=False):
        with pytest.raises(docker.UnknownContainer):
            docker.start_container(mocked_context, 'unknown')


def test_start_not_running_container(mocked_context: Mock):
    with patch('outcome.devkit.invoke.docker.container_exists', return_value=True):
        with patch('outcome.devkit.invoke.docker.container_is_running', return_value=False):
            docker.start_container(mocked_context, 'known')
            mocked_context.run.assert_called_once_with('docker start known')


def test_start_running_container(mocked_context: Mock):
    with patch('outcome.devkit.invoke.docker.container_exists', return_value=True):
        with patch('outcome.devkit.invoke.docker.container_is_running', return_value=True):
            docker.start_container(mocked_context, 'known')
            mocked_context.run.assert_not_called()


def test_stop_running_container(mocked_context: Mock):
    with patch('outcome.devkit.invoke.docker.container_is_running', return_value=True):
        docker.stop_container(mocked_context, 'known')
        mocked_context.run.assert_called_once_with('docker stop known')


def test_stop_not_running_container(mocked_context: Mock):
    with patch('outcome.devkit.invoke.docker.container_is_running', return_value=False):
        docker.stop_container(mocked_context, 'known')
        mocked_context.run.assert_not_called()


@pytest.fixture(scope='session')
def stopped_container_output():
    path = Path(__file__).parent / Path('data', 'stopped_containers.txt')
    with open(path, 'r') as h:
        return h.read()


@pytest.fixture(scope='session')
def running_container_output():
    path = Path(__file__).parent / Path('data', 'running_containers.txt')
    with open(path, 'r') as h:
        return h.read()


@pytest.fixture(scope='session')
def all_container_output(stopped_container_output: str, running_container_output: str):
    return f'{stopped_container_output}{running_container_output}'


@pytest.fixture(scope='session')
def expected_running_docker_count(running_container_output: str):
    return len(running_container_output.splitlines())


@pytest.fixture(scope='session')
def expected_stopped_docker_count(stopped_container_output: str):
    return len(stopped_container_output.splitlines())


@pytest.fixture(scope='session')
def expected_all_docker_count(all_container_output: str):
    return len(all_container_output.splitlines())


def test_get_docker_containers_all(
    mocked_context: Mock, snapshot: SnapshotAssertion, all_container_output: str, expected_all_docker_count: int,
):
    result = Mock(spec=Result)

    result.stdout = all_container_output
    mocked_context.run.return_value = result

    dockers = docker.get_docker_containers(mocked_context, only_running=False)

    processes = list(dockers)
    assert mocked_context.run.mock_calls == snapshot
    # We're not actually testing that the returned amount is dependant on
    # the only_running flag, since we're providing the output
    # this assertion is just to check that we're not losing anything during
    # parsing
    assert len(processes) == expected_all_docker_count


def test_get_docker_containers(
    mocked_context: Mock, snapshot: SnapshotAssertion, running_container_output: str, expected_running_docker_count: int,
):
    result = Mock(spec=Result)

    result.stdout = running_container_output
    mocked_context.run.return_value = result

    dockers = docker.get_docker_containers(mocked_context, only_running=True)

    processes = list(dockers)
    assert mocked_context.run.mock_calls == snapshot

    # We're not actually testing that the returned amount is dependant on
    # the only_running flag, since we're providing the output
    # this assertion is just to check that we're not losing anything during
    # parsing
    assert len(processes) == expected_running_docker_count


def test_container_exists(mocked_context: Mock, all_container_output: str):
    result = Mock(spec=Result)

    result.stdout = all_container_output
    mocked_context.run.return_value = result

    assert docker.container_exists(mocked_context, 'review-api-app-db')
    assert not docker.container_exists(mocked_context, 'unknown')


def test_container_is_running(mocked_context: Mock, running_container_output: str):
    result = Mock(spec=Result)

    result.stdout = running_container_output
    mocked_context.run.return_value = result

    assert docker.container_is_running(mocked_context, 'review-api-app-db')
    assert not docker.container_is_running(mocked_context, 'unknown')
