#!/bin/bash

# Change to the script's directory
cd "$(dirname "$0")"

# download whls packages
mkdir -p ../wheelhouse
pip download --dest=../wheelhouse -r ../requirements.txt

