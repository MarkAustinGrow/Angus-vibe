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

##### Method: `cleanup_old_logs`

```python
def cleanup_old_logs(self, days_to_keep=7) -> int
```

**Description**: Remove logs older than the specified number of days.

**Parameters**:
- `days_to_keep` (int, optional): Number of days of logs to keep. Defaults to 7.

**Returns**:
- `int`: Number of logs deleted

**Example**:
```python
deleted_count = angus.cleanup_old_logs(days_to_keep=14)
print(f"Deleted {deleted_count} old logs")
```

**Error Handling**: Returns 0 if an error occurs during the cleanup operation.

##### Method: `run_scheduled_tasks`

```python
def run_scheduled_tasks(self)
```

**Description**: Runs scheduled tasks continuously. This method sets up scheduled tasks to run at specified intervals: upload videos to YouTube every hour, fetch comments from YouTube videos every hour, and clean up old logs every day. The method runs indefinitely until interrupted.

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

##### Method: `create_storage_bucket`

```python
def create_storage_bucket(self, bucket_name: str, is_public: bool = True) -> bool
```

**Description**: Create a storage bucket if it doesn't exist.

**Parameters**:
- `bucket_name` (str): Name of the bucket to create
- `is_public` (bool, optional): Whether the bucket should be public. Defaults to True.

**Returns**:
- `bool`: True if the bucket was created or already exists, False otherwise

**Example**:
```python
success = supabase.create_storage_bucket('uploads', is_public=True)
if success:
    print("Storage bucket created successfully")
else:
    print("Failed to create storage bucket")
```

**Error Handling**: Returns False if an error occurs during bucket creation.

##### Method: `upload_file_to_storage`

```python
def upload_file_to_storage(self, bucket_name: str, file_path: str, file_name: Optional[str] = None) -> Optional[str]
```

**Description**: Upload a file to a storage bucket.

**Parameters**:
- `bucket_name` (str): Name of the bucket to upload to
- `file_path` (str): Path to the file to upload
- `file_name` (Optional[str]): Name to use for the file in storage (defaults to basename of file_path)

**Returns**:
- `Optional[str]`: Public URL of the uploaded file, or None if upload failed

**Example**:
```python
url = supabase.upload_file_to_storage('uploads', '/path/to/file.mp3')
if url:
    print(f"File uploaded to: {url}")
else:
    print("Failed to upload file")
```

**Error Handling**: Returns None if an error occurs during file upload.

##### Method: `delete_file_from_storage`

```python
def delete_file_from_storage(self, bucket_name: str, file_name: str) -> bool
```

**Description**: Delete a file from a storage bucket.

**Parameters**:
- `bucket_name` (str): Name of the bucket containing the file
- `file_name` (str): Name of the file to delete

**Returns**:
- `bool`: True if the file was deleted, False otherwise

**Example**:
```python
success = supabase.delete_file_from_storage('uploads', 'file.mp3')
if success:
    print("File deleted successfully")
else:
    print("Failed to delete file")
```

**Error Handling**: Returns False if an error occurs during file deletion.

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

The `openai_utils.py` module provides functions for generating responses using OpenAI and analyzing music.

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

#### Function: `analyze_music`

```python
def analyze_music(input_source: str, is_youtube_url: bool = False, model: str = "gpt-4o") -> Dict[str, Any]
```

**Description**: Analyze music using OpenAI. This function can analyze both YouTube videos and MP3 files, and generates detailed analysis including lyrics analysis, music analysis, and music creation parameters for the Nuro API.

**Parameters**:
- `input_source` (str): Either a path to an MP3 file or a YouTube URL
- `is_youtube_url` (bool, optional): Whether the input_source is a YouTube URL. Defaults to False.
- `model` (str, optional): OpenAI model to use. Defaults to "gpt-4o".

**Returns**:
- `Dict[str, Any]`: Dictionary with analysis results, including:
  - `summary`: Brief summary of the lyrics
  - `themes`: List of themes in the lyrics
  - `moods`: List of moods in the lyrics
  - `language`: Language of the lyrics
  - `explicit`: Whether the lyrics contain explicit content
  - `genres`: List of music genres
  - `subgenres`: List of music subgenres
  - `instruments`: List of instruments used
  - `bpm`: Beats per minute
  - `key`: Musical key
  - `vocals`: Description of vocals
  - `music_creation_params`: Parameters for the Nuro music creation API

**Example**:
```python
# Analyze a YouTube video
analysis = analyze_music("https://www.youtube.com/watch?v=VIDEO_ID", is_youtube_url=True)

# Analyze an MP3 file
analysis = analyze_music("/path/to/file.mp3")

# Use a different model
analysis = analyze_music("https://www.youtube.com/watch?v=VIDEO_ID", is_youtube_url=True, model="gpt-4")

if analysis:
    print(f"Summary: {analysis['summary']}")
    print(f"Genres: {', '.join(analysis['genres'])}")
    
    # Access music creation parameters
    if 'music_creation_params' in analysis:
        params = analysis['music_creation_params']
        print(f"Lyrics for music creation: {params['lyrics'][:100]}...")
        print(f"Genre: {params['genre']}")
        print(f"Mood: {params['mood']}")
        print(f"Timbre: {params['timbre']}")
        print(f"Duration: {params['duration']} seconds")
```

**Error Handling**:
- Returns detailed error information if the API call fails
- Handles JSON parsing errors by attempting to extract valid JSON from the response
- Provides fallback values for music creation parameters if not specified by OpenAI

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
def analyze_music(self, file_url: str, endpoint: str = "lyrics_ddex") -> Optional[Dict[str, Any]]
```

**Description**: Analyze a music file using the Sonoteller API.

**Parameters**:
- `file_url` (str): URL of the music file to analyze (.mp3 only)
- `endpoint` (str, optional): API endpoint to use. Options: "lyrics_ddex" (default), "music_ddex", "lyrics", "music". Defaults to "lyrics_ddex".

**Returns**:
- `Optional[Dict[str, Any]]`: Dictionary with analysis results, or None if an error occurs

**Example**:
```python
# Analyze an MP3 file
analysis = sonoteller.analyze_music("https://example.com/song.mp3")

# Analyze using the music_ddex endpoint
analysis = sonoteller.analyze_music(
    "https://example.com/song.mp3",
    endpoint="music_ddex"
)

if analysis:
    print(f"Language: {analysis.get('language')}")
    print(f"Summary: {analysis.get('summary')}")
    
    # Handle both list and dictionary formats for moods
    if isinstance(analysis.get('ddex moods'), list):
        print(f"Moods: {', '.join(analysis['ddex moods'])}")
    else:
        print(f"Moods: {', '.join(analysis['ddex moods'].values())}")
else:
    print("Failed to analyze music")
```

**Error Handling**:
- Validates that the URL is an MP3 file
- Supports multiple Sonoteller API endpoints
- Makes HTTP requests to the Sonoteller API
- Properly handles API response status codes and error messages
- Returns detailed error information if the API call fails, including:
  - Error message
  - Error details
  - Raw API response (when available)

**Note**: The Sonoteller API works best with direct MP3 file URLs. For YouTube videos or other formats, you can use the YouTubeAudioExtractor to convert them to MP3 format first.

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

#### Route: `/upload`

**Description**: Upload a file and return its URL.

**Method**: POST

**Parameters**:
- `file`: The file to upload (must be an MP3 file)

**Returns**: JSON response with the uploaded file URL.

**Error Handling**:
- Returns a 400 error if no file is provided
- Returns a 400 error if the file is not an MP3
- Generates a unique filename to avoid conflicts

#### Route: `/analyze`

**Description**: Analyzes a music file using OpenAI.

**Method**: POST

**Parameters**:
- `url` (str): URL of the music file to analyze (.mp3)
- `model` (str, optional): OpenAI model to use. Defaults to "gpt-4o".
- `song_id` (str, optional): Optional song ID to associate with the analysis

**Returns**: JSON response with analysis results and music creation parameters.

**Example Response**:
```json
{
  "success": true,
  "analysis": {
    "summary": "Brief summary of the lyrics",
    "themes": ["theme1", "theme2"],
    "moods": ["mood1", "mood2"],
    "language": "English",
    "explicit": "No",
    "genres": ["Pop", "Electronic"],
    "subgenres": ["Synth-pop", "Future Bass"],
    "instruments": ["Synthesizer", "Drums", "Vocals"],
    "bpm": "120",
    "key": "C Major",
    "vocals": "Female vocals with harmonies"
  },
  "music_creation_params": {
    "type": "vocal",
    "lyrics": "Sample lyrics for music creation...",
    "gender": "Female",
    "genre": "Pop",
    "mood": "Happy",
    "timbre": "Bright",
    "duration": 120
  },
  "id": "uuid-of-saved-record"
}
```

**Error Handling**:
- Returns a 400 error if no URL is provided
- Returns a 400 error if the URL is not an MP3
- Returns a 500 error if the analysis fails
- Stores the analysis in the influence_music table in Supabase
- Extracts music_creation_params from the analysis result and includes them in the response

#### Route: `/analyze_youtube`

**Description**: Analyzes a YouTube video using OpenAI.

**Method**: POST

**Parameters**:
- `url` (str): URL of the YouTube video to analyze
- `model` (str, optional): OpenAI model to use. Defaults to "gpt-4o".
- `song_id` (str, optional): Optional song ID to associate with the analysis

**Returns**: JSON response with analysis results and music creation parameters.

**Error Handling**:
- Returns a 400 error if no URL is provided
- Returns a 400 error if the URL is not a valid YouTube URL
- Returns a 500 error if the analysis fails
- Stores the analysis in the influence_music table in Supabase
- Extracts music_creation_params from the analysis result and includes them in the response

#### Route: `/save_parsed_analysis`

**Description**: Save parsed Sonoteller analysis to the database.

**Method**: POST

**Parameters**:
- `analysis` (Dict): The analysis data to save
- `url` (str, optional): URL of the analyzed music file
- `song_id` (str, optional): Optional song ID to associate with the analysis

**Returns**: JSON response with the saved analysis ID.

**Error Handling**:
- Returns a 400 error if no analysis is provided
- Returns a 500 error if saving fails

### 7. YouTube Audio Extractor (youtube_audio_extractor.py)

The `YouTubeAudioExtractor` class provides functionality to extract audio from YouTube videos for analysis with the Sonoteller API.

#### Class: `YouTubeAudioExtractor`

##### Constructor

```python
def __init__(self, temp_dir: Optional[str] = None)
```

**Description**: Initializes the YouTube audio extractor.

**Parameters**:
- `temp_dir` (Optional[str]): Optional directory to store temporary files. If not provided, system temp directory will be used.

**Returns**: None

**Example**:
```python
# Using system temp directory
extractor = YouTubeAudioExtractor()

# Using custom temp directory
extractor = YouTubeAudioExtractor(temp_dir="/path/to/temp")
```

##### Method: `extract_audio`

```python
def extract_audio(self, youtube_url: str) -> str
```

**Description**: Extract audio from a YouTube video and save as MP3.

**Parameters**:
- `youtube_url` (str): URL of the YouTube video

**Returns**:
- `str`: Path to the extracted MP3 file

**Example**:
```python
mp3_path = extractor.extract_audio("https://www.youtube.com/watch?v=VIDEO_ID")
print(f"Audio extracted to: {mp3_path}")
```

**Error Handling**:
- Uses pytube to download the highest quality audio stream
- Converts the downloaded file to MP3 format
- Provides detailed error information if the download fails

##### Method: `get_file_url`

```python
def get_file_url(self, file_path: str) -> str
```

**Description**: Convert a local file path to a file:// URL.

**Parameters**:
- `file_path` (str): Path to the local file

**Returns**:
- `str`: file:// URL for the local file

**Example**:
```python
file_url = extractor.get_file_url("/path/to/file.mp3")
print(f"File URL: {file_url}")
```

##### Method: `cleanup`

```python
def cleanup(self, file_path: str) -> None
```

**Description**: Clean up a temporary file.

**Parameters**:
- `file_path` (str): Path to the file to clean up

**Returns**: None

**Example**:
```python
extractor.cleanup("/path/to/temp/file.mp3")
```

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

## Test Scripts

### test_angus.py
Unit tests for Agent Angus using mocks to avoid making actual API calls.
