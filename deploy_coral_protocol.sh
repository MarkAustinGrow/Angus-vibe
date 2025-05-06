#!/bin/bash
# Deploy Coral Protocol Integration to Linode Server
# This script fetches the latest changes from the coral_protocol_langchain branch,
# rebuilds the Docker containers, and restarts the services.

set -e  # Exit on error

echo "Deploying Coral Protocol Integration to Linode Server..."

# Step 1: Fetch the latest changes
echo "Fetching latest changes from remote repository..."
git fetch origin

# Step 2: Checkout the coral_protocol_langchain branch
echo "Checking out coral_protocol_langchain branch..."
git checkout coral_protocol_langchain

# Step 3: Pull the latest changes
echo "Pulling latest changes..."
git pull origin coral_protocol_langchain

# Step 4: Stop the current Docker containers
echo "Stopping current Docker containers..."
docker-compose down

# Step 5: Rebuild the Docker containers
echo "Rebuilding Docker containers..."
docker-compose build

# Step 6: Start the containers
echo "Starting Docker containers..."
docker-compose up -d

# Step 7: Check the status of the containers
echo "Checking container status..."
docker ps

echo "Deployment completed successfully!"
