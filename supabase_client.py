"""
Supabase client for interacting with the database and storage.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from supabase import create_client

# Import configuration
from config import SUPABASE_URL, SUPABASE_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    """
    Client for interacting with Supabase to store and retrieve data, and manage storage.
    """
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize the Supabase client.
        
        Args:
            url: Supabase URL (defaults to environment variable)
            key: Supabase key (defaults to environment variable)
        """
        self.url = url or SUPABASE_URL
        self.key = key or SUPABASE_KEY
        self.client = None
        
        # Validate credentials
        if not self.url or not self.key:
            logger.warning("Supabase credentials are missing!")
            raise ValueError("Supabase credentials are required")
        
        # Initialize client
        try:
            self.client = create_client(self.url, self.key)
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.error(f"Error initializing Supabase client: {str(e)}")
            raise
    
    def store_song_data(self, song_data: Dict[str, Any]) -> str:
        """
        Store song data in Supabase.
        
        Args:
            song_data: Dictionary with song data including title, lyrics, audio_url, etc.
            
        Returns:
            The ID of the created song record
        """
        logger.info(f"Storing song data for '{song_data.get('title', 'Unknown')}' in Supabase")
        
        # Check if we need to handle voice_gender separately
        voice_gender = None
        
        # Remove voice_gender from song_data if it exists
        if 'voice_gender' in song_data:
            voice_gender = song_data.pop('voice_gender')
            
            # Add voice_gender to style or tags if needed
            if 'style' in song_data and song_data['style']:
                if f"{voice_gender} voice" not in song_data['style']:
                    song_data['style'] = f"{song_data['style']}, {voice_gender} voice"
            else:
                song_data['style'] = f"{voice_gender} voice"
        
        try:
            response = self.client.table("songs").insert(song_data).execute()
            
            if response.data and len(response.data) > 0:
                song_id = response.data[0].get('id')
                logger.info(f"Song data stored successfully with ID: {song_id}")
                return song_id
            else:
                logger.error("No data returned from Supabase insert operation")
                return None
                
        except Exception as e:
            logger.error(f"Error storing song data: {str(e)}")
            return None
    
    def get_song_by_id(self, song_id: str) -> Dict[str, Any]:
        """
        Retrieve a song by its ID.
        
        Args:
            song_id: The ID of the song to retrieve
            
        Returns:
            Dictionary with song data, or None if not found
        """
        logger.info(f"Retrieving song with ID: {song_id}")
        
        try:
            response = self.client.table("songs").select("*").eq("id", song_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Retrieved song: {response.data[0].get('title')}")
                return response.data[0]
            else:
                logger.warning(f"No song found with ID: {song_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving song: {str(e)}")
            return None
    
    def list_songs(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List songs from the database.
        
        Args:
            limit: Maximum number of songs to return
            offset: Offset for pagination
            
        Returns:
            List of song data dictionaries
        """
        logger.info(f"Listing songs (limit: {limit}, offset: {offset})")
        
        try:
            # Use range method for pagination instead of offset
            # The range method takes start and end parameters
            # where start is inclusive and end is exclusive
            start = offset
            end = offset + limit - 1  # -1 because end is exclusive
            
            response = self.client.table("songs").select("*").order("created_at", desc=True).limit(limit).execute()
            
            if response.data:
                # If we need to handle offset manually
                if offset > 0 and len(response.data) > offset:
                    # Slice the results to implement offset manually
                    result = response.data[offset:offset+limit]
                    logger.info(f"Retrieved {len(result)} songs (manual offset)")
                    return result
                else:
                    logger.info(f"Retrieved {len(response.data)} songs")
                    return response.data
            else:
                logger.warning("No songs found")
                return []
                
        except Exception as e:
            logger.error(f"Error listing songs: {str(e)}")
            return []
    
    # Storage methods
    
    def create_storage_bucket(self, bucket_name: str, is_public: bool = True) -> bool:
        """
        Create a storage bucket if it doesn't exist.
        
        Args:
            bucket_name: Name of the bucket to create
            is_public: Whether the bucket should be public
            
        Returns:
            True if the bucket was created or already exists, False otherwise
        """
        logger.info(f"Creating storage bucket: {bucket_name} (public: {is_public})")
        
        try:
            # Check if bucket exists
            try:
                self.client.storage.get_bucket(bucket_name)
                logger.info(f"Bucket already exists: {bucket_name}")
                return True
            except Exception:
                # Bucket doesn't exist, create it
                pass
                
            # Create the bucket
            self.client.storage.create_bucket(bucket_name)
            
            # Set bucket to public if requested
            if is_public:
                self.client.storage.update_bucket(bucket_name, {"public": True})
                
            logger.info(f"Created storage bucket: {bucket_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating storage bucket: {str(e)}")
            return False
    
    def upload_file_to_storage(self, bucket_name: str, file_path: str, file_name: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to a storage bucket.
        
        Args:
            bucket_name: Name of the bucket to upload to
            file_path: Path to the file to upload
            file_name: Name to use for the file in storage (defaults to basename of file_path)
            
        Returns:
            Public URL of the uploaded file, or None if upload failed
        """
        if not file_name:
            file_name = os.path.basename(file_path)
            
        logger.info(f"Uploading file to storage: {file_path} -> {bucket_name}/{file_name}")
        
        try:
            # Ensure bucket exists
            if not self.create_storage_bucket(bucket_name):
                logger.error(f"Failed to create or access bucket: {bucket_name}")
                return None
                
            # Upload the file
            with open(file_path, 'rb') as f:
                self.client.storage.from_(bucket_name).upload(file_name, f)
                
            # Get the public URL
            public_url = self.client.storage.from_(bucket_name).get_public_url(file_name)
            logger.info(f"Uploaded file to storage: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Error uploading file to storage: {str(e)}")
            return None
    
    def delete_file_from_storage(self, bucket_name: str, file_name: str) -> bool:
        """
        Delete a file from a storage bucket.
        
        Args:
            bucket_name: Name of the bucket containing the file
            file_name: Name of the file to delete
            
        Returns:
            True if the file was deleted, False otherwise
        """
        logger.info(f"Deleting file from storage: {bucket_name}/{file_name}")
        
        try:
            self.client.storage.from_(bucket_name).remove([file_name])
            logger.info(f"Deleted file from storage: {bucket_name}/{file_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file from storage: {str(e)}")
            return False
