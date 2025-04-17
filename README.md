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
- `openai_utils.py` - Utilities for generating responses using OpenAI
- `create_youtube_table.sql` - SQL script to create the YouTube table in Supabase
- `requirements.txt` - List of Python dependencies
- `Roadmap.md` - Project roadmap and implementation details
- `TESTING.md` - Documentation for testing the OpenAI comment response feature
- Test scripts:
  - `test_openai_response.py` - Tests OpenAI response generation
  - `test_youtube_reply.py` - Tests YouTube comment reply functionality
  - `test_comment_response_flow.py` - Tests the complete comment response flow
  - `test_fetch_specific_video.py` - Tests fetching comments for a specific video
  - `test_angus_specific_video.py` - Tests running Angus on a specific video

## Prerequisites

- Python 3.7+
- Supabase account with existing songs database
- YouTube API credentials (API key, OAuth client ID and client secret, channel ID)
- OpenAI API key (for generating responses to YouTube comments)

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
   pip install -r requirements.txt
   ```
   
   Or install dependencies manually:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client supabase requests openai python-dotenv schedule
   ```

3. Set up environment variables:
   ```bash
   # YouTube API Credentials
   export YOUTUBE_API_KEY=your-api-key
   export YOUTUBE_CLIENT_ID=your-client-id
   export YOUTUBE_CLIENT_SECRET=your-client-secret
   export YOUTUBE_CHANNEL_ID=your-channel-id

   # Supabase Credentials
   export SUPABASE_URL=your-supabase-url
   export SUPABASE_KEY=your-supabase-key
   
   # OpenAI API Credentials
   export OPENAI_API_KEY=your-openai-api-key
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

Retrieve comments for uploaded YouTube videos, store them in the Supabase feedback table, and reply to them:

```bash
python angus.py --fetch-comments --limit 10 --max-replies 10
```

This will:
- Fetch comments for up to 10 uploaded videos
- Store them in the feedback table
- Reply to up to 10 comments across all videos using OpenAI-generated responses

You can adjust the `--max-replies` parameter (default: 10) to control how many comments to reply to in a single run.

### Run in Daemon Mode

Run Agent Angus continuously with scheduled tasks:

```bash
python angus.py --daemon
```

In daemon mode, Agent Angus will:
- Upload 1 video to YouTube every hour
- Fetch comments from up to 10 videos every hour
- Automatically respond to up to 10 new comments per hour using OpenAI-generated responses
- Distribute replies fairly across videos
- Run continuously until interrupted (Ctrl+C)

This is useful for automating the YouTube publishing and feedback collection process.


## Features

### YouTube Video Upload
Agent Angus automatically uploads videos from your Supabase songs table to YouTube. It ensures that each song is only uploaded once by tracking the upload status in the YouTube table.

### Comment Collection
Agent Angus fetches comments from your YouTube videos and stores them in the Supabase feedback table for analysis.

### OpenAI-Powered Comment Responses
Agent Angus uses OpenAI to generate personalized responses to YouTube comments. The system:
- Fetches new comments from your videos
- Generates contextual responses based on the song title and style
- Posts the responses as replies to the comments
- Tracks which comments have already been responded to
- Intelligently distributes replies across multiple videos
- Limits the number of replies per hour to avoid rate limiting

The multi-comment reply capability ensures that:
- Up to 10 comments (configurable) are replied to per hour
- Replies are distributed fairly across all videos
- Comments that already have replies are skipped
- All processed comments are stored in the feedback table

This feature helps engage with your audience automatically and provides a way to track which comments have been processed.

### OpenAI-Powered Music Analysis
Agent Angus uses OpenAI to analyze music files and extract detailed insights. The system:
- Analyzes both MP3 files and YouTube videos
- Extracts information about lyrics, mood, themes, and musical characteristics
- Identifies genres, subgenres, instruments, BPM, and musical key
- Generates sample lyrics inspired by the music
- Creates music creation parameters for potential integration with music generation APIs
- Stores analysis results in the Supabase database

The web interface provides a user-friendly way to:
- Upload MP3 files for analysis
- Analyze music from YouTube URLs
- View formatted analysis results
- Access raw JSON data for further processing

To use the music analysis feature:
```bash
python angus.py --web --port 5000
```

This will start the web UI on port 5000, allowing you to analyze music through your browser.

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

### OpenAI API Issues

If you encounter issues with OpenAI comment responses:

1. Verify your OpenAI API key is correct in the `.env` file
2. Check that your OpenAI account has sufficient credits
3. If responses are not being generated, check the OpenAI API status at https://status.openai.com/
4. Adjust the system prompt in `openai_utils.py` if you want to change the style or length of responses

## Testing

Agent Angus includes several test scripts to verify different aspects of the system:

### OpenAI Response Testing

Test the OpenAI response generation without requiring YouTube integration:

```bash
python test_openai_response.py
```

This tests the ability to generate contextual responses to comments using OpenAI.

### YouTube Reply Testing

Test replying to a specific YouTube comment:

```bash
python test_youtube_reply.py --video-id VIDEO_ID [--comment-id COMMENT_ID]
```

This tests the ability to fetch comments and post replies on YouTube.

### Complete Flow Testing

Test the entire comment response flow:

```bash
python test_comment_response_flow.py --video-id VIDEO_ID
```

This tests the complete process from fetching comments to generating responses and posting replies.

### Specific Video Testing

Test fetching comments for a specific video and checking if they have replies:

```bash
python test_fetch_specific_video.py --video-id VIDEO_ID
```

Test running Angus on a specific video:

```bash
python test_angus_specific_video.py --video-id VIDEO_ID
```

For more detailed testing instructions, see the [TESTING.md](TESTING.md) file.

## License

[MIT License](LICENSE)
