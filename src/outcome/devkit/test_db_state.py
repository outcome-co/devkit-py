"""DB State class and helpers.

```
from outcome.devkit.test_db_state import TestDatabaseState, register_pact_provider_state


class SampleOrganizationsState(TestDatabaseState):

    models = [Organization]

    @classmethod
    def setup(cls, dependencies_records):
        orgs = [Organization.get_or_create(**organization)[0] for organization in sample_organization_records()]
        return {'organizations': orgs}


@register_pact_provider_state('user exists')
class SampleUsersState(TestDatabaseState):

    models = [User]
    depends_on = [SampleOrganizations]

    @classmethod
    def setup(cls, dependencies_records):
        # you can access dependencies_records['organizations'] if needed
        users = [User.get_or_create(**user)[0] for user in sample_user_records()]
        return {'users': users}


# PYTEST TESTS

@pytest.fixture
def sample_users_state():
    with SampleUsersState() as records:
        yield records


def test_something(sample_users_state):
    # do something with sample_users_state['users']
    # do something with sample_users_state['organizations']


# PACT VERIFICATION TESTS

from outcome.devkit.test_db_state import reset_pact_provider_states, known_db_states

def provider_state(name, **params):
    if name in known_db_states.keys():
        known_db_states[name].setup_states()
    else:
        raise ProviderStateMissing(name)


@pytest.fixture
def reset_provider_states():
    reset_pact_provider_states()


# @pytest.mark.usefixtures('test_database_fn')
def test_pact_interaction(pact_verifier, reset_provider_states):
    provider_url = state.config().get('PACT_PROVIDER_URL')
    pact_verifier.verify(provider_url, provider_state, provider_state_header)


```
"""

from typing import Dict, List, Protocol

known_db_states = {}


class DbModel(Protocol):
    # This describe the minimal interface needed by DbModel to work properly.
    def truncate_table(self) -> None:
        """Truncates table."""


class DbRecord(Protocol):
    ...


class TestDatabaseState:
    """Database State class.

    This class allows to manage database states during tests.

    Examples:
        class SampleUsers(TestDatabaseState):

            models = [User]
            depends_on = [SampleOrganizations]  # Optional dependencies

            @classmethod
            def setup(cls):
                users = [User.get_or_create(**user)[0] for user in sample_user_records()]
                return {'users': users}

        You can then use it as a context manager inside your pytest tests:

        with SampleUsers() as records:
            # calls setup() of SampleOrganizations and SampleUsers
            ...
        # calls teardown() of SampleOrganizations and SampleUsers
    """

    models = []
    depends_on = []

    @classmethod
    def setup_states(cls) -> Dict[str, List[DbRecord]]:
        created_records = {}
        for dependency in cls.depends_on:
            created_records.update(dependency.setup_states())
        created_records.update(cls.setup(dependencies_records=created_records))
        return created_records

    @classmethod
    def setup(cls, dependencies_records: Dict[str, List[DbRecord]]) -> Dict[str, List[DbRecord]]:  # pragma: no cover
        ...

    @classmethod
    def teardown(cls) -> None:
        for dependency in cls.depends_on:
            dependency.teardown()
        for m in cls.models:
            m.truncate_table(cascade=True)

    def __enter__(self):
        return self.setup_states()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.teardown()


def _register_db_state(state_name: str, db_state: TestDatabaseState) -> None:
    known_db_states[state_name] = db_state


def register_pact_provider_state(state_name: str):
    """Register pact provider state decorator.

    Examples:
        @register_pact_provider_state('my state')
        class MyState(TestDatabaseState):
            ...

        Then, you can access you state through known_dn_states.
        For instance:

        known_db_states['my state'].setup_states()

    Args:
        state_name (str): The state name.

    Returns:
        Callable: Wrapped function.
    """

    def decorator(cls: TestDatabaseState):
        _register_db_state(state_name, cls)
        return cls

    return decorator


def reset_pact_provider_states() -> None:
    known_models = set()
    for _, state in known_db_states.items():
        known_models.update(set(state.models))
    for model in known_models:
        model.truncate_table(cascade=True)
