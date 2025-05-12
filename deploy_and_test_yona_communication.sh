#!/bin/bash
# Deploy and test Yona communication on the Linode server

# Set default values
SERVER_USER="root"
SERVER_HOST="angs.club"
SERVER_DIR="/opt/Angus-vibe"

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
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Deploying and testing Yona communication on $SERVER_USER@$SERVER_HOST:$SERVER_DIR"

# Create the deployment script
cat > deploy_and_test.sh << 'EOF'
#!/bin/bash
# Deploy and test Yona communication

# Set the directory
SERVER_DIR="$1"
cd $SERVER_DIR

# Pull the latest changes from GitHub
echo "Pulling latest changes from GitHub..."
git pull origin working-version

# Make the test scripts executable
echo "Making test scripts executable..."
chmod +x run_direct_yona_test.sh

# Install required packages
echo "Installing required packages..."
pip install langchain>=0.1.0 langchain_mcp_adapters==0.0.11 langchain-openai>=0.0.2 aiohttp>=3.8.5

# Run the test script
echo "Running the test script..."
./run_direct_yona_test.sh

echo "Deployment and testing completed!"
EOF

# Make the deployment script executable
chmod +x deploy_and_test.sh

# Copy the deployment script to the server
echo "Copying deployment script to the server..."
scp deploy_and_test.sh $SERVER_USER@$SERVER_HOST:/tmp/

# Execute the deployment script on the server
echo "Executing deployment script on the server..."
ssh $SERVER_USER@$SERVER_HOST "bash /tmp/deploy_and_test.sh $SERVER_DIR"

# Clean up
echo "Cleaning up..."
rm deploy_and_test.sh

echo "Deployment and testing completed!"
