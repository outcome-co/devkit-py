#! /bin/bash

set -e

# Install dependencies
pip install --upgrade outcome-devkit magicinvoke outcome-read-toml==2.1.0 outcome-utils==4.25.0
npm i -g pyright

# Create development environment
PYTHONPATH=src inv setup.auto
