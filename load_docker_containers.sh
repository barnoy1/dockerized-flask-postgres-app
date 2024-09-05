#!/bin/bash

# Define environment variables
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="password"
POSTGRES_DB="mydatabase"
DATABASE_URL="postgresql://postgres:password@db:5432/mydatabase"

# Create a Docker network
docker network create mynetwork

# Run the PostgreSQL container
docker run -d \
  --name db \
  --network mynetwork \
  -e POSTGRES_USER=$POSTGRES_USER \
  -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
  -e POSTGRES_DB=$POSTGRES_DB \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:13-alpine

# Build the web service Docker image
docker build -f Dockerfile.debug -t web-image .

# Run the web service container
docker run -d \
  --name web \
  --network mynetwork \
  -e DATABASE_URL=$DATABASE_URL \
  -p 5000:5000 \
  -p 5678:5678 \
  web-image

# Create and mount the volume
docker volume create postgres_data
