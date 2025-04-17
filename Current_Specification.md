# Agent Angus - Current Specification

## Overview

Agent Angus is an AI-powered automation system for YouTube publishing and audience engagement for AI-generated music videos. It serves as a bridge between content stored in Supabase and the YouTube platform, handling the entire workflow from video upload to audience interaction.

## Key Features

### 1. YouTube Publishing Automation

- **Automated Video Uploads**: Automatically uploads songs from the Supabase database to YouTube
- **Upload Queue Management**: Manages a queue of pending uploads with configurable limits
- **Upload Failure Handling**: Detects and handles YouTube upload limits and other failures
- **Video Metadata Management**: Generates and applies appropriate titles, descriptions, and tags for uploaded videos

### 2. Audience Engagement

- **Comment Monitoring**: Automatically fetches and stores comments from uploaded YouTube videos
- **AI-Powered Responses**: Generates contextually relevant responses to YouTube comments using OpenAI
- **Response Management**: Configurable limits for comment replies with fair distribution across videos
- **Engagement Tracking**: Stores all comments and responses in the database for analysis

### 3. Music Analysis

- **OpenAI API Integration**: Analyzes music files to extract insights about lyrics, mood, themes, and musical characteristics
- **Comprehensive Analysis**: Generates detailed analysis of lyrics, musical elements, and suggested music creation parameters
- **Analysis Storage**: Stores analysis results in the Supabase database for future reference
- **YouTube Audio Extraction**: Can extract audio from YouTube videos for analysis

### 4. Web Interface

- **Music Analysis UI**: Web interface for analyzing music using the OpenAI API
- **File Upload Support**: Allows uploading MP3 files for analysis
- **URL-based Analysis**: Supports analysis of music files via direct URLs
- **Analysis Visualization**: Displays analysis results in a user-friendly format
- **Database Integration**: Saves analysis results to the Supabase database

### 5. Scheduled Operations

- **Daemon Mode**: Runs continuously with scheduled tasks for uploads and comment retrieval
- **Configurable Scheduling**: Hourly tasks for video uploads and comment fetching
- **Log Management**: Automatic cleanup of old logs with configurable retention period

## Technical Specifications

### Database Schema

#### YouTube Table
Tracks videos uploaded to YouTube with the following fields:
- Video ID and metadata
- Upload status and timestamp
- View and like counts

#### Influence Music Table
Stores music analysis results with the following fields:
- Reference to the song
- URL of the analyzed file
- Complete analysis data in JSON format
- Creation timestamp

### API Integrations

- **YouTube API**: OAuth 2.0 authentication for video uploads, comment retrieval, and comment replies
- **OpenAI API**: For generating contextual responses to YouTube comments and comprehensive music analysis

### Command-Line Interface

Comprehensive CLI with options for:
- Creating database tables
- Uploading videos
- Fetching and responding to comments
- Running in daemon mode
- Starting the web UI
- Setting limits for operations

### Deployment Options

- **Docker Support**: Containerized deployment with Docker and docker-compose
- **Environment Configuration**: Configurable through environment variables
- **Cross-Platform Support**: Windows batch files and Unix shell scripts for easy execution

## User Interfaces

### Web UI

- **Analysis Form**: Input form for music URL or file upload
- **Analysis Type Selection**: Dropdown for selecting the type of analysis
- **Results Display**: Formatted display of analysis results including:
  - Language detection
  - Lyrics summary
  - Mood analysis
  - Theme identification
  - Genre classification
  - Musical characteristics (BPM, key, etc.)
- **Raw JSON View**: Option to view the complete analysis data

### Command-Line Interface

- **Interactive Mode**: Direct command execution with immediate feedback
- **Daemon Mode**: Background operation with scheduled tasks
- **Test Mode**: Simulation mode for testing without making actual API calls

## Operational Modes

### Standard Mode

- Manual execution of specific tasks through command-line arguments
- Configurable limits for number of items to process
- Detailed logging of operations

### Daemon Mode

- Continuous operation with scheduled tasks
- Hourly video uploads (limited to avoid YouTube restrictions)
- Hourly comment fetching and response generation
- Daily log cleanup

### Web UI Mode

- Interactive web interface for music analysis
- File upload and URL-based analysis
- Results visualization and storage

## Integration Points

### Supabase Integration

- Reads song data from the songs table
- Stores video information in the youtube table
- Stores comments in the feedback table
- Stores music analysis in the influence_music table
- Supports file storage for uploaded audio files

### YouTube Integration

- OAuth 2.0 authentication for secure API access
- Video upload with metadata
- Comment retrieval and filtering
- Comment reply posting

### OpenAI Integration

- Contextual response generation for YouTube comments
- Comprehensive music analysis including lyrics, genre, mood, and musical characteristics
- Generation of music creation parameters for potential integration with music generation APIs
- Support for both YouTube URLs and direct MP3 files
- Customizable system prompts based on song information
- Detailed error reporting for API failures
