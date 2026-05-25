#!/bin/bash

# Exit on any error
set -e

echo "Starting deployment process..."

# 1. Pull the latest code (uncomment if using git)
# echo "Pulling latest code..."
# git pull origin main

# 2. Rebuild the docker images
echo "Building Docker images..."
docker-compose -f docker-compose.yml build --no-cache

# 3. Apply DB migrations / initial setup (handled by app.py automatically on startup, but can be forced here)
echo "Ensuring database is up before proceeding..."
docker-compose -f docker-compose.yml up -d db redis
# Give DB a few seconds to initialize
sleep 15

# 4. Start/Restart services (Rolling restart approach)
echo "Starting web and nginx services..."
docker-compose -f docker-compose.yml up -d --no-deps --build web
docker-compose -f docker-compose.yml up -d nginx

echo "Cleaning up dangling images..."
docker image prune -f

echo "Deployment successful!"
docker-compose ps
