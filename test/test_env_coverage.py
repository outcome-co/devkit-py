import pytest

from coverage.config import CoverageConfig

from unittest.mock import patch, Mock

from outcome.devkit.env_coverage import EnvironmentExclusionPlugin, _ignore_opt_name
from outcome.utils import env


@pytest.fixture
def mock_config():
    mock = Mock(spec_set=CoverageConfig)

    internal_array = []

    def get(key):
        return internal_array.copy()

    def set_v(key, v):
        internal_array.clear()
        internal_array.extend(v)

    mock.get_option.side_effect = get
    mock.set_option.side_effect = set_v

    return mock


class TestEnvCoverage:
    @patch('outcome.devkit.env_coverage.env', auto_spec=True)
    def test_exclude_integration_tests(self, mock_env: Mock, mock_config: Mock):
        mock_env.is_integration.return_value = False
        mock_env.is_test.return_value = True

        plugin = EnvironmentExclusionPlugin()
        plugin.configure(mock_config)

        mock_config.set_option.assert_called_once_with(_ignore_opt_name, ['# pragma: exclude-from-integration-tests'])

    @patch('outcome.devkit.env_coverage.env', auto_spec=True)
    def test_exclude_unit_tests(self, mock_env: Mock, mock_config: Mock):
        mock_env.is_integration.return_value = True
        mock_env.is_test.return_value = False

        plugin = EnvironmentExclusionPlugin()
        plugin.configure(mock_config)

        mock_config.set_option.assert_called_once_with(_ignore_opt_name, ['# pragma: exclude-from-unit-tests'])

    @patch('outcome.devkit.env_coverage.env', auto_spec=True)
    def test_exclude_both(self, mock_env: Mock, mock_config: Mock):
        mock_env.is_integration.return_value = False
        mock_env.is_test.return_value = False

        plugin = EnvironmentExclusionPlugin()
        plugin.configure(mock_config)

        mock_config.set_option.assert_any_call(_ignore_opt_name, ['# pragma: exclude-from-unit-tests'])
        mock_config.set_option.assert_called_with(_ignore_opt_name, ['# pragma: exclude-from-unit-tests', '# pragma: exclude-from-integration-tests'])
