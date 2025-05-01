#!/bin/bash
# Script to run the improved Angus-Yona communication test

echo "Starting Improved Angus-Yona communication test..."

# Default values
MESSAGE=""
TIMEOUT=300
VERIFY=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --message)
            MESSAGE="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --no-verify)
            VERIFY=false
            shift
            ;;
        *)
            echo "Unknown option: $1"
            shift
            ;;
    esac
done

# Display parameters
echo "Parameters:"
if [[ -n "$MESSAGE" ]]; then
    echo "Message: $MESSAGE"
fi
echo "Timeout: $TIMEOUT seconds"
echo "Verify delivery: $VERIFY"
echo

# Build the command
CMD="python3 test_improved_yona_communication.py"
if [[ -n "$MESSAGE" ]]; then
    CMD="$CMD --message \"$MESSAGE\""
fi
if [[ "$TIMEOUT" != "300" ]]; then
    CMD="$CMD --timeout $TIMEOUT"
fi
if [[ "$VERIFY" == "false" ]]; then
    CMD="$CMD --no-verify"
fi

echo "Running: $CMD"
echo
eval $CMD

echo
echo "Test completed."
echo "Press Enter to continue..."
read
