# Agent Angus

Agent Angus is an AI agent that automates YouTube publishing and audience feedback collection for AI-generated music videos.

## Overview

Agent Angus automates the following tasks:

1. **Upload existing songs from Supabase** to YouTube
2. **Track uploaded videos** in a new YouTube table
3. **Retrieve and store YouTube comments** in the Supabase database for analysis

## Project Structure

- `angus.py` - Main script for Agent Angus
- `youtube_client.py` - Client for interacting with YouTube API
- `supabase_client.py` - Client for interacting with Supabase
- `create_youtube_table.sql` - SQL script to create the YouTube table in Supabase
- `Roadmap.md` - Project roadmap and implementation details

## Prerequisites

- Python 3.7+
- Supabase account with existing songs database
- YouTube API credentials (API key, OAuth client ID and client secret)

### YouTube API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" > "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as the application type
   - Add the following authorized redirect URI:
     - `urn:ietf:wg:oauth:2.0:oob` (this is for out-of-band authentication)
5. Note your Client ID and Client Secret
6. Create an API key for simple API calls

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd angus
   ```

2. Install dependencies:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client supabase requests
   ```

3. Set up environment variables:
   ```bash
   # YouTube API Credentials
   export YOUTUBE_API_KEY=your-api-key
   export YOUTUBE_CLIENT_ID=your-client-id
   export YOUTUBE_CLIENT_SECRET=your-client-secret

   # Supabase Credentials
   export SUPABASE_URL=your-supabase-url
   export SUPABASE_KEY=your-supabase-key
   ```

   Alternatively, create a `.env` file with these variables.

## Usage

### Create YouTube Table

Create the YouTube table in Supabase to track uploaded videos:

```bash
python angus.py --create-table
```

### Upload Songs to YouTube

Upload songs from the Supabase songs table to YouTube:

```bash
python angus.py --upload --limit 5
```

This will upload up to 5 songs that have video URLs but haven't been uploaded to YouTube yet.

### Fetch Comments

Retrieve comments for uploaded YouTube videos and store them in the Supabase feedback table:

```bash
python angus.py --fetch-comments --limit 10
```

This will fetch comments for up to 10 uploaded videos and store them in the feedback table.

### Run in Daemon Mode

Run Agent Angus continuously with scheduled tasks:

```bash
python angus.py --daemon
```

In daemon mode, Agent Angus will:
- Upload up to 3 videos to YouTube every hour
- Fetch comments from uploaded videos every hour
- Run continuously until interrupted (Ctrl+C)

This is useful for automating the YouTube publishing and feedback collection process.


## Database Schema

### YouTube Table

The YouTube table tracks videos uploaded to YouTube:

| Field Name      | Type        | Description                                  |
|----------------|------------|----------------------------------------------|
| `id` (PK)      | `uuid`      | Unique ID, primary key (auto-generated)     |
| `song_id`      | `uuid`      | Reference to songs table                    |
| `youtube_id`   | `text`      | YouTube video ID                            |
| `title`        | `text`      | Video title on YouTube                      |
| `description`  | `text`      | Video description on YouTube                |
| `upload_date`  | `timestamp` | Timestamp of when the video was uploaded    |
| `status`       | `text`      | Upload status (e.g., "pending", "uploaded", "failed") |
| `view_count`   | `integer`   | Number of views (can be updated periodically) |
| `like_count`   | `integer`   | Number of likes (can be updated periodically) |

## Troubleshooting

### OAuth Authentication Instructions

The first time you run the script with the `--upload` flag, you'll need to authenticate with YouTube:

1. Make sure you've added the required redirect URI to your Google Cloud Console project:
   - `urn:ietf:wg:oauth:2.0:oob` (for out-of-band authentication)

2. When you run the script, it will display a URL in the console like this:
   ```
   Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?...
   After authorization, you will receive a code. Please enter that code here:
   ```

3. Copy and paste this URL into your browser
   
4. Sign in with your Google account and grant the requested permissions

5. After authorization, you'll see a code displayed in the browser. Copy this code.

6. Paste the code back into the console prompt and press Enter

7. If authentication is successful, a `token.pickle` file will be created in your project directory. This file stores your credentials for future use, so you won't need to repeat this process unless the token expires.

### Troubleshooting OAuth Issues

If you encounter OAuth errors:

1. Verify that you've added the correct redirect URI (`urn:ietf:wg:oauth:2.0:oob`) to your Google Cloud Console project
2. Make sure you're using the correct client ID and client secret in your `.env` file
3. Check that your Google Cloud project has the YouTube Data API v3 enabled
4. If you're still having issues, try deleting the `token.pickle` file (if it exists) and authenticating again

### Supabase Connection Issues

If you encounter Supabase connection errors:

1. Verify your Supabase URL and key in the `.env` file
2. Make sure your Supabase project is active
3. Check that the required tables exist in your database

### Video Upload Issues

If videos fail to upload:

1. Check that the video URLs in your songs table are valid and accessible
2. Verify that your YouTube account has upload permissions
3. Check for any quota limitations on your YouTube API usage

## License

[MIT License](LICENSE)
