#!/usr/bin/env python3
"""
YouTube Authentication Script for Angus

This script helps you authenticate with YouTube and generate a valid token.pickle file
that can be transferred to your server for use with the Angus application.
"""
import os
import sys
import logging
import pickle
import tempfile
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Import configuration if available, otherwise use environment variables
try:
    from config import YOUTUBE_API_KEY, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_CHANNEL_ID
except ImportError:
    print("Could not import config.py, using environment variables instead")
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    YOUTUBE_CLIENT_ID = os.environ.get('YOUTUBE_CLIENT_ID')
    YOUTUBE_CLIENT_SECRET = os.environ.get('YOUTUBE_CLIENT_SECRET')
    YOUTUBE_CHANNEL_ID = os.environ.get('YOUTUBE_CHANNEL_ID')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OAuth 2.0 scopes for YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", 
          "https://www.googleapis.com/auth/youtube.force-ssl"]

def authenticate():
    """
    Authenticate with YouTube API using OAuth 2.0.
    
    Returns:
        The authenticated YouTube API client if successful, None otherwise
    """
    creds = None
    token_paths = ['./data/token.pickle', 'token.pickle']
    token_path_used = None
    
    # Check if we already have a token
    for token_path in token_paths:
        if os.path.exists(token_path):
            try:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
                logger.info(f"Loaded credentials from {token_path}")
                token_path_used = token_path
                break
            except Exception as e:
                logger.warning(f"Error loading credentials from {token_path}: {str(e)}")
    
    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Refreshed expired credentials")
            except Exception as e:
                logger.warning(f"Error refreshing credentials: {str(e)}")
                # If refresh fails, force new authentication
                creds = None
        
        # If we still don't have valid credentials, get new ones
        if not creds or not creds.valid:
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
                print("\n" + "=" * 80)
                print("Please visit this URL to authorize this application:")
                print(auth_url)
                print("=" * 80)
                print("\nAfter authorization, you will receive a code. Please enter that code here:")
                
                # Get the authorization code from the user
                code = input().strip()
                
                # Exchange the authorization code for credentials
                flow.fetch_token(code=code)
                creds = flow.credentials
                
                logger.info("Authentication successful")
                
                # Save credentials for future use
                # Try to save in data directory first, then in current directory
                for save_path in ['./data', '.']:
                    try:
                        os.makedirs(save_path, exist_ok=True)
                        token_file = os.path.join(save_path, 'token.pickle')
                        with open(token_file, 'wb') as token:
                            pickle.dump(creds, token)
                        logger.info(f"Saved credentials to {token_file}")
                        token_path_used = token_file
                        break
                    except Exception as e:
                        logger.warning(f"Could not save credentials to {save_path}: {str(e)}")
                
            finally:
                # Clean up temporary file
                if os.path.exists(client_secrets_file):
                    os.remove(client_secrets_file)
    
    # Build YouTube API client
    try:
        youtube = build("youtube", "v3", credentials=creds)
        return youtube
    except Exception as e:
        logger.error(f"Error building YouTube client: {str(e)}")
        return None

def verify_authentication(youtube):
    """
    Verify that the authentication worked by making a simple API call.
    
    Args:
        youtube: The YouTube API client
        
    Returns:
        True if authentication is working, False otherwise
    """
    if not youtube:
        return False
    
    try:
        # Try to get the authenticated user's channel info
        request = youtube.channels().list(part="snippet", mine=True)
        response = request.execute()
        
        if response and 'items' in response and len(response['items']) > 0:
            channel = response['items'][0]
            channel_title = channel['snippet']['title']
            channel_id = channel['id']
            logger.info(f"Successfully authenticated as channel: {channel_title} (ID: {channel_id})")
            return True
        else:
            logger.error("Authentication verification failed: No channel found")
            return False
    except Exception as e:
        logger.error(f"Authentication verification failed: {str(e)}")
        return False

def main():
    """
    Main function to authenticate with YouTube and verify the authentication.
    """
    print("YouTube Authentication Script for Angus")
    print("This script will help you authenticate with YouTube and generate a valid token.pickle file.")
    
    # Check if we have the required credentials
    if not YOUTUBE_CLIENT_ID or not YOUTUBE_CLIENT_SECRET:
        print("\nERROR: YouTube OAuth credentials are missing!")
        print("Please make sure you have set the YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET")
        print("either in config.py or as environment variables.")
        return False
    
    # Authenticate with YouTube
    print("\nAuthenticating with YouTube...")
    youtube = authenticate()
    
    if not youtube:
        print("\nERROR: Failed to authenticate with YouTube.")
        return False
    
    # Verify the authentication
    print("\nVerifying authentication...")
    if verify_authentication(youtube):
        print("\nSUCCESS: Authentication successful!")
        
        # Find the token.pickle file
        token_paths = ['./data/token.pickle', 'token.pickle']
        token_path = None
        for path in token_paths:
            if os.path.exists(path):
                token_path = os.path.abspath(path)
                break
        
        if token_path:
            print(f"\nToken file saved at: {token_path}")
            print("\nTo use this token on your server:")
            print(f"1. Copy {token_path} to your server's /app/data directory")
            print("2. Restart the Angus container")
            print("\nExample SCP command (adjust as needed):")
            print(f"scp {token_path} user@your-server:/opt/angus/data/token.pickle")
        else:
            print("\nWARNING: Could not find the token.pickle file.")
        
        return True
    else:
        print("\nERROR: Authentication verification failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
