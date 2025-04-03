"""
Test script for the Sonoteller API client.
"""
import json
import argparse
import logging
from sonoteller_client import SonotellerClient
from config import SONOTELLER_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sonoteller_client(file_url=None, use_direct_api=False, endpoint="lyrics_ddex"):
    """
    Test the Sonoteller client with a sample MP3 URL.
    
    Args:
        file_url: Optional URL to a music file. If not provided, a sample URL will be used.
        use_direct_api: If True, test the API directly without using the client class.
        endpoint: API endpoint to use.
    """
    # Use provided URL or default to sample MP3
    if not file_url:
        file_url = "https://storage.googleapis.com/musikame-files/thefatrat-mayday-feat-laura-brehm-lyriclyrics-videocopyright-free-music.mp3"
    
    print(f"Testing Sonoteller API with file URL: {file_url}")
    print(f"Endpoint: {endpoint}")
    
    # Check if it's an MP3 URL
    if not file_url.lower().endswith('.mp3'):
        print("Error: Only MP3 URLs are supported.")
        return
    
    # Create Sonoteller client
    client = SonotellerClient(SONOTELLER_API_KEY)
    
    # Test the client
    try:
        print("Sending request to Sonoteller API...")
        result = client.analyze_music(
            file_url, 
            endpoint=endpoint
        )
        
        if result:
            if "error" in result:
                print(f"Error from API: {result['error']}")
                if "details" in result:
                    print(f"Details: {result['details']}")
                if "raw_response" in result:
                    print(f"Raw response: {result['raw_response']}")
            else:
                print("Successfully received and parsed response")
                print(json.dumps(result, indent=2))
                
                # Print key information
                if "language" in result:
                    print(f"\nLanguage: {result['language']}")
                if "summary" in result:
                    print(f"\nSummary: {result['summary']}")
                if "ddex moods" in result:
                    # Handle both list and dictionary formats
                    if isinstance(result['ddex moods'], list):
                        print(f"\nMoods: {', '.join(result['ddex moods'])}")
                    else:
                        print(f"\nMoods: {', '.join(result['ddex moods'].values())}")
                if "ddex themes" in result:
                    # Handle both list and dictionary formats
                    if isinstance(result['ddex themes'], list):
                        print(f"\nThemes: {', '.join(result['ddex themes'])}")
                    else:
                        print(f"\nThemes: {', '.join(result['ddex themes'].values())}")
                if "keywords" in result:
                    # Handle both list and dictionary formats
                    if isinstance(result['keywords'], list):
                        print(f"\nKeywords: {', '.join(result['keywords'])}")
                    else:
                        print(f"\nKeywords: {', '.join(result['keywords'].values())}")
                
                # Check if this is a real API response or a mock
                if "error" in result:
                    print(f"\nERROR: {result['error']}")
                    if "details" in result:
                        print(f"Details: {result['details']}")
        else:
            print("No result returned from API")
            
    except Exception as e:
        print(f"Error testing Sonoteller client: {str(e)}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the Sonoteller API client")
    parser.add_argument("--url", help="URL of the MP3 file to analyze")
    parser.add_argument("--direct", action="store_true", help="Test the API directly without using the client class")
    parser.add_argument("--endpoint", default="lyrics_ddex", 
                       choices=["lyrics_ddex", "music_ddex", "lyrics", "music"], 
                       help="API endpoint to use")
    args = parser.parse_args()
    
    # Run the test
    test_sonoteller_client(
        args.url, 
        args.direct,
        args.endpoint
    )
