#!/bin/bash
# Deploy Angus Coral Agent on the server

# Set variables
SERVER="root@angs.club"
APP_DIR="/app"

# Check if SSH key is available
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "SSH key not found. Please make sure you have SSH access to the server."
    exit 1
fi

# Display deployment information
echo "Deploying Angus Coral Agent to $SERVER:$APP_DIR"
echo "This script will:"
echo "1. Copy the necessary files to the server"
echo "2. Update the docker-compose.yml file"
echo "3. Restart the containers"
echo ""

# Confirm deployment
read -p "Do you want to continue? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# Copy files to the server
echo "Copying files to the server..."
scp angus_coral_agent.py $SERVER:$APP_DIR/
scp Dockerfile.coral $SERVER:$APP_DIR/
scp requirements.coral.txt $SERVER:$APP_DIR/
scp docker-compose.yml $SERVER:$APP_DIR/

# Check if files were copied successfully
if [ $? -ne 0 ]; then
    echo "Error copying files to the server."
    exit 1
fi

# Restart containers
echo "Restarting containers..."
ssh $SERVER "cd $APP_DIR && docker-compose down && docker-compose up -d"

# Check if containers were restarted successfully
if [ $? -ne 0 ]; then
    echo "Error restarting containers."
    exit 1
fi

# Display logs
echo "Displaying logs..."
ssh $SERVER "cd $APP_DIR && docker-compose logs angus_coral | tail -n 20"

echo ""
echo "Deployment completed successfully."
echo "You can check the logs using:"
echo "  ssh $SERVER \"cd $APP_DIR && docker-compose logs -f angus_coral\""
