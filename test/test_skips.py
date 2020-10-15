from unittest.mock import Mock, patch

import pytest
from outcome.devkit import test_helpers
from outcome.utils import env


@pytest.mark.parametrize('is_e2e', [True, False])
@patch('outcome.devkit.test_helpers.env.is_e2e')
def test_skip_e2e_skip(is_e2e_mock: Mock, is_e2e):

    is_e2e_mock.return_value = is_e2e

    @test_helpers.skip_for_e2e
    def my_test():
        return True

    assert my_test.pytestmark[0].name == 'skipif'
    assert my_test.pytestmark[0].args[0] is is_e2e


@test_helpers.skip_for_integration
def test_skip_integration_skip():
    assert not env.is_integration()


@test_helpers.skip_for_unit
def test_skip_unit_test():
    assert not env.is_test()
