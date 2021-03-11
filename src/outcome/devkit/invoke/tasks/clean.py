import shutil
from pathlib import Path

from invoke import Collection, Context, task


@task
def docs(c: Context):
    """Remove docs."""
    c.run('rm -rf docs')


@task
def python(c: Context):
    """Remove python artifacts."""
    c.run('find . -name "*.pyc" -delete')
    c.run('find . -name "__pycache__" -delete')
    c.run('rm -rf dist .nox')


@task
def coverage(c: Context):
    """Remove coverage files."""
    c.run('rm -rf coverage')


@task
def pacts(c: Context, pact_dir: str = 'pacts'):
    """Remove Pact files.

    When we use Pact, as it is in `merge` writing mode, we need to delete all files in the
    pacts directory to reset the list of known interactions before integration tests.
    """
    if Path(pact_dir).exists():
        shutil.rmtree(pact_dir)


@task(docs, python, coverage, pacts)
def all(c: Context):  # noqa: A001, WPS125
    """Clean everything."""
    ...


ns = Collection(coverage, python, docs, pacts)
ns.add_task(all, default=True)
