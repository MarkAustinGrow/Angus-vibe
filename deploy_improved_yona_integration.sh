#!/bin/bash
# Deployment script for the improved Angus-Yona integration

# Display a banner
echo "========================================"
echo "  Deploying Improved Yona Integration   "
echo "========================================"

# Check if the target directory is provided
if [ -z "$1" ]; then
    TARGET_DIR="/opt/angus"
    echo "No target directory provided, using default: $TARGET_DIR"
else
    TARGET_DIR="$1"
    echo "Target directory: $TARGET_DIR"
fi

# Check if the target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Target directory does not exist: $TARGET_DIR"
    exit 1
fi

# Copy the improved files
echo "Copying improved files..."

# Copy the main adapter file
cp angus_coral_adapter_improved.py "$TARGET_DIR/"
echo "Copied angus_coral_adapter_improved.py"

# Copy the test files
cp test_improved_yona_communication.py "$TARGET_DIR/"
echo "Copied test_improved_yona_communication.py"

cp run_improved_yona_test.sh "$TARGET_DIR/"
chmod +x "$TARGET_DIR/run_improved_yona_test.sh"
echo "Copied run_improved_yona_test.sh"

# Copy the documentation
cp IMPROVED_YONA_INTEGRATION.md "$TARGET_DIR/"
echo "Copied IMPROVED_YONA_INTEGRATION.md"

echo "All improved files copied successfully."

# Ask if the user wants to restart the Coral adapter
read -p "Do you want to restart the Coral adapter with the improved version? (y/n): " RESTART

if [ "$RESTART" = "y" ] || [ "$RESTART" = "Y" ]; then
    echo "Updating the Docker configuration to use the improved adapter..."
    
    # Create a backup of the original Dockerfile
    cp "$TARGET_DIR/Dockerfile" "$TARGET_DIR/Dockerfile.backup"
    echo "Created backup of original Dockerfile: Dockerfile.backup"
    
    # Update the Dockerfile to use the improved adapter
    sed -i 's/CMD \["python", "angus_coral_adapter.py"\]/CMD ["python", "angus_coral_adapter_improved.py"]/' "$TARGET_DIR/Dockerfile"
    echo "Updated Dockerfile to use the improved adapter"
    
    # Rebuild and restart the Docker containers
    echo "Rebuilding Docker images..."
    cd "$TARGET_DIR"
    docker-compose build
    
    # Check if the build was successful
    if [ $? -eq 0 ]; then
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
        echo "The improved Angus-Yona integration is now running."
        echo "You can check the logs with: docker logs angus_coral_1"
    else
        echo "Error: Failed to build Docker images."
        echo "Restoring original Dockerfile..."
        mv "$TARGET_DIR/Dockerfile.backup" "$TARGET_DIR/Dockerfile"
        echo "Please check the build logs for more information."
        exit 1
    fi
else
    echo "Skipping restart. You can manually update the Docker configuration and restart the containers with:"
    echo "1. Edit $TARGET_DIR/Dockerfile to use angus_coral_adapter_improved.py"
    echo "2. cd $TARGET_DIR && docker-compose build"
    echo "3. docker-compose down && docker-compose up -d"
fi

echo "========================================"
echo "  Deployment script completed!          "
echo "========================================"
