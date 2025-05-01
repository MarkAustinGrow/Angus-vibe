#!/bin/bash
# Script to update Angus-Yona integration files on the server

# Display a banner
echo "========================================"
echo "  Updating Angus-Yona Integration Files "
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

# Copy the updated files
echo "Copying updated files..."

# Copy the main adapter file
cp angus_coral_adapter.py "$TARGET_DIR/"
echo "Copied angus_coral_adapter.py"

# Copy the test files
cp test_angus_yona_communication.py "$TARGET_DIR/"
echo "Copied test_angus_yona_communication.py"

cp run_angus_yona_test.sh "$TARGET_DIR/"
chmod +x "$TARGET_DIR/run_angus_yona_test.sh"
echo "Copied run_angus_yona_test.sh"

# Copy the documentation
cp ANGUS_YONA_INTEGRATION.md "$TARGET_DIR/"
echo "Copied ANGUS_YONA_INTEGRATION.md"

echo "All files copied successfully."

# Ask if the user wants to restart the Coral adapter
read -p "Do you want to restart the Coral adapter? (y/n): " RESTART

if [ "$RESTART" = "y" ] || [ "$RESTART" = "Y" ]; then
    echo "Restarting Coral adapter..."
    cd "$TARGET_DIR"
    docker-compose restart coral
    
    # Check if the restart was successful
    if [ $? -eq 0 ]; then
        echo "Coral adapter restarted successfully."
        echo "Displaying logs..."
        docker logs angus_coral_1
    else
        echo "Error: Failed to restart Coral adapter."
        echo "Please check the Docker logs for more information."
    fi
else
    echo "Skipping restart. You can restart the Coral adapter manually with:"
    echo "cd $TARGET_DIR && docker-compose restart coral"
fi

echo "========================================"
echo "  Update completed!                     "
echo "========================================"
