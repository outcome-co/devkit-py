from invoke import Collection, Context, task
from outcome.devkit.invoke import docker, env
from outcome.devkit.invoke.tasks import package
from outcome.read_toml import lib as read_toml
from outcome.utils.config import Config

defaults = {
    'DB_IMAGE': 'postgres:latest',
    'DB_NAME': 'postgres',
    'DB_USER': 'postgres',
    'DB_PASSWORD': 'postgres',
    'DB_HOST': '127.0.0.1',
    'DB_PORT': '5432',
}


config = Config(package.pyproject_path, defaults=defaults)


def read_or_default(key: str, default: str) -> str:
    try:
        return read_toml.read_from_file(env.r(package.pyproject_file), key)
    except KeyError:
        return default


database_image = env.from_config('DB_IMAGE', config=config)
database_name = env.from_config('DB_NAME', config=config)
database_user = env.from_config('DB_USER', config=config)
database_password = env.from_config('DB_PASSWORD', config=config)
database_port = env.from_config('DB_PORT', config=config)
database_host = env.from_config('DB_HOST', config=config)


@env.add
def database_container(e: env.Env) -> str:
    name = env.r(package.package_name)
    return f'{name}-db'


@task
def start(c: Context):
    container_name = env.r(database_container)

    # If the container is running, there's nothing to do
    if docker.container_is_running(c, container_name):
        return

    if docker.container_exists(c, container_name):
        docker.start_container(c, container_name)

    container_image = env.r(database_image)
    container_port = int(env.r(database_port))
    container_password = env.r(database_password)

    container_env = {'POSTGRES_PASSWORD': container_password}

    # Container doesn't exist, we need to create it
    docker.create_container(c, container_name, image=container_image, port=container_port, environment=container_env)


@task
def stop(c: Context):
    container_name = env.r(database_container)

    if docker.container_is_running(c, container_name):
        docker.stop_container(c, container_name)


ns = Collection(start, stop)
