#!/bin/bash
# Deployment script for Agent Angus with Coral Protocol integration

echo "Deploying Agent Angus with Coral Protocol integration..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Pull the latest changes from the repository
echo "Pulling latest changes from the repository..."
git pull

# Build the Docker images
echo "Building Docker images..."
docker-compose build angus-coral

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose stop angus-coral

# Start the new containers
echo "Starting new containers..."
docker-compose up -d angus-coral

# Display the logs
echo "Deployment complete. Displaying logs..."
docker-compose logs -f angus-coral
