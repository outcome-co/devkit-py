from pathlib import Path

from invoke import Collection, Context, task
from outcome.devkit.invoke import env
from outcome.devkit.invoke.tasks import clean
from outcome.utils.env import is_ci


@env.add
def code_dirs(e: env.Env) -> str:
    return ' '.join(d for d in ('./src', './bin', './test') if Path(d).is_dir())


@task(clean.all)
def types(c: Context):
    """Run type-checking."""
    c.run(f'poetry run pyright {env.r(code_dirs)}')


@task(clean.all)
def format(c: Context):  # noqa: A001, WPS125
    """Run formatter."""
    if is_ci():
        c.run(f'poetry run black --check {env.r(code_dirs)}')
    else:
        c.run(f'poetry run black {env.r(code_dirs)}')


@task(clean.all)
def isort(c: Context):
    """Run isort."""
    if is_ci():
        c.run(f'poetry run isort -rc {env.r(code_dirs)} --check-only')
    else:
        c.run(f'poetry run isort -rc {env.r(code_dirs)}')


@task(clean.all)
def lint(c: Context):
    """Run flake8."""
    c.run(f'poetry run flake8 {env.r(code_dirs)}')


@task(clean.all, types, isort, format, lint)
def all(c: Context):  # noqa: A001, WPS125
    """Run all checks."""
    ...


ns = Collection(all, lint, isort, format, types)
