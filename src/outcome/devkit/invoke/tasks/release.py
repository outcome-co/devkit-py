from typing import Optional

from invoke import Collection, Context, task
from outcome.devkit.invoke import env
from outcome.devkit.invoke.tasks import clean
from outcome.read_toml.lib import read_from_file


def get_key_from_pyproject(e: env.Env, key: str):
    try:
        pyproject = e.read('pyproject.toml')
        assert pyproject
        return read_from_file(pyproject, key)
    except KeyError:
        return None


@env.add(required=False)
def package_repository_name(e: env.Env):
    return get_key_from_pyproject(e, 'package.repository.name')


@env.add(required=False)
def package_repository_url(e: env.Env):
    return get_key_from_pyproject(e, 'package.repository.url')


@task(clean.all)
def build(c: Context):
    """Build the python package."""
    c.run('poetry build')


@task(build)
def publish(c: Context, repository_name: Optional[str] = None, repository_url: Optional[str] = None):
    """Publish the python package."""

    if any((repository_name, repository_url)) and not all((repository_name, repository_url)):
        raise RuntimeError('You must provide both name and URL when specifying a custom package repository')

    repo_name = repository_name or env.nullable_read(package_repository_name)
    repo_url = repository_url or env.nullable_read(package_repository_url)

    if repo_name and repo_url:
        c.run(f'poetry config repositories.{repo_name} {repo_url}')
        c.run(f'poetry publish -n -r {repo_name}')
    else:
        c.run('poetry publish -n')


ns = Collection(build, publish)
