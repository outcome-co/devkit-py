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


@task(docs, python, coverage)
def all(c: Context):  # noqa: A001, WPS125
    """Clean everything."""
    ...


ns = Collection(coverage, python, docs)
ns.add_task(all, default=True)
