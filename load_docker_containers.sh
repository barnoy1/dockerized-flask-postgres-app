#!/bin/bash

# Variables
DB_CONTAINER_NAME="db"
WEB_CONTAINER_NAME="web"
DB_IMAGE="postgres:13-alpine"
WEB_IMAGE="web_image:latest"
DB_USER="postgres"
DB_PASSWORD="password"
DB_NAME="custom_db"
DB_PORT="5432"
WEB_PORT="5000"
DEBUG_PORT="5678"

# Create the Docker network
docker network create mynetwork || true

# Run the PostgreSQL container
docker run -d \
  --name $DB_CONTAINER_NAME \
  --network mynetwork \
  -e POSTGRES_USER=$DB_USER \
  -e POSTGRES_PASSWORD=$DB_PASSWORD \
  -e POSTGRES_DB=$DB_NAME \
  -v postgres_data:/var/lib/postgresql/data \
  -v $(pwd)/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh \
  --health-cmd="pg_isready -U $DB_USER -d $DB_NAME" \
  --health-interval=10s \
  --health-retries=5 \
  --health-start-period=30s \
  $DB_IMAGE

# Build the web application image
docker build -t $WEB_IMAGE -f Dockerfile.debug .

# Run the web application container
docker run -d \
  --name $WEB_CONTAINER_NAME \
  --network mynetwork \
  -e DATABASE_URL="postgres://$DB_USER:$DB_PASSWORD@$DB_CONTAINER_NAME:$DB_PORT/$DB_NAME" \
  -p $WEB_PORT:5000 \
  -p $DEBUG_PORT:5678 \
  $WEB_IMAGE

# Create Docker volume
docker volume create postgres_data || true

echo "Containers and network have been set up."
