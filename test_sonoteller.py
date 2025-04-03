"""
Test script for the Sonoteller API.
"""
import http.client
import json
import urllib.parse

def test_sonoteller_api():
    """Test the Sonoteller API with a sample MP3 URL."""
    # Sample MP3 URL
    file_url = "https://storage.googleapis.com/musikame-files/thefatrat-mayday-feat-laura-brehm-lyriclyrics-videocopyright-free-music.mp3"
    
    # API credentials
    api_key = "58fafc6204msh41ac38769729b59p17fbc3jsneeebeb330eb2"
    host = "sonoteller-ai1.p.rapidapi.com"
    
    try:
        # Create connection
        conn = http.client.HTTPSConnection(host)
        
        # URL encode the file parameter
        encoded_url = urllib.parse.quote(file_url)
        payload = f"file={encoded_url}"
        
        # Set headers
        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': host,
            'Content-Type': "application/x-www-form-urlencoded"
        }
        
        # Make request
        print(f"Sending request to {host}/lyrics_ddex with payload: {payload}")
        conn.request("POST", "/lyrics_ddex", payload, headers)
        
        # Get response
        res = conn.getresponse()
        data = res.read()
        
        # Print response status
        print(f"Response status: {res.status} {res.reason}")
        
        # Print response headers
        print("Response headers:")
        for header in res.getheaders():
            print(f"  {header[0]}: {header[1]}")
        
        # Print response data
        response_text = data.decode("utf-8")
        print(f"Response data (first 500 chars):")
        print(response_text[:500])
        
        # Try to parse as JSON
        try:
            result = json.loads(response_text)
            print("Successfully parsed response as JSON")
            print(json.dumps(result, indent=2))
        except json.JSONDecodeError as e:
            print(f"Failed to parse response as JSON: {str(e)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_sonoteller_api()
