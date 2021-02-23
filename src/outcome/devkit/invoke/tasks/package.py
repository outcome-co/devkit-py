from pathlib import Path

from outcome.devkit.invoke import env
from outcome.read_toml import lib as read_toml
from outcome.utils.config import Config

pyproject_path = Path.cwd() / 'pyproject.toml'

pyproject_file = env.declare('pyproject.toml', str(pyproject_path))
config = Config(pyproject_path)


@env.add
def package_name(e: env.Env) -> str:
    return read_toml.read_from_file(env.r(pyproject_file), 'tool.poetry.name')


@env.add
def package_version(e: env.Env) -> str:
    return read_toml.read_from_file(env.r(pyproject_file), 'tool.poetry.version')
