#!/bin/bash
# Run Angus Coral Agent test script

# Set environment variables
export CORAL_SERVER_URL=https://coral.pushcollective.club/sse

# Check if requests library is installed
if ! pip list | grep -q "requests"; then
    echo "Installing required dependencies..."
    pip install requests
fi

# Run the test script
echo "Running Angus Coral Agent test script..."
python test_angus_coral.py

echo ""
echo "If the test shows that the Angus agent is not registered,"
echo "make sure the Angus Coral Agent is running using run_angus_coral.sh"
