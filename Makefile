.PHONY: build publish clean 

.PHONY: install-build-system dev-setup production-setup

# VARIABLES

PKG_NAME = $(shell docker run --rm -v $$(pwd):/work/ outcomeco/action-read-toml:latest --path /work/pyproject.toml --key tool.poetry.name)
PKG_VERSION = $(shell docker run --rm -v $$(pwd):/work/ outcomeco/action-read-toml:latest --path /work/pyproject.toml --key tool.poetry.version) 

# The BUILD_SYSTEM_REQUIREMENTS variable is used *inside* a docker container 
# during the build process when 'make install-build-system' is run, which would normally require
# to have a docker in a docker. Since this is a bit complex for such a 
# small build, it's easier to just pass the BUILD_SYSTEM_REQUIREMENTS to the docker build process
# via a --build-arg and then pass the BUILD_SYSTEM_REQUIREMENTS as an environment variable
# to the Makefile inside the build process.
#
# Here, we check if the BUILD_SYSTEM_REQUIREMENTS is already available, i.e. it's provided 
# as an environment variable, if not we can assume we're not in the build process and
# we have access to docker

ifndef BUILD_SYSTEM_REQUIREMENTS
# If the BUILD_SYSTEM_REQUIREMENTS variable is not defined, fetch it using the docker
BUILD_SYSTEM_REQUIREMENTS = $(shell docker run --rm -v $$(pwd):/work/ outcomeco/action-read-toml:latest --path /work/pyproject.toml --key build-system.requires)
endif

install-build-system:
	# We pass the variable through echo/xargs to avoid whitespacing issues 
	echo "$(BUILD_SYSTEM_REQUIREMENTS)" | xargs pip install

dev-setup: install-build-system
	./pre-commit.sh
	poetry install

production-setup: install-build-system
	poetry config virtualenvs.create false
	poetry install --no-dev --no-interaction --no-ansi

clean:
	rm -rf dist
	rm -rf **/*.egg-info
	rm -rf .coverage

build: clean
	poetry build

publish: build
	poetry publish
