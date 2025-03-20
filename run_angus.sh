#!/bin/bash
# Script to run Agent Angus with common commands

# Function to display help
show_help() {
    echo "Agent Angus - YouTube Publishing and Feedback Collection"
    echo ""
    echo "Usage: ./run_angus.sh [command] [options]"
    echo ""
echo "Commands:"
echo "  setup       Create the YouTube table in Supabase"
echo "  upload      Upload pending songs to YouTube"
echo "  comments    Fetch comments for uploaded videos"
echo "  daemon      Run in daemon mode with scheduled tasks"
echo "  test        Run tests in simulation mode"
echo "  help        Show this help message"
    echo ""
    echo "Options:"
    echo "  --limit N   Limit the number of items to process (default: 10)"
    echo "  --simulate  Run in simulation mode without making actual API calls"
    echo ""
    echo "Examples:"
    echo "  ./run_angus.sh setup"
    echo "  ./run_angus.sh upload --limit 5"
    echo "  ./run_angus.sh comments --limit 10"
    echo "  ./run_angus.sh upload --simulate"
    echo "  ./run_angus.sh test"
}

# Default values
LIMIT=10
SIMULATE=""

# Parse command
COMMAND=$1
shift

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        --limit)
            LIMIT=$2
            shift 2
            ;;
        --simulate)
            SIMULATE="--simulate"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Execute command
case $COMMAND in
    setup)
        echo "Creating YouTube table in Supabase..."
        python angus.py --create-table $SIMULATE
        ;;
    upload)
        echo "Uploading songs to YouTube (limit: $LIMIT)..."
        python angus.py --upload --limit $LIMIT $SIMULATE
        ;;
    comments)
        echo "Fetching comments for uploaded videos (limit: $LIMIT)..."
        python angus.py --fetch-comments --limit $LIMIT $SIMULATE
        ;;
    daemon)
        echo "Starting Agent Angus in daemon mode..."
        python angus.py --daemon
        ;;
    test)
        echo "Running tests in simulation mode..."
        python test_angus.py
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
