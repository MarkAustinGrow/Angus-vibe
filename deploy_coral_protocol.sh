#!/bin/bash
# Deployment script for the Coral Protocol integration

# Display a banner
echo "========================================"
echo "  Deploying Coral Protocol Integration  "
echo "========================================"

# Navigate to the Angus directory
cd /opt/angus

# Pull the latest changes from the Coral_protocol branch
echo "Pulling latest changes from the Coral_protocol branch..."
git fetch
git checkout Coral_protocol

# Check if the checkout was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to checkout the Coral_protocol branch."
    echo "Please make sure the branch exists and you have the necessary permissions."
    exit 1
fi

# Rebuild the Docker images
echo "Rebuilding Docker images..."
docker-compose build

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to build Docker images."
    echo "Please check the build logs for more information."
    exit 1
fi

# Restart the Docker containers
echo "Restarting Docker containers..."
docker-compose down
docker-compose up -d

# Check if the containers are running
echo "Checking container status..."
docker ps

# Display the logs of the Coral Protocol adapter
echo "Displaying logs of the Coral Protocol adapter..."
docker logs angus_coral_1

echo "========================================"
echo "  Deployment completed successfully!    "
echo "========================================"
echo "The Coral Protocol integration is now running."
echo "You can check the logs with: docker logs angus_coral_1"
