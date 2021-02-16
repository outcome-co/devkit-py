"""Dynamically adapt coverage reporting based on the current environment.

Some code is tested by unit tests, some code is only tested by integration tests,
we want to ensure we're calculating the correct coverage based on the environment,
i.e. we're not trying to get 100% code coverage, we're trying to get 100% coverage
for the code that it makes sense to test.

This plugin allows us to use two new pragmas that will exclude lines from coverage
based on the environement (as determined by the `env` module).

You can use `pragma: no-cover-for-test` to exclude code that shouldn't be covered by unit tests,
and `pragm: no-cover-for-integration` for code that shouldn't be covered by integration tests.
"""
from typing import Any, Callable, Dict

from coverage import CoveragePlugin
from coverage.config import CoverageConfig
from coverage.plugin_support import Plugins
from outcome.utils import env


def not_test():
    return not env.is_test()


def not_integration():
    return not env.is_integration()


_environments: Dict[str, Callable[[], bool]] = {
    'only-covered-in-unit-tests': not_test,
    'only-covered-in-integration-tests': not_integration,
}

ignore_opt_name = 'report:exclude_lines'


class EnvironmentExclusionPlugin(CoveragePlugin):
    def configure(self, config: CoverageConfig) -> None:
        """Configure the plugin, called by coveragepy.

        Args:
            config (CoverageConfig): The current coveragepy config object.
        """
        # Go over each env, and add the markers for the current env
        # We don't stop at the first, as `env` may allow for overlapping
        # environments
        for marker, env_test in _environments.items():
            if env_test():
                self.ignore_marker(config, marker)

    def ignore_marker(self, config: CoverageConfig, marker: str) -> None:
        pragma = f'# pragma: {marker}'

        # exclude_lines is an array of patterns that coverage will use to
        # attempt to match lines for exclusion
        exclude_lines = config.get_option(ignore_opt_name)
        exclude_lines.append(pragma)

        config.set_option(ignore_opt_name, exclude_lines)


def coverage_init(reg: Plugins, options: Any) -> None:  # pragma: no cover
    """The plugin entrypoint, called directly by coveragepy.

    It allows us to register the plugin with coveragepy.

    Args:
        reg (Plugins): The object on which to register the plugin.
        options (Any): The configuration options specified in the config file.
    """
    reg.add_configurer(EnvironmentExclusionPlugin())
