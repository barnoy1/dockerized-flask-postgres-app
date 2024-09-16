#!/bin/bash

set -e

# Use the POSTGRES_DB environment variable to get the database name
DB_NAME=${POSTGRES_DB:-custom_db}

# Wait for PostgreSQL to be ready
until pg_isready -U postgres; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Check if the database already exists
if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
  echo "Database $DB_NAME already exists. Skipping creation."
else
  echo "Creating database $DB_NAME..."
  psql -U postgres -c "CREATE DATABASE $DB_NAME;"
fi

echo "Database initialization completed."