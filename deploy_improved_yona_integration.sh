#!/bin/bash
# Deploy the improved Yona integration to a server

# Set default values
SERVER_USER="root"
SERVER_HOST="angs.club"
SERVER_DIR="/opt/Angus-vibe"
BRANCH="working-version"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --user)
            SERVER_USER="$2"
            shift
            shift
            ;;
        --host)
            SERVER_HOST="$2"
            shift
            shift
            ;;
        --dir)
            SERVER_DIR="$2"
            shift
            shift
            ;;
        --branch)
            BRANCH="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Deploying improved Yona integration to $SERVER_USER@$SERVER_HOST:$SERVER_DIR"

# Create a temporary directory for the files
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Copy the files to the temporary directory
echo "Copying files to temporary directory..."
cp src/coral_protocol/langchain/runnable.py $TEMP_DIR/
cp angus_coral_adapter.py $TEMP_DIR/
cp test_improved_yona_communication.py $TEMP_DIR/
cp run_improved_yona_test.sh $TEMP_DIR/
cp run_improved_yona_test.bat $TEMP_DIR/
cp IMPROVED_YONA_INTEGRATION.md $TEMP_DIR/

# Create the deployment script
cat > $TEMP_DIR/deploy.sh << 'EOF'
#!/bin/bash
# Deploy the improved Yona integration

# Set the directory
SERVER_DIR="$1"
cd $SERVER_DIR

# Create the directory structure if it doesn't exist
mkdir -p src/coral_protocol/langchain

# Copy the files
cp runnable.py src/coral_protocol/langchain/
cp angus_coral_adapter.py ./
cp test_improved_yona_communication.py ./
cp run_improved_yona_test.sh ./
cp run_improved_yona_test.bat ./
cp IMPROVED_YONA_INTEGRATION.md ./

# Make the scripts executable
chmod +x run_improved_yona_test.sh

# Restart the Docker containers
docker-compose down
docker-compose build angus_coral
docker-compose up -d

echo "Deployment completed successfully!"
EOF

# Make the deployment script executable
chmod +x $TEMP_DIR/deploy.sh

# Copy the files to the server
echo "Copying files to the server..."
scp -r $TEMP_DIR/* $SERVER_USER@$SERVER_HOST:/tmp/

# Execute the deployment script on the server
echo "Executing deployment script on the server..."
ssh $SERVER_USER@$SERVER_HOST "bash /tmp/deploy.sh $SERVER_DIR"

# Clean up the temporary directory
echo "Cleaning up temporary directory..."
rm -rf $TEMP_DIR

echo "Deployment completed successfully!"
