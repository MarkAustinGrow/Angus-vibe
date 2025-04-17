#!/bin/bash
# Script to update file paths in the database to be container-friendly

# Make sure we're in the right directory
cd /opt/angus

# Create the uploads directory if it doesn't exist
mkdir -p /app/data/uploads

# Run the script in dry-run mode first to see what changes would be made
echo "Running in dry-run mode to see what changes would be made..."
python update_file_paths.py --dry-run

# Ask for confirmation before making changes
read -p "Do you want to proceed with updating the database? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Run the script with the --execute flag to actually make the changes
    echo "Updating database..."
    python update_file_paths.py --execute
    
    # Restart the Docker containers
    echo "Restarting Docker containers..."
    docker-compose down
    docker-compose up -d
    
    echo "Done! Check the logs to see if the uploads are working now:"
    echo "docker logs angus_angus_1"
else
    echo "Operation cancelled."
fi
