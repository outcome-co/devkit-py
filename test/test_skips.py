from outcome.devkit import test_helpers
from outcome.utils import env


@test_helpers.skip_for_integration
def test_skip_integration_skip():
    assert not env.is_integration()


@test_helpers.skip_for_unit
def test_skip_unit_test():
    assert not env.is_test()
