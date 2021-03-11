import json
import os
from pathlib import Path

from invoke import Collection, Context, task
from outcome.devkit.invoke import docker, env
from outcome.devkit.invoke.tasks import git, package

pact_broker_url = env.declare('PACT_BROKER_URL', 'https://pact.svc.outcome.co')
pact_providers_dir = env.declare('PACT_PROVIDERS_DIR', 'pacts')
pact_foundation_cli_image = env.declare('PACT_FOUNDATION_CLI_IMAGE', 'pactfoundation/pact-cli:latest')

pact_broker_username = env.from_os('PACT_BROKER_USERNAME')
pact_broker_password = env.from_os('PACT_BROKER_PASSWORD')
pact_github_token = env.from_os('PACT_GITHUB_TOKEN')


def pact_foundation_vars():
    return {
        'PACT_BROKER_BASE_URL': env.r(pact_broker_url),
        'PACT_BROKER_USERNAME': env.r(pact_broker_username),
        'PACT_BROKER_PASSWORD': env.r(pact_broker_password),
    }


event_pact_changed = {
    'event_type': 'pact_content_changed',
    'client_payload': {'pact_url': '${pactbroker.pactUrl}', 'consumer': '${pactbroker.consumerName}'},
}


@task
def create_webhooks_from_pacts(c: Context):  # noqa: A001, WPS125
    """Create webhooks in Pact Broker from local pact files."""
    for file in Path(env.r(pact_providers_dir)).glob('*'):
        with open(file, 'r') as handler:
            json_file = json.load(handler)
        provider_name = json_file['provider']['name']
        create_webhooks_for_provider(c, provider_name)


@task
def create_webhooks_for_provider(c: Context, provider_name: str):  # noqa: A001, WPS125
    """Create webhook in Pact Broker for a provider."""
    var_pact_github_token = env.r(pact_github_token)
    var_event_pact_changed = json.dumps(event_pact_changed)

    docker.create_container(
        c,
        f'webhook-{provider_name}',
        image=env.r(pact_foundation_cli_image),
        environment=pact_foundation_vars(),
        command='broker',
        command_args=[
            ('create-webhook', f'https://api.github.com/repos/outcome-co/{provider_name}/dispatches'),
            ('--contract-content-changed',),
            ('--provider', provider_name),
            ('-X', 'POST'),
            ('-H', 'User-Agent: PactBroker'),
            ('-H', 'Host: api.github.com'),
            ('-H', 'Content-Type: application/json'),
            ('-H', 'Accept: application/vnd.github.v3+json'),
            ('-H', f'Authorization: token ${var_pact_github_token}'),
            ('-d', f"'{var_event_pact_changed}'"),
        ],
    )


@task
def publish_as_consumer(c: Context):  # noqa: A001, WPS125
    """Publish local Pact files to Pact Broker."""
    var_package_version = env.r(package.package_version)
    var_pact_providers_dir = env.r(pact_providers_dir)
    var_cwd = os.getcwd()

    docker.create_container(
        c,
        f'publish-{var_package_version}',
        image=env.r(pact_foundation_cli_image),
        environment=pact_foundation_vars(),
        volumes=[(var_cwd, '/app')],
        workdir='/app',
        command='publish',
        command_args=[
            (f'/app/{var_pact_providers_dir}',),
            ('--consumer-app-version', env.r(git.commit_sha1)),
            ('--tag', env.r(package.package_version)),
            ('--tag', env.r(git.git_branch)),
        ],
    )


@task
def create_version_tags(c: Context):  # noqa: A001, WPS125
    """Tag Pact with the version of the package."""
    var_package_version = env.r(package.package_version)
    var_cwd = os.getcwd()

    docker.create_container(
        c,
        f'tags-{var_package_version}',
        image=env.r(pact_foundation_cli_image),
        environment=pact_foundation_vars(),
        volumes=[(var_cwd, '/app')],
        workdir='/app',
        command='broker',
        command_args=[
            ('create-version-tag',),
            ('--pacticipant', env.r(package.package_name)),
            ('--version', env.r(git.commit_sha1)),
            ('--tag', env.r(package.package_version)),
            ('--tag', env.r(git.git_branch)),
        ],
    )


ns = Collection(create_webhooks_from_pacts, create_webhooks_for_provider, publish_as_consumer, create_version_tags)
