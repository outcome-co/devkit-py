from invoke import Collection
from outcome.devkit.invoke.tasks import check, clean, release, setup, test
from outcome.utils import env

namespace = Collection(setup, clean, release, check, test)

namespace.configure({'run': {'echo': True, 'pty': not env.is_ci()}})
