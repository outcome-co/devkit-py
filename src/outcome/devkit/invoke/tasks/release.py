from invoke import Collection, Context, task
from outcome.devkit.invoke.tasks import clean


@task(clean.all)
def build(c: Context):
    """Build the python package."""
    c.run('poetry build')


@task(build)
def publish(c: Context):
    """Publish the python package."""
    c.run('poetry publish')


ns = Collection(build, publish)
