"""
YouTube audio extractor for Sonoteller analysis.

This module provides functionality to extract audio from YouTube videos
for analysis with the Sonoteller API.
"""
import os
import tempfile
import logging
import uuid
from typing import Optional
from pytube import YouTube
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeAudioExtractor:
    """
    Extracts audio from YouTube videos for analysis.
    """
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize the YouTube audio extractor.
        
        Args:
            temp_dir: Optional directory to store temporary files.
                     If not provided, system temp directory will be used.
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"Using temporary directory: {self.temp_dir}")
    
    def extract_audio(self, youtube_url: str) -> str:
        """
        Extract audio from a YouTube video and save as MP3.
        
        Args:
            youtube_url: URL of the YouTube video
            
        Returns:
            Path to the extracted MP3 file
        """
        logger.info(f"Extracting audio from YouTube URL: {youtube_url}")
        
        # Extract video ID for a more meaningful filename
        video_id = self._extract_video_id(youtube_url)
        filename = f"youtube_{video_id or uuid.uuid4()}.mp3"
        output_path = os.path.join(self.temp_dir, filename)
        
        try:
            # Create YouTube object
            yt = YouTube(youtube_url)
            
            # Get the audio stream with highest quality
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            if not audio_stream:
                raise ValueError(f"No audio stream found for {youtube_url}")
            
            # Download the file (this will be in mp4 format)
            logger.info(f"Downloading audio stream: {audio_stream.abr}kbps")
            temp_file = audio_stream.download(output_path=self.temp_dir)
            
            # Rename to mp3
            os.rename(temp_file, output_path)
            logger.info(f"Audio extracted to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error extracting audio from YouTube: {str(e)}")
            raise
    
    def get_file_url(self, file_path: str) -> str:
        """
        Convert a local file path to a file:// URL.
        
        Args:
            file_path: Path to the local file
            
        Returns:
            file:// URL for the local file
        """
        # Normalize path separators for URL
        normalized_path = file_path.replace('\\', '/')
        
        # Ensure path starts with a slash for file:// URLs
        if not normalized_path.startswith('/'):
            normalized_path = '/' + normalized_path
            
        return f"file://{normalized_path}"
    
    def _extract_video_id(self, youtube_url: str) -> Optional[str]:
        """
        Extract the video ID from a YouTube URL.
        
        Args:
            youtube_url: URL of the YouTube video
            
        Returns:
            Video ID or None if not found
        """
        parsed_url = urlparse(youtube_url)
        
        # Handle youtube.com URLs
        if parsed_url.netloc in ('youtube.com', 'www.youtube.com'):
            query_params = parse_qs(parsed_url.query)
            return query_params.get('v', [None])[0]
            
        # Handle youtu.be URLs
        elif parsed_url.netloc == 'youtu.be':
            return parsed_url.path.lstrip('/')
            
        return None
    
    def cleanup(self, file_path: str) -> None:
        """
        Clean up a temporary file.
        
        Args:
            file_path: Path to the file to clean up
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up file {file_path}: {str(e)}")
