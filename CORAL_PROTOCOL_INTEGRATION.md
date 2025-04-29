# Agent Angus Coral Protocol Integration

This document provides instructions for integrating Agent Angus with the Coral Protocol server, allowing all of Agent Angus's functionality to be accessible through the Coral Protocol.

## Overview

The Coral Protocol integration allows Agent Angus to:

1. Register as an agent on the Coral Protocol server
2. Listen for mentions and process requests
3. Expose its functionality as tools that can be called through the Coral Protocol

The integration is implemented through the `AngusCoralAdapter` class, which bridges Agent Angus with the Coral Protocol server.

## Features

The following Agent Angus features are available through the Coral Protocol:

1. **YouTube Video Upload**: Upload videos to YouTube
2. **YouTube Comment Fetching**: Fetch comments from YouTube videos
3. **YouTube Comment Responses**: Generate and post responses to YouTube comments
4. **Music Analysis**: Analyze music using OpenAI

## Installation

No additional installation is required beyond the standard Agent Angus dependencies. The integration uses the `coral_client.py` file that is included in the repository.

## Usage

### Starting the Integration

#### On Windows:

```
run_angus_coral.bat
```

#### On Unix/Linux:

```
chmod +x run_angus_coral.sh
./run_angus_coral.sh
```

### Interacting with Agent Angus through Coral Protocol

Once the integration is running, you can interact with Agent Angus through the Coral Protocol server by mentioning it in a thread. Here are some example commands:

#### Analyzing a YouTube Video:

```
@Agent Angus analyze this YouTube video: https://youtube.com/watch?v=dQw4w9WgXcQ
```

#### Uploading a Video to YouTube:

```
@Agent Angus upload to youtube url: https://example.com/video.mp4 title: My Video description: This is my video
```

#### Fetching Comments from a YouTube Video:

```
@Agent Angus fetch comments for id: dQw4w9WgXcQ
```

## Configuration

The integration can be configured by modifying the parameters in the `AngusCoralAdapter` constructor:

```python
adapter = AngusCoralAdapter(
    session_id="custom-session-id",  # Optional custom session ID
    server_url="https://your-coral-server.com",  # Custom Coral server URL
    use_devmode=True  # Whether to use DevMode endpoints
)
```

## Troubleshooting

### Common Issues

#### Connection Errors

If you encounter connection errors to the Coral Protocol server:

1. Verify that the server URL is correct
2. Check that the server is running
3. Try using the `use_devmode=True` parameter
4. Check network connectivity

#### Agent Registration Failures

If Agent Angus fails to register with the Coral Protocol server:

1. Check the logs for error messages
2. Verify that the Coral Protocol server is accepting new agent registrations
3. Try using a different session ID

#### Message Processing Errors

If Agent Angus fails to process messages or mentions:

1. Check the logs for error messages
2. Verify that the agent ID is correct
3. Verify that the transport session ID is correct
4. Check that the Coral Protocol server is sending messages correctly

## Extending the Integration

To add new functionality to the integration:

1. Add new methods to the `AngusCoralAdapter` class
2. Update the `_process_mention` method to handle new commands
3. Update the help message to include the new commands

## License

This integration is licensed under the same license as Agent Angus.
