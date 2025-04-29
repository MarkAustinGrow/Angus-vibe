# YouTube Authentication for Coral Protocol Integration

This document provides instructions for authenticating with YouTube to fix the Coral Protocol integration on your Linode server.

## The Problem

The Coral Protocol adapter is failing to start because it needs to authenticate with YouTube, but it can't do so in a non-interactive Docker environment. The logs show:

```
WARNING:youtube_client:Error refreshing credentials: ('invalid_grant: Token has been expired or revoked.', {'error': 'invalid_grant', 'error_description': 'Token has been expired or revoked.'})
ERROR:youtube_client:Error initializing YouTube client: EOF when reading a line
```

## The Solution

We need to:
1. Generate a valid YouTube authentication token locally
2. Copy this token to the server
3. Restart the Coral Protocol adapter

## Step 1: Run the Authentication Script Locally

### On Windows:

1. Double-click on `run_youtube_auth_local.bat`
2. Follow the prompts to enter your YouTube API credentials
3. Visit the provided URL in your browser
4. Authorize the application and copy the code
5. Paste the code into the script when prompted

### On Unix/Linux:

1. Make the script executable:
   ```bash
   chmod +x run_youtube_auth_local.sh
   ```
2. Run the script:
   ```bash
   ./run_youtube_auth_local.sh
   ```
3. Follow the prompts to enter your YouTube API credentials
4. Visit the provided URL in your browser
5. Authorize the application and copy the code
6. Paste the code into the script when prompted

## Step 2: Copy the Token to the Server

After successful authentication, the script will create a `token.pickle` file in the `data` directory. Copy this file to your server:

```bash
scp data/token.pickle root@angs.club:/opt/angus/data/
```

## Step 3: Restart the Coral Protocol Adapter

SSH into your server and restart the Coral Protocol adapter:

```bash
ssh root@angs.club
cd /opt/angus
docker-compose restart coral
```

## Step 4: Verify the Integration

Check the logs to make sure the adapter is now running without authentication errors:

```bash
docker logs angus_coral_1
```

## Troubleshooting

### Authentication Fails

If you encounter issues during authentication:
1. Make sure you're using the correct YouTube API credentials
2. Check that you have the necessary permissions for the YouTube channel
3. Try clearing your browser cookies and cache before authorizing

### Token Not Working

If the token doesn't work on the server:
1. Make sure the token.pickle file was copied to the correct location
2. Check the permissions on the token.pickle file
3. Try regenerating the token with the authentication script

### Adapter Still Failing

If the Coral Protocol adapter is still failing after copying the token:
1. Check the Docker logs for any other errors
2. Make sure the data directory is properly mounted in the Docker container
3. Try restarting the entire Docker stack:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Token Expiration

YouTube tokens typically expire after some time. If you encounter authentication issues in the future, you may need to repeat this process to generate a new token.

## Security Considerations

The `token.pickle` file contains sensitive credentials that grant access to your YouTube account. Handle it securely:

1. Don't share the token with unauthorized users
2. Don't commit the token to version control
3. Use secure methods to transfer the token to your server

## Alternative Approaches

If you continue to have issues with YouTube authentication, consider:

1. Modifying the Coral Protocol adapter to skip YouTube authentication
2. Using a service account instead of OAuth for authentication
3. Implementing a non-interactive authentication method

For more information on YouTube API authentication, see the [Google API Client Library documentation](https://developers.google.com/api-client-library/python/guide/aaa_oauth).
