# YouTube Authentication Instructions

This guide will help you authenticate with YouTube on your local development machine and transfer the authentication token to your server.

## Prerequisites

1. Make sure you have the required YouTube API credentials in your `config.py` file:
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_API_KEY`
   - `YOUTUBE_CHANNEL_ID`

2. Make sure you have the required Python packages installed:
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

## Step 1: Run the Authentication Script

1. Run the authentication script:
   ```bash
   python youtube_auth.py
   ```

2. The script will display a URL. Copy this URL and paste it into your web browser.

3. Sign in with your Google account and authorize the application.

4. After authorization, you will receive a code. Copy this code and paste it back into the terminal where the script is running.

5. The script will save the authentication token to a file called `token.pickle` (either in the current directory or in a `data` subdirectory).

## Step 2: Transfer the Token to Your Server

1. Use SCP to copy the token file to your server:
   ```bash
   scp ./data/token.pickle user@your-server:/opt/angus/data/token.pickle
   ```
   
   Or if the token is in the current directory:
   ```bash
   scp token.pickle user@your-server:/opt/angus/data/token.pickle
   ```

2. Make sure the token file has the correct permissions:
   ```bash
   ssh user@your-server "chmod 600 /opt/angus/data/token.pickle"
   ```

## Step 3: Restart the Angus Container

1. SSH into your server:
   ```bash
   ssh user@your-server
   ```

2. Navigate to the Angus directory:
   ```bash
   cd /opt/angus
   ```

3. Restart the Docker containers:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. Check the logs to verify that the YouTube client is now authenticated:
   ```bash
   docker logs angus_angus_1
   ```

   You should see a message like:
   ```
   INFO:youtube_client:Loaded credentials from /app/data/token.pickle
   INFO:youtube_client:YouTube client initialized
   ```

## Troubleshooting

If you encounter any issues:

1. Make sure your Google account has a YouTube channel associated with it.

2. Make sure your YouTube API project has the YouTube Data API v3 enabled.

3. If you see an error about invalid credentials, try deleting the token.pickle file and running the authentication script again.

4. If you're still having issues, check the logs for more detailed error messages:
   ```bash
   docker logs angus_angus_1
