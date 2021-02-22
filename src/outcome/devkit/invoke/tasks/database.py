from invoke import Collection, Context, task
from outcome.devkit.invoke import docker, env
from outcome.devkit.invoke.tasks import package
from outcome.read_toml import lib as read_toml


def read_or_default(key: str, default: str) -> str:
    try:
        return read_toml.read_from_file(env.r(package.pyproject_file), key)
    except KeyError:
        return default


@env.add
def database_image(e: env.Env) -> str:
    return read_or_default('db.image', 'postgres:latest')


@env.add
def database_name(e: env.Env) -> str:
    return read_or_default('db.name', 'postgres')


@env.add
def database_user(e: env.Env) -> str:
    return read_or_default('db.user', 'postgres')


@env.add
def database_password(e: env.Env) -> str:
    return read_or_default('db.password', 'postgres')


@env.add
def database_host(e: env.Env) -> str:
    return read_or_default('db.host', '127.0.0.1')


@env.add
def database_port(e: env.Env) -> str:
    return read_or_default('db.port', '5432')


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
