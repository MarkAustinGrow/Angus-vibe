#!/usr/bin/env python3
"""
Standalone YouTube authentication script for generating token.pickle
This script can be run in the Docker container to authenticate with YouTube.
"""

import os
import pickle
import tempfile
import json
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from config import YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth 2.0 scopes for YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", 
          "https://www.googleapis.com/auth/youtube.force-ssl"]

def authenticate_youtube():
    """
    Authenticate with YouTube API and save token.pickle
    """
    print("=== YouTube Authentication ===")
    print("This will generate a new token.pickle file for YouTube API access.")
    print()
    
    # Validate credentials
    if not YOUTUBE_CLIENT_ID or not YOUTUBE_CLIENT_SECRET:
        print("❌ Error: YouTube OAuth credentials are missing!")
        print("Please check your environment variables:")
        print("- YOUTUBE_CLIENT_ID")
        print("- YOUTUBE_CLIENT_SECRET")
        return False
    
    # Create client_secrets.json file for OAuth flow
    client_secrets = {
        "installed": {
            "client_id": YOUTUBE_CLIENT_ID,
            "client_secret": YOUTUBE_CLIENT_SECRET,
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    
    # Write client secrets to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(client_secrets, f)
        client_secrets_file = f.name
    
    try:
        # Create flow from client secrets file
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, 
            SCOPES,
            redirect_uri="urn:ietf:wg:oauth:2.0:oob"
        )
        
        # Get the authorization URL
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        # Print the URL for the user to visit
        print("🔗 Please visit this URL to authorize this application:")
        print(f"   {auth_url}")
        print()
        print("📋 After authorization, you will receive a code.")
        print("💬 Please enter that code here:")
        
        # Get the authorization code from the user
        code = input("Authorization code: ").strip()
        
        if not code:
            print("❌ No authorization code provided!")
            return False
        
        # Exchange the authorization code for credentials
        print("🔄 Exchanging authorization code for credentials...")
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        print("✅ Authentication successful!")
        
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(client_secrets_file):
            os.remove(client_secrets_file)
    
    # Save credentials for future use
    # Try to save in data directory first, then in current directory
    save_paths = ['/app/data', './data', '.']
    saved = False
    
    for save_path in save_paths:
        try:
            os.makedirs(save_path, exist_ok=True)
            token_file = os.path.join(save_path, 'token.pickle')
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
            print(f"💾 Saved credentials to {token_file}")
            saved = True
            break
        except Exception as e:
            logger.warning(f"Could not save credentials to {save_path}: {str(e)}")
    
    if not saved:
        print("❌ Failed to save credentials to any location!")
        return False
    
    print("🎉 YouTube authentication completed successfully!")
    print("📁 Token saved as token.pickle")
    print("🚀 You can now start the main Angus container.")
    return True

if __name__ == "__main__":
    success = authenticate_youtube()
    exit(0 if success else 1)
