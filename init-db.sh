#!/bin/bash
set -e
psql -U postgres -c "CREATE DATABASE custom_db;"