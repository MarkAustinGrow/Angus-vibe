#!/usr/bin/env python3
"""
Script to update file paths in the database to be container-friendly.

This script updates the video_url field in the songs table to use paths
that are accessible from within the Docker container.
"""
import os
import sys
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import custom modules
try:
    from supabase_client import SupabaseClient
except ImportError:
    logger.error("Could not import SupabaseClient. Make sure you're running this script from the Angus directory.")
    sys.exit(1)

def update_file_paths(dry_run: bool = True) -> None:
    """
    Update file paths in the database to be container-friendly.
    
    Args:
        dry_run: If True, only print the changes that would be made without actually making them.
    """
    logger.info(f"Updating file paths (dry_run: {dry_run})")
    
    # Initialize Supabase client
    try:
        supabase = SupabaseClient()
        logger.info("Supabase client initialized")
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {str(e)}")
        return
    
    # Get songs with file:// URLs
    try:
        response = supabase.client.table("songs").select("id, title, video_url").like("video_url", "file://%").execute()
        songs = response.data
        logger.info(f"Found {len(songs)} songs with file:// URLs")
    except Exception as e:
        logger.error(f"Error querying songs: {str(e)}")
        return
    
    # Process each song
    for song in songs:
        song_id = song.get('id')
        title = song.get('title')
        video_url = song.get('video_url')
        
        logger.info(f"Processing song: {title}")
        logger.info(f"  Current URL: {video_url}")
        
        # Skip if the URL is not a file:// URL
        if not video_url or not video_url.startswith('file://'):
            logger.info(f"  Skipping: Not a file:// URL")
            continue
        
        # Extract the file path from the URL
        file_path = video_url[7:]  # Remove 'file://' prefix
        
        # Get the filename
        filename = os.path.basename(file_path.replace('\\', '/'))
        
        # Create a container-friendly path
        container_path = f"file:///app/data/uploads/{filename}"
        
        logger.info(f"  New URL: {container_path}")
        
        # Update the database
        if not dry_run:
            try:
                supabase.client.table("songs").update({"video_url": container_path}).eq("id", song_id).execute()
                logger.info(f"  Updated database record")
            except Exception as e:
                logger.error(f"  Error updating database record: {str(e)}")
        else:
            logger.info(f"  Would update database record (dry run)")
        
        # Check if the file exists in the container
        container_file_path = f"/app/data/uploads/{filename}"
        if os.path.exists(container_file_path):
            logger.info(f"  File exists at: {container_file_path}")
        else:
            logger.warning(f"  File does not exist at: {container_file_path}")
            
            # Check if the file exists in the original location
            if os.path.exists(file_path):
                logger.info(f"  File exists at original location: {file_path}")
                
                # Copy the file to the container location
                if not dry_run:
                    try:
                        os.makedirs(os.path.dirname(container_file_path), exist_ok=True)
                        import shutil
                        shutil.copy2(file_path, container_file_path)
                        logger.info(f"  Copied file to: {container_file_path}")
                    except Exception as e:
                        logger.error(f"  Error copying file: {str(e)}")
                else:
                    logger.info(f"  Would copy file to: {container_file_path} (dry run)")
            else:
                logger.error(f"  File does not exist at original location: {file_path}")
                logger.error(f"  You will need to manually copy the file to: {container_file_path}")

def main():
    """
    Main entry point for the script.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Update file paths in the database to be container-friendly.')
    parser.add_argument('--dry-run', action='store_true', help='Only print the changes that would be made without actually making them.')
    parser.add_argument('--execute', action='store_true', help='Actually make the changes to the database.')
    
    args = parser.parse_args()
    
    # Default to dry run unless --execute is specified
    dry_run = not args.execute
    
    update_file_paths(dry_run=dry_run)

if __name__ == "__main__":
    main()
