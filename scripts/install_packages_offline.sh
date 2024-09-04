#!/bin/bash

# Change to the script's directory
cd "$(dirname "$0")"

# Install packages from wheelhouse using relative paths
pip install --no-index --find-links=../wheelhouse -r ../requirements.txt
