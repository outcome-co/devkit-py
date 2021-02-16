from typing import Any, List, cast
from unittest.mock import Mock, patch

import pytest
from coverage.config import CoverageConfig
from outcome.devkit.env_coverage import EnvironmentExclusionPlugin, ignore_opt_name


class MockedCoverageConfig(Mock):
    get_option: Mock
    set_option: Mock


class MockedEnv(Mock):
    is_integration: Mock
    is_test: Mock


@pytest.fixture
def mock_config():
    mock = cast(MockedCoverageConfig, Mock(spec_set=CoverageConfig))

    internal_array: List[Any] = []

    def get(key: str):
        return internal_array.copy()

    def set_v(key: str, v: Any):
        internal_array.clear()
        internal_array.extend(v)

    mock.get_option.side_effect = get
    mock.set_option.side_effect = set_v

    return mock


class TestEnvCoverage:
    @patch('outcome.devkit.env_coverage.env', auto_spec=True)
    def test_exclude_integration_tests(self, mock_env: MockedEnv, mock_config: MockedCoverageConfig):
        mock_env.is_integration.return_value = False
        mock_env.is_test.return_value = True

        plugin = EnvironmentExclusionPlugin()
        plugin.configure(mock_config)

        mock_config.set_option.assert_called_once_with(ignore_opt_name, ['# pragma: only-covered-in-integration-tests'])

    @patch('outcome.devkit.env_coverage.env', auto_spec=True)
    def test_exclude_unit_tests(self, mock_env: MockedEnv, mock_config: MockedCoverageConfig):
        mock_env.is_integration.return_value = True
        mock_env.is_test.return_value = False

        plugin = EnvironmentExclusionPlugin()
        plugin.configure(mock_config)

        mock_config.set_option.assert_called_once_with(ignore_opt_name, ['# pragma: only-covered-in-unit-tests'])

    @patch('outcome.devkit.env_coverage.env', auto_spec=True)
    def test_exclude_both(self, mock_env: MockedEnv, mock_config: MockedCoverageConfig):
        mock_env.is_integration.return_value = False
        mock_env.is_test.return_value = False

        plugin = EnvironmentExclusionPlugin()
        plugin.configure(mock_config)

        mock_config.set_option.assert_any_call(ignore_opt_name, ['# pragma: only-covered-in-unit-tests'])
        mock_config.set_option.assert_called_with(
            ignore_opt_name, ['# pragma: only-covered-in-unit-tests', '# pragma: only-covered-in-integration-tests'],
        )
