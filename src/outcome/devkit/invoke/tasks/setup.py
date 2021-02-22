import platform
from typing import Optional

from invoke import Collection, Context, run, task
from outcome.devkit.invoke import env
from outcome.devkit.invoke.tasks import package
from outcome.read_toml import lib as read_toml
from outcome.utils.env import is_ci


@env.add
def build_system_requirements(e: env.Env) -> Optional[str]:
    return read_toml.read_from_file(env.r(package.pyproject_file), 'build-system.requires')


@env.add
def poetry_ld_flags_from_brew(e: env.Env) -> str:
    # Retrieve the path to the ssl library, used for compiling some python C extensions
    path: str = run('brew --prefix openssl', echo=False, hide=True).stdout
    return f'{path.strip()}/lib'


@task
def build_system(c: Context):
    """Install essential build system components."""
    requirements = env.r(build_system_requirements)
    c.run(f'pip install "{requirements}"')

    if not is_ci():
        # Setup pre-commit
        c.run('pre-commit install -t pre-commit')
        c.run('pre-commit install -t pre-push')
        c.run('pre-commit install -t commit-msg')


@task(build_system)
def ci(c: Context):
    """Install the dependencies for CI environments."""
    c.run('poetry install --no-interaction --no-ansi --remove-untracked')


@task(build_system)
def dev(c: Context):
    """Install the dependencies for dev environments."""
    install_env = {}

    if platform.system() == 'Darwin':
        install_env.update({'LDFLAGS': env.r(poetry_ld_flags_from_brew)})

    c.run('poetry install --remove-untracked', env=install_env)


@task(build_system)
def production(c: Context):
    """Install the dependencies for production environments."""
    c.run('poetry config virtualenvs.create false')
    c.run('poetry install --no-dev --no-interaction --no-ansi  --remove-untracked')


@task
def auto(c: Context):
    """Install either dev or CI dependencies, based on the environment."""
    if is_ci():
        ci(c)
    else:
        dev(c)


namespace = Collection(build_system, ci, dev, production, auto)
