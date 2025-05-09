#!/bin/bash
# Run Angus Coral Agent locally for testing

# Set environment variables
export CORAL_SERVER_URL=https://coral.pushcollective.club/sse

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY environment variable is not set."
    echo "The Coral Protocol integration may not work properly without it."
    echo "Please set it using: export OPENAI_API_KEY=your-api-key"
fi

# Install dependencies if needed
if ! pip list | grep -q "langchain_mcp_adapters"; then
    echo "Installing required dependencies..."
    pip install -r requirements.coral.txt
fi

# Run the agent
echo "Starting Angus Coral Agent..."
python angus_coral_agent.py
