from invoke import Collection, Context, task
from outcome.devkit.invoke.tasks import clean
from outcome.utils.env import is_ci

_default_target = './test'


def run_tests(  # noqa: WPS211
    c: Context, app_env: str, coverage: str, target: str, capture: bool = True, update_snapshots: bool = False,
):
    options = ['-vvv', '--ff', '--maxfail=1']

    if capture:
        options.append('-s')

    if update_snapshots:
        options.append('--snapshot-update')

    options_string = ' '.join(options)
    env = {'APP_ENV': app_env, 'PYTHONPATH': 'src'}

    # The in_stream is to play nice with pytest's capturing
    c.run(f'poetry run coverage run --context={coverage} -m pytest {options_string} {target}', env=env, in_stream=not capture)

    if is_ci():
        c.run('poetry run coverage report -m')
    else:
        # Run a first coverage, to the console but don't fail based on %
        c.run('poetry run coverage report -m --fail-under 0')
        # Run a second coverage to output html, and fail according to %
        c.run('poetry run coverage html --show-contexts')


@task(clean.all)
def unit(c: Context, target: str = _default_target, capture: bool = True, update_snapshots: bool = False):
    """Run unit tests."""
    run_tests(c, 'test', 'unit', target, capture, update_snapshots)


@task(clean.all)
def integration(c: Context, target: str = _default_target, capture: bool = True, update_snapshots: bool = False):
    """Run integration tests."""
    run_tests(c, 'integration', 'integration', target, capture, update_snapshots)


@task(clean.all, unit, integration)
def all(c: Context):  # noqa: A001, WPS125
    """Run unit and integration tests."""
    ...


ns = Collection(unit, integration)
ns.add_task(all, default=True)
