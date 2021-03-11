from typing import cast

from invoke import run
from outcome.devkit.invoke import env


@env.add
def git_branch(e: env.Env):
    return cast(str, run('git rev-parse --abbrev-ref HEAD').stdout.strip())


@env.add
def commit_sha1(e: env.Env):
    return cast(str, run('git rev-parse --short=8 HEAD').stdout.strip())
