#!/bin/bash
# Run Agent Angus with CrewAI integration
# This shell script runs the CrewAI integration for Agent Angus

echo "Starting Agent Angus with CrewAI integration..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed or not in the PATH."
    echo "Please install Python and try again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv/lib/python*/site-packages/crewai" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies."
        exit 1
    fi
fi

# Check for --simple-tools flag
USE_SIMPLE_TOOLS=""
for arg in "$@"; do
    if [ "$arg" == "--simple-tools" ]; then
        USE_SIMPLE_TOOLS="--simple-tools"
        echo "Using simple tools created with the @tool decorator"
    fi
done

# Run the CrewAI integration
echo "Running Agent Angus with CrewAI integration..."
python run_angus_crew.py "$@" $USE_SIMPLE_TOOLS

# Deactivate virtual environment
deactivate

echo "Done."
