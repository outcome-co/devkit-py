from mock import Mock
from outcome.devkit.test_db_state import (
    TestDatabaseState,
    known_db_states,
    register_pact_provider_state,
    reset_pact_provider_states,
)


def test_register_state():
    @register_pact_provider_state('my state')
    class MyState(TestDatabaseState):
        ...

    assert known_db_states['my state'] == MyState


def test_reset_pact_provider_states():
    model1 = Mock()
    model2 = Mock()
    model3 = Mock()
    model4 = Mock()

    @register_pact_provider_state('my state')
    class MyState(TestDatabaseState):
        models = [model1, model2]

    @register_pact_provider_state('other state')
    class MyOtherState(TestDatabaseState):
        models = [model3]

    class MyUnknownState(TestDatabaseState):
        models = [model4]

    reset_pact_provider_states()
    model1.truncate_table.assert_called_once()
    model2.truncate_table.assert_called_once()
    model3.truncate_table.assert_called_once()
    model4.truncate_table.assert_not_called()


def test_db_state():
    model1 = Mock()
    model2 = Mock()
    all_models = [model1, model2]
    mock_setup1 = Mock()

    class TestStateModel(TestDatabaseState):
        models = all_models

        @classmethod
        def setup(cls, dependencies_records):
            mock_setup1()
            return {'model1': [mock_setup1.return_value]}

    with TestStateModel() as records:
        mock_setup1.assert_called_once()
        assert records['model1'] == [mock_setup1.return_value]
        model1.truncate_table.assert_not_called()
        model2.truncate_table.assert_not_called()
    model1.truncate_table.assert_called_once()
    model2.truncate_table.assert_called_once()


def test_db_state_depends():
    model1 = Mock()
    model2 = Mock()
    all_models = [model1, model2]
    mock_setup1 = Mock()
    mock_setup2 = Mock()

    class TestStateModel(TestDatabaseState):
        models = all_models

        @classmethod
        def setup(cls, dependencies_records):
            mock_setup1()
            return {'model1': [mock_setup1.return_value]}

    class TestStateModelDepends(TestDatabaseState):
        models = all_models
        depends_on = [TestStateModel]

        @classmethod
        def setup(cls, dependencies_records):
            assert dependencies_records['model1'] == [mock_setup1.return_value]
            mock_setup2()
            return {'model2': [mock_setup2.return_value]}

    with TestStateModelDepends() as records:
        mock_setup1.assert_called_once()
        mock_setup2.assert_called_once()
        assert records['model1'] == [mock_setup1.return_value]
        assert records['model2'] == [mock_setup2.return_value]
        model1.truncate_table.assert_not_called()
        model2.truncate_table.assert_not_called()
    model1.truncate_table.assert_called()
    model2.truncate_table.assert_called()
