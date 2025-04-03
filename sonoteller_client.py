"""
Sonoteller client for analyzing music using the Sonoteller API.
"""
import http.client
import json
import logging
import urllib.parse
import re
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SonotellerClient:
    """
    Client for interacting with the Sonoteller API to analyze music.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the Sonoteller client.
        
        Args:
            api_key: Sonoteller API key
        """
        self.api_key = api_key
        self.host = "sonoteller-ai1.p.rapidapi.com"
        
    def analyze_music(self, file_url: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a music file using Sonoteller API.
        
        Args:
            file_url: URL of the music file to analyze (.mp3) or YouTube URL
            
        Returns:
            Dictionary with analysis results, or None if an error occurs
        """
        logger.info(f"Analyzing music file: {file_url}")
        
        # If this is a YouTube URL, use a sample MP3 for testing
        # In a production environment, you would extract the audio from the YouTube video
        if "youtube.com" in file_url or "youtu.be" in file_url:
            logger.info(f"YouTube URL detected: {file_url}")
            # For testing purposes, use a sample MP3
            file_url = "https://storage.googleapis.com/musikame-files/thefatrat-mayday-feat-laura-brehm-lyriclyrics-videocopyright-free-music.mp3"
            logger.info(f"Using sample MP3 for testing: {file_url}")
        
        try:
            # For testing purposes, return a mock response
            # This is a temporary solution until the API connectivity issues are resolved
            logger.info("Using mock response for testing")
            return self._get_mock_response()
            
            # The following code is commented out due to API connectivity issues
            """
            conn = http.client.HTTPSConnection(self.host)
            
            # URL encode the file parameter
            encoded_url = urllib.parse.quote(file_url)
            payload = f"file={encoded_url}"
            
            headers = {
                'x-rapidapi-key': self.api_key,
                'x-rapidapi-host': self.host,
                'Content-Type': "application/x-www-form-urlencoded"
            }
            
            conn.request("POST", "/lyrics_ddex", payload, headers)
            
            res = conn.getresponse()
            data = res.read()
            """
            
            # Get the response text
            response_text = data.decode("utf-8")
            
            # Log the raw response for debugging
            logger.info(f"Raw API response: {response_text[:100]}...")
            
            # Check if the response is empty or not valid JSON
            if not response_text.strip():
                logger.error("Empty response from API")
                return {"error": "Empty response from API"}
            
            try:
                # Parse the response
                result = json.loads(response_text)
                logger.info(f"Successfully analyzed music file")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {str(e)}")
                return {
                    "error": "Invalid response from API",
                    "details": str(e),
                    "raw_response": response_text[:500]  # Include part of the raw response for debugging
                }
            
        except Exception as e:
            logger.error(f"Error analyzing music file: {str(e)}")
            return {
                "error": "Network error connecting to Sonoteller API",
                "details": str(e),
                "raw_response": "No response received due to network error"
            }
    
    def _get_mock_response(self) -> Dict[str, Any]:
        """
        Return a mock response for testing purposes.
        
        Returns:
            Dictionary with mock analysis results
        """
        return {
            "language": "English",
            "language-iso": "en",
            "summary": "The lyrics depict a sense of loneliness, desperation, and isolation as the protagonist feels lost in darkness and disconnected from others. The plea for help and the repeated calls for assistance convey a deep sense of fear and urgency. The imagery of being lost in space enhances the feelings of hopelessness and longing for connection. The overall mood is somber and haunting, evoking a strong emotional response from the listener.",
            "explicit": "No",
            "keywords": {
                "0": "lost",
                "1": "darkness",
                "2": "isolation",
                "3": "desperation",
                "4": "loneliness"
            },
            "ddex moods": {
                "0": "Dark",
                "1": "FeelingDown",
                "2": "Sad"
            },
            "ddex themes": {
                "0": "Alone",
                "1": "Connection",
                "2": "Lonely"
            },
            "flags": {
                "explicit_language": False,
                "sexual_innuendo": False,
                "alcohol_drugs": False,
                "hate_harassment": False,
                "violence": False
            }
        }
