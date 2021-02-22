from outcome.devkit.invoke import env
from outcome.read_toml import lib as read_toml

pyproject_file = env.declare('pyproject.toml', './pyproject.toml')


@env.add
def package_name(e: env.Env) -> str:
    return read_toml.read_from_file(env.r(pyproject_file), 'tool.poetry.name')


@env.add
def package_version(e: env.Env) -> str:
    return read_toml.read_from_file(env.r(pyproject_file), 'tool.poetry.version')
