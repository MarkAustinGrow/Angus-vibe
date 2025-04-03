# Agent Angus Codebase Documentation

## Overview

Agent Angus is an AI agent that automates YouTube publishing and audience feedback collection for AI-generated music videos. The application performs the following key tasks:

1. Uploads existing songs from Supabase to YouTube
2. Tracks uploaded videos in a YouTube table in Supabase
3. Retrieves and stores YouTube comments in the Supabase database for analysis
4. Responds to YouTube comments using OpenAI-generated responses
5. Analyzes music using the Sonoteller API and stores results in Supabase

## System Architecture

Agent Angus consists of several key components that work together:

1. **Main Agent (angus.py)**: Orchestrates the entire system, handling command-line arguments, scheduling tasks, and coordinating between components.
2. **Supabase Client (supabase_client.py)**: Manages database operations with Supabase, including storing video information and comments.
3. **YouTube Client (youtube_client.py)**: Handles all interactions with the YouTube API, including video uploads, comment fetching, and comment replies.
4. **OpenAI Utilities (openai_utils.py)**: Generates responses to YouTube comments using OpenAI's API.
5. **Sonoteller Client (sonoteller_client.py)**: Handles interactions with the Sonoteller API for music analysis.
6. **Web UI (web_ui.py)**: Provides a web interface for analyzing music using the Sonoteller API.
7. **Database Schema (create_youtube_table.sql)**: Defines the structure of the YouTube table in Supabase.
8. **Test Scripts**: Various scripts to test different aspects of the system.

## Component Documentation

### 1. AgentAngus (angus.py)

The `AgentAngus` class is the main orchestrator of the application, coordinating between the Supabase database, YouTube API, and OpenAI.

#### Class: `AgentAngus`

##### Constructor

```python
def __init__(self)
```

**Description**: Initializes Agent Angus by creating instances of the Supabase and YouTube clients.

**Parameters**: None

**Returns**: None

**Example**:
```python
angus = AgentAngus()
```

##### Method: `create_youtube_table`

```python
def create_youtube_table(self) -> bool
```

**Description**: Creates the YouTube table in Supabase if it doesn't exist. Reads the SQL from the create_youtube_table.sql file and executes it.

**Parameters**: None

**Returns**: 
- `bool`: True if successful, False otherwise

**Example**:
```python
success = angus.create_youtube_table()
if success:
    print("YouTube table created successfully")
else:
    print("Failed to create YouTube table")
```

**Error Handling**: Logs errors but continues with other statements if one statement fails.

##### Method: `get_songs_to_upload`

```python
def get_songs_to_upload(self, limit: int = 10) -> List[Dict[str, Any]]
```

**Description**: Gets songs from Supabase that haven't been successfully uploaded to YouTube yet.

**Parameters**:
- `limit` (int, optional): Maximum number of songs to return. Defaults to 10.

**Returns**:
- `List[Dict[str, Any]]`: List of song data dictionaries

**Example**:
```python
songs = angus.get_songs_to_upload(limit=5)
for song in songs:
    print(f"Song to upload: {song['title']}")
```

**Error Handling**: Returns an empty list if an error occurs.

##### Method: `upload_song_to_youtube`

```python
def upload_song_to_youtube(self, song: Dict[str, Any]) -> Optional[str]
```

**Description**: Uploads a song to YouTube and stores the result in the youtube table.

**Parameters**:
- `song` (Dict[str, Any]): Song data dictionary

**Returns**:
- `Optional[str]`: YouTube video ID if successful, None otherwise

**Raises**:
- `Exception`: If there's an error during upload, including upload limit exceeded

**Example**:
```python
song = {
    'id': 'song-id',
    'title': 'Song Title',
    'video_url': 'https://example.com/video.mp4',
    'gpt_description': 'This is a description',
    'lyrics': 'These are the lyrics',
    'style': 'pop, rock'
}
youtube_id = angus.upload_song_to_youtube(song)
if youtube_id:
    print(f"Successfully uploaded to YouTube with ID: {youtube_id}")
else:
    print("Failed to upload to YouTube")
```

**Error Handling**: 
- Records upload failures in the youtube table
- Re-raises upload limit exceeded errors to be caught by upload_all_pending_songs

##### Method: `upload_all_pending_songs`

```python
def upload_all_pending_songs(self, limit: int = 10) -> int
```

**Description**: Uploads all pending songs to YouTube.

**Parameters**:
- `limit` (int, optional): Maximum number of songs to upload. Defaults to 10.

**Returns**:
- `int`: Number of successfully uploaded songs

**Example**:
```python
uploaded_count = angus.upload_all_pending_songs(limit=5)
print(f"Successfully uploaded {uploaded_count} songs")
```

**Error Handling**:
- Handles upload limit exceeded errors by stopping further uploads
- Adds a small delay between uploads to avoid rate limiting

##### Method: `fetch_comments_for_video`

```python
def fetch_comments_for_video(self, youtube_id: str, song_id: str = None, max_replies: int = None) -> int
```

**Description**: Fetches comments for a YouTube video, stores them in the feedback table, and replies to them using OpenAI.

**Parameters**:
- `youtube_id` (str): YouTube video ID
- `song_id` (str, optional): Optional song ID (if not provided, will be looked up)
- `max_replies` (int, optional): Maximum number of replies to post (None for unlimited)

**Returns**:
- `int`: Number of comments fetched and stored

**Example**:
```python
comments_count = angus.fetch_comments_for_video('youtube-video-id', max_replies=5)
print(f"Fetched and processed {comments_count} comments")
```

**Error Handling**:
- Skips comments that already exist in the feedback table
- Skips comments that already have replies
- Logs errors for individual comment processing but continues with other comments

##### Method: `fetch_comments_for_all_videos`

```python
def fetch_comments_for_all_videos(self, limit: int = 10, max_total_replies: int = 10) -> int
```

**Description**: Fetches comments for all uploaded YouTube videos.

**Parameters**:
- `limit` (int, optional): Maximum number of videos to process. Defaults to 10.
- `max_total_replies` (int, optional): Maximum total number of replies to post across all videos. Defaults to 10.

**Returns**:
- `int`: Total number of comments fetched

**Example**:
```python
total_comments = angus.fetch_comments_for_all_videos(limit=5, max_total_replies=10)
print(f"Fetched a total of {total_comments} comments")
```

**Error Handling**:
- Distributes replies fairly across videos
- Adds a small delay between requests to avoid rate limiting
- Stops when the maximum total replies is reached

##### Method: `run_scheduled_tasks`

```python
def run_scheduled_tasks(self)
```

**Description**: Runs scheduled tasks continuously. This method sets up scheduled tasks to run at specified intervals: upload videos to YouTube every hour and fetch comments from YouTube videos every hour. The method runs indefinitely until interrupted.

**Parameters**: None

**Returns**: None

**Example**:
```python
# This will run indefinitely until interrupted
angus.run_scheduled_tasks()
```

**Error Handling**:
- Catches and logs errors in scheduled tasks but continues running
- Handles keyboard interrupts for graceful shutdown

#### Function: `main`

```python
def main()
```

**Description**: Main entry point for Agent Angus. Parses command-line arguments and runs the appropriate tasks.

**Parameters**: None

**Returns**: None

**Example**:
```python
# Called when the script is run directly
if __name__ == "__main__":
    main()
```

**Command-line Arguments**:
- `--create-table`: Create the YouTube table in Supabase
- `--upload`: Upload pending songs to YouTube
- `--fetch-comments`: Fetch comments for uploaded videos
- `--limit`: Limit the number of items to process (default: 1)
- `--max-replies`: Maximum number of comment replies to post (default: 10)
- `--daemon`: Run in daemon mode with scheduled tasks
- `--web`: Run the web UI for Sonoteller analysis
- `--port`: Port for the web UI (default: 5000)

### 2. SupabaseClient (supabase_client.py)

The `SupabaseClient` class handles all interactions with the Supabase database.

#### Class: `SupabaseClient`

##### Constructor

```python
def __init__(self, url: Optional[str] = None, key: Optional[str] = None)
```

**Description**: Initializes the Supabase client with the provided URL and key, or uses the values from the environment variables.

**Parameters**:
- `url` (Optional[str]): Supabase URL (defaults to environment variable)
- `key` (Optional[str]): Supabase key (defaults to environment variable)

**Returns**: None

**Raises**:
- `ValueError`: If Supabase credentials are missing
- `Exception`: If there's an error initializing the Supabase client

**Example**:
```python
# Using environment variables
supabase = SupabaseClient()

# Using custom credentials
supabase = SupabaseClient(url="https://your-project.supabase.co", key="your-api-key")
```

##### Method: `store_song_data`

```python
def store_song_data(self, song_data: Dict[str, Any]) -> str
```

**Description**: Stores song data in Supabase.

**Parameters**:
- `song_data` (Dict[str, Any]): Dictionary with song data including title, lyrics, audio_url, etc.

**Returns**:
- `str`: The ID of the created song record, or None if an error occurs

**Example**:
```python
song_data = {
    'title': 'New Song',
    'lyrics': 'These are the lyrics',
    'video_url': 'https://example.com/video.mp4',
    'style': 'pop, rock'
}
song_id = supabase.store_song_data(song_data)
if song_id:
    print(f"Song stored with ID: {song_id}")
else:
    print("Failed to store song")
```

**Error Handling**: Returns None if an error occurs during the insert operation.

##### Method: `get_song_by_id`

```python
def get_song_by_id(self, song_id: str) -> Dict[str, Any]
```

**Description**: Retrieves a song by its ID.

**Parameters**:
- `song_id` (str): The ID of the song to retrieve

**Returns**:
- `Dict[str, Any]`: Dictionary with song data, or None if not found

**Example**:
```python
song = supabase.get_song_by_id('song-id')
if song:
    print(f"Retrieved song: {song['title']}")
else:
    print("Song not found")
```

**Error Handling**: Returns None if the song is not found or if an error occurs.

##### Method: `list_songs`

```python
def list_songs(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]
```

**Description**: List songs from the database.

**Parameters**:
- `limit` (int, optional): Maximum number of songs to return. Defaults to 10.
- `offset` (int, optional): Offset for pagination. Defaults to 0.

**Returns**:
- `List[Dict[str, Any]]`: List of song data dictionaries

**Example**:
```python
songs = supabase.list_songs(limit=5, offset=10)
for song in songs:
    print(f"Song: {song['title']}")
```

**Error Handling**: Returns an empty list if an error occurs or if no songs are found.

### 3. YouTubeClient (youtube_client.py)

The `YouTubeClient` class handles all interactions with the YouTube API.

#### Class: `YouTubeClient`

##### Constructor

```python
def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, 
             api_key: Optional[str] = None, channel_id: Optional[str] = None)
```

**Description**: Initializes the YouTube client with the provided credentials, or uses the values from the environment variables.

**Parameters**:
- `client_id` (Optional[str]): YouTube OAuth client ID (defaults to environment variable)
- `client_secret` (Optional[str]): YouTube OAuth client secret (defaults to environment variable)
- `api_key` (Optional[str]): YouTube API key (defaults to environment variable)
- `channel_id` (Optional[str]): YouTube channel ID (defaults to environment variable)

**Returns**: None

**Raises**:
- `ValueError`: If YouTube OAuth credentials are missing
- `Exception`: If there's an error initializing the YouTube client

**Example**:
```python
# Using environment variables
youtube = YouTubeClient()

# Using custom credentials
youtube = YouTubeClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    api_key="your-api-key",
    channel_id="your-channel-id"
)
```

##### Method: `authenticate`

```python
def authenticate(self) -> None
```

**Description**: Authenticates with YouTube API using OAuth 2.0.

**Parameters**: None

**Returns**: None

**Example**:
```python
youtube.authenticate()
```

**Error Handling**:
- Refreshes the token if it's expired
- Creates a new token if it doesn't exist or can't be refreshed
- Saves the token for future use

##### Method: `upload_video`

```python
def upload_video(self, video_url: str, title: str, description: str, 
                 tags: List[str] = None) -> Optional[str]
```

**Description**: Upload a video to YouTube.

**Parameters**:
- `video_url` (str): URL of the video file to upload
- `title` (str): Title of the video
- `description` (str): Description of the video
- `tags` (List[str], optional): List of tags for the video. Defaults to None.

**Returns**:
- `Optional[str]`: YouTube video ID if successful, None otherwise

**Example**:
```python
youtube_id = youtube.upload_video(
    video_url="https://example.com/video.mp4",
    title="My Video",
    description="This is my video description",
    tags=["music", "original"]
)
if youtube_id:
    print(f"Video uploaded with ID: {youtube_id}")
else:
    print("Failed to upload video")
```

**Error Handling**:
- Downloads the video to a temporary file
- Reports upload progress
- Cleans up the temporary file after upload
- Re-raises upload limit exceeded errors
- Returns None for other errors

##### Method: `reply_to_comment`

```python
def reply_to_comment(self, comment_id: str, reply_text: str) -> Optional[str]
```

**Description**: Reply to a YouTube comment.

**Parameters**:
- `comment_id` (str): The ID of the comment to reply to
- `reply_text` (str): The text of the reply

**Returns**:
- `Optional[str]`: The ID of the reply comment if successful, None otherwise

**Example**:
```python
reply_id = youtube.reply_to_comment(
    comment_id="comment-id",
    reply_text="Thank you for your comment!"
)
if reply_id:
    print(f"Reply posted with ID: {reply_id}")
else:
    print("Failed to post reply")
```

**Error Handling**: Returns None if an error occurs during the reply operation.

##### Method: `fetch_comments`

```python
def fetch_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]
```

**Description**: Fetch comments for a YouTube video.

**Parameters**:
- `video_id` (str): YouTube video ID
- `max_results` (int, optional): Maximum number of comments to retrieve. Defaults to 100.

**Returns**:
- `List[Dict[str, Any]]`: List of comment data dictionaries

**Example**:
```python
comments = youtube.fetch_comments(video_id="video-id", max_results=50)
for comment in comments:
    print(f"Comment by {comment['author']}: {comment['content']}")
```

**Error Handling**:
- Returns an empty list if an error occurs or if no comments are found
- Checks if we've already replied to each comment

### 4. OpenAI Utilities (openai_utils.py)

The `openai_utils.py` module provides functions for generating responses using OpenAI.

#### Function: `generate_response`

```python
def generate_response(comment_text: str, song_title: str, song_style: Optional[str] = None) -> Optional[str]
```

**Description**: Generate a response to a YouTube comment using OpenAI.

**Parameters**:
- `comment_text` (str): The text of the comment
- `song_title` (str): The title of the song
- `song_style` (Optional[str]): Optional style information about the song. Defaults to None.

**Returns**:
- `Optional[str]`: Generated response text, or None if an error occurs

**Example**:
```python
response = generate_response(
    comment_text="I love this song!",
    song_title="Cosmic Dreams",
    song_style="Electronic, Ambient"
)
if response:
    print(f"Generated response: {response}")
else:
    print("Failed to generate response")
```

**Error Handling**: Returns None if an error occurs during the API call.

### 5. SonotellerClient (sonoteller_client.py)

The `SonotellerClient` class handles all interactions with the Sonoteller API for music analysis.

#### Class: `SonotellerClient`

##### Constructor

```python
def __init__(self, api_key: str)
```

**Description**: Initializes the Sonoteller client with the provided API key.

**Parameters**:
- `api_key` (str): Sonoteller API key

**Returns**: None

**Example**:
```python
# Using environment variable
from config import SONOTELLER_API_KEY
sonoteller = SonotellerClient(SONOTELLER_API_KEY)
```

##### Method: `analyze_music`

```python
def analyze_music(self, file_url: str) -> Optional[Dict[str, Any]]
```

**Description**: Analyze a music file using the Sonoteller API.

**Parameters**:
- `file_url` (str): URL of the music file to analyze (.mp3) or YouTube URL

**Returns**:
- `Optional[Dict[str, Any]]`: Dictionary with analysis results, or None if an error occurs

**Example**:
```python
analysis = sonoteller.analyze_music("https://example.com/song.mp3")
if analysis:
    print(f"Language: {analysis.get('language')}")
    print(f"Summary: {analysis.get('summary')}")
else:
    print("Failed to analyze music")
```

**Error Handling**:
- Handles YouTube URLs by using a sample MP3 for testing
- Returns detailed error information if the API call fails
- Provides a mock response for testing when the API is unavailable

### 6. Web UI (web_ui.py)

The `web_ui.py` module provides a web interface for analyzing music using the Sonoteller API.

#### Function: `run_web_ui`

```python
def run_web_ui(host='0.0.0.0', port=5000, debug=False)
```

**Description**: Run the web UI for Sonoteller analysis.

**Parameters**:
- `host` (str, optional): Host to bind to. Defaults to '0.0.0.0'.
- `port` (int, optional): Port to bind to. Defaults to 5000.
- `debug` (bool, optional): Whether to run in debug mode. Defaults to False.

**Returns**: None

**Example**:
```python
# Run the web UI on port 8080
run_web_ui(port=8080)
```

#### Route: `/`

**Description**: Renders the main page of the web UI.

**Method**: GET

**Returns**: HTML page with a form for entering a music URL.

#### Route: `/analyze`

**Description**: Analyzes a music file using the Sonoteller API.

**Method**: POST

**Parameters**:
- `url` (str): URL of the music file to analyze (.mp3) or YouTube URL
- `song_id` (str, optional): Optional song ID to associate with the analysis

**Returns**: JSON response with analysis results.

**Error Handling**:
- Returns a 400 error if no URL is provided
- Returns a 500 error if the analysis fails
- Stores the analysis in the influence_music table in Supabase

## Database Schema

### YouTube Table

The YouTube table tracks videos uploaded to YouTube:

```sql
create table if not exists youtube (
  id uuid default uuid_generate_v4() primary key,
  song_id uuid references songs(id),
  youtube_id text unique,
  title text,
  description text,
  upload_date timestamp with time zone default now(),
  status text,
  view_count integer default 0,
  like_count integer default 0
);

-- Create index for faster lookups
create index if not exists youtube_song_id_idx on youtube(song_id);
create index if not exists youtube_youtube_id_idx on youtube(youtube_id);
create index if not exists youtube_status_idx on youtube(status);

-- Add comment to explain table purpose
comment on table youtube is 'Tracks videos uploaded to YouTube from the songs table';
```

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

## Test Scripts

### test_angus.py

Unit tests for Agent Angus using mocks to avoid making actual API calls.

**Test Cases**:
- `test_create_youtube_table`: Tests creating the YouTube table
- `test_get_songs_to_upload`: Tests getting songs to upload
- `test_upload_song_to_youtube`: Tests uploading a song to YouTube
- `test_fetch_comments`: Tests fetching comments for a video

### test_openai_response.py

Tests the OpenAI response generation without requiring YouTube integration.

**Usage**:
```bash
python test_openai_response.py
```

### test_youtube_reply.py

Tests the ability to reply to a specific YouTube comment.

**Usage**:
```bash
python test_youtube_reply.py --video-id VIDEO_ID [--comment-id COMMENT_ID]
```

### test_comment_response_flow.py

Tests the entire comment response flow from fetching comments to generating responses and posting replies.

**Usage**:
```bash
python test_comment_response_flow.py --video-id VIDEO_ID
```

### test_fetch_specific_video.py

Tests fetching comments for a specific video and checking if they have replies.

**Usage**:
```bash
python test_fetch_specific_video.py --video-id VIDEO_ID
```

### test_angus_specific_video.py

Tests running Angus on a specific video.

**Usage**:
```bash
python test_angus_specific_video.py --video-id VIDEO_ID
```

### Influence Music Table

The Influence Music table stores Sonoteller analysis results:

```sql
create table if not exists influence_music (
  id uuid default uuid_generate_v4() primary key,
  song_id uuid references songs(id),
  url text not null,
  analysis jsonb not null,
  created_at timestamp with time zone default now()
);

-- Create index for faster lookups
create index if not exists influence_music_song_id_idx on influence_music(song_id);

-- Add comment to explain table purpose
comment on table influence_music is 'Stores Sonoteller analysis results for influence music';
```

| Field Name      | Type        | Description                                  |
|----------------|------------|----------------------------------------------|
| `id` (PK)      | `uuid`      | Unique ID, primary key (auto-generated)     |
| `song_id`      | `uuid`      | Reference to songs table (optional)         |
| `url`          | `text`      | URL of the analyzed music file              |
| `analysis`     | `jsonb`     | JSON data with Sonoteller analysis results  |
| `created_at`   | `timestamp` | Timestamp of when the analysis was created  |

## Command-Line Interface

Agent Angus provides a command-line interface for various operations:

```bash
python angus.py [options]
```

**Options**:
- `--create-table`: Create the YouTube table in Supabase
- `--upload`: Upload pending songs to YouTube
- `--fetch-comments`: Fetch comments for uploaded videos
- `--limit N`: Limit the number of items to process (default: 1)
- `--max-replies N`: Maximum number of comment replies to post (default: 10)
- `--daemon`: Run in daemon mode with scheduled tasks
- `--web`: Run the web UI for Sonoteller analysis
- `--port N`: Port for the web UI (default: 5000)

**Examples**:

Create the YouTube table:
```bash
python angus.py --create-table
```

Upload pending songs to YouTube:
```bash
python angus.py --upload --limit 5
```

Fetch comments for uploaded videos:
```bash
python angus.py --fetch-comments --limit 10 --max-replies 10
```

Run in daemon mode with scheduled tasks:
```bash
python angus.py --daemon
```

Run the web UI for Sonoteller analysis:
```bash
python angus.py --web --port 8080
```

## Run Scripts

### run_angus.bat (Windows)

Batch script to run Agent Angus with common commands.

**Usage**:
```batch
run_angus.bat [command] [options]
```

**Commands**:
- `setup`: Create the YouTube table in Supabase
- `upload`: Upload pending songs to YouTube
- `comments`: Fetch comments for uploaded videos
- `daemon`: Run in daemon mode with scheduled tasks
- `web`: Run the web UI for Sonoteller analysis
- `test`: Run tests in simulation mode
- `help`: Show help message

**Options**:
- `--limit N`: Limit the number of items to process (default: 10)
- `--simulate`: Run in simulation mode without making actual API calls
- `--port N`: Port for the web UI (default: 5000)

**Examples**:
```batch
run_angus.bat setup
run_angus.bat upload --limit 5
run_angus.bat comments --limit 10
```

### run_angus.sh (Unix-based systems)

Shell script to run Agent Angus with common commands.

**Usage**:
```bash
./run_angus.sh [command] [options]
```

**Commands**:
- `setup`: Create the YouTube table in Supabase
- `upload`: Upload pending songs to YouTube
- `comments`: Fetch comments for uploaded videos
- `daemon`: Run in daemon mode with scheduled tasks
- `web`: Run the web UI for Sonoteller analysis
- `test`: Run tests in simulation mode
- `help`: Show help message

**Options**:
- `--limit N`: Limit the number of items to process (default: 10)
- `--simulate`: Run in simulation mode without making actual API calls
- `--port N`: Port for the web UI (default: 5000)

**Examples**:
```bash
./run_angus.sh setup
./run_angus.sh upload --limit 5
./run_angus.sh comments --limit 10
./run_angus.sh web --port 8080
