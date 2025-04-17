classmethod"""
Sonoteller client for analyzing music using the Sonoteller API.
"""
import http.client
import json
import logging
import urllib.parse
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
        
    def analyze_music(self, file_url: str, endpoint: str = "lyrics_ddex") -> Optional[Dict[str, Any]]:
        """
        Analyze a music file using Sonoteller API.
        
        Args:
            file_url: URL of the music file to analyze (.mp3 only)
            endpoint: API endpoint to use. Options: "lyrics_ddex" (default), "music_ddex", "lyrics", "music"
            
        Returns:
            Dictionary with analysis results, or None if an error occurs
        """
        logger.info(f"Analyzing music file: {file_url}")
        
        try:
            # Check if this is an MP3 URL
            if not file_url.lower().endswith('.mp3'):
                logger.error(f"Unsupported file format: {file_url}")
                return {
                    "error": "Unsupported file format",
                    "details": "Only MP3 URLs are supported. Please convert your media to MP3 format first.",
                    "raw_response": "No response received"
                }
        
            # Make the API request
            result = self._make_api_request(file_url, endpoint)
            
            # If successful, add metadata about the source
            if result and "error" not in result:
                result["_source_url"] = file_url
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing music file: {str(e)}")
            
            # Return error information
            return {
                "error": "Error analyzing music file",
                "details": str(e),
                "raw_response": "No response received due to error"
            }
    
    def _make_api_request(self, file_url: str, endpoint: str) -> Dict[str, Any]:
        """
        Make a request to the Sonoteller API.
        
        Args:
            file_url: URL of the music file to analyze
            endpoint: API endpoint to use
            
        Returns:
            Dictionary with analysis results
        """
        # Create connection to Sonoteller API
        conn = http.client.HTTPSConnection(self.host)
        
        # Create JSON payload as per documentation
        payload_data = {"file": file_url}
        payload = json.dumps(payload_data)
        
        headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': self.host,
            'Content-Type': "application/json"
        }
        
        # Validate endpoint
        valid_endpoints = ["lyrics_ddex", "music_ddex", "lyrics", "music"]
        if endpoint not in valid_endpoints:
            logger.warning(f"Invalid endpoint: {endpoint}. Using lyrics_ddex instead.")
            endpoint = "lyrics_ddex"
        
        logger.info(f"Sending request to {self.host}/{endpoint} with payload: {payload}")
        conn.request("POST", f"/{endpoint}", payload, headers)
        
        res = conn.getresponse()
        data = res.read()
        
        # Get the response text
        response_text = data.decode("utf-8")
        
        # Log the response status and headers
        logger.info(f"Response status: {res.status} {res.reason}")
        
        # Log the raw response for debugging (first 100 chars)
        logger.info(f"Raw API response: {response_text[:100]}...")
        
        # Check if the response status is not successful
        if res.status != 200:
            logger.error(f"API returned error status: {res.status} {res.reason}")
            return {
                "error": f"API error: {res.status} {res.reason}",
                "raw_response": response_text[:500]
            }
            
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
