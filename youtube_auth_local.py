#!/usr/bin/env python3
"""
YouTube Authentication Script

This script authenticates with the YouTube API and generates a token.pickle file
that can be used for non-interactive authentication in Docker containers.
"""
import os
import pickle
import tempfile
import json
import sys

# Check if required packages are installed
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
except ImportError:
    print("Required packages not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-auth-oauthlib", "google-auth"])
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

# OAuth 2.0 scopes for YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", 
          "https://www.googleapis.com/auth/youtube.force-ssl"]

def get_env_var(var_name, prompt_message=None):
    """Get an environment variable or prompt the user for it."""
    value = os.environ.get(var_name)
    if not value and prompt_message:
        value = input(prompt_message)
        # Save to environment for future use
        os.environ[var_name] = value
    return value

def authenticate():
    """Authenticate with YouTube API and save token."""
    # Get credentials from environment variables or prompt
    client_id = get_env_var("YOUTUBE_CLIENT_ID", 
                           "Enter your YouTube Client ID: ")
    client_secret = get_env_var("YOUTUBE_CLIENT_SECRET", 
                               "Enter your YouTube Client Secret: ")
    
    if not client_id or not client_secret:
        print("Error: YouTube Client ID and Client Secret are required.")
        return False
    
    # Create client_secrets.json file for OAuth flow
    client_secrets = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
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
        print("\n" + "="*80)
        print("Please visit this URL to authorize this application:")
        print(auth_url)
        print("="*80 + "\n")
        print("After authorization, you will receive a code. Please enter that code here:")
        
        # Get the authorization code from the user
        code = input().strip()
        
        # Exchange the authorization code for credentials
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        print("\nAuthentication successful!")
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Save credentials to token.pickle in data directory
        token_path = os.path.join("data", "token.pickle")
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"Saved credentials to {token_path}")
        print("\nYou can now copy this file to your server with:")
        print(f"scp {token_path} root@angs.club:/opt/angus/data/")
        
        return True
        
    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        return False
        
    finally:
        # Clean up temporary file
        if os.path.exists(client_secrets_file):
            os.remove(client_secrets_file)

if __name__ == "__main__":
    print("YouTube Authentication Script")
    print("-----------------------------")
    print("This script will help you authenticate with the YouTube API")
    print("and generate a token.pickle file for use in Docker containers.\n")
    
    success = authenticate()
    
    if success:
        print("\nNext steps:")
        print("1. Copy the token.pickle file to your server:")
        print("   scp data/token.pickle root@angs.club:/opt/angus/data/")
        print("2. SSH into your server:")
        print("   ssh root@angs.club")
        print("3. Restart the Coral Protocol adapter:")
        print("   cd /opt/angus")
        print("   docker-compose restart coral")
        print("4. Check the logs:")
        print("   docker logs angus_coral_1")
    else:
        print("\nAuthentication failed. Please try again.")
