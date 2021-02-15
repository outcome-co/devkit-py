#! /bin/bash

set -e

# Install dependencies
pip install --upgrade "outcome-devkit>=5.0.0"
npm i -g pyright

# Create development environment
PYTHONPATH=src inv setup.auto
