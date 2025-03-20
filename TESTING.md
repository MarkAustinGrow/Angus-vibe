# Testing the OpenAI Comment Response Feature

This document provides instructions for testing the OpenAI comment response feature in Agent Angus.

## Prerequisites

Before testing, ensure you have:

1. Set up the required environment variables in your `.env` file:
   ```
   OPENAI_API_KEY=your-openai-api-key
   YOUTUBE_CHANNEL_ID=your-youtube-channel-id
   ```

2. Installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Test Scripts

We've provided several test scripts to verify different aspects of the feature:

### 1. Test OpenAI Response Generation

This script tests the OpenAI response generation without requiring YouTube integration:

```bash
python test_openai_response.py
```

Expected output:
```
INFO:__main__:Testing OpenAI response generation for comment: 'This song is amazing! I love the beat and the lyrics are so meaningful.'
INFO:__main__:Song title: 'Cosmic Dreams'
INFO:__main__:Song style: 'Electronic, Ambient'
INFO:openai_utils:Generated response for comment: [OpenAI's response will appear here]
INFO:__main__:Successfully generated response: '[OpenAI's response will appear here]'
```

### 2. Test YouTube Comment Reply

This script tests the ability to reply to a specific YouTube comment:

```bash
python test_youtube_reply.py --video-id VIDEO_ID
```

Replace `VIDEO_ID` with an actual YouTube video ID that has comments.

You can also specify a particular comment to reply to:

```bash
python test_youtube_reply.py --video-id VIDEO_ID --comment-id COMMENT_ID
```

### 3. Test Complete Comment Response Flow

This script tests the entire flow from fetching comments to generating responses and posting replies:

```bash
python test_comment_response_flow.py --video-id VIDEO_ID
```

Replace `VIDEO_ID` with an actual YouTube video ID that has comments.

### 4. Test with Agent Angus

To test the feature with the main Agent Angus script:

```bash
python angus.py --fetch-comments --limit 1
```

This will fetch comments from one video and attempt to reply to any new comments.

## Troubleshooting

If you encounter issues:

1. **OpenAI API errors**:
   - Check that your OpenAI API key is valid
   - Verify you have sufficient credits in your OpenAI account
   - Check the OpenAI API status at https://status.openai.com/

2. **YouTube API errors**:
   - Ensure your YouTube OAuth credentials are valid
   - Verify your YouTube channel ID is correct
   - Check that you have the necessary permissions to post comments

3. **"Already replied" messages**:
   - This is normal if you've already replied to all comments
   - Try testing with a different video that has new comments

4. **No comments found**:
   - Verify the video ID is correct
   - Ensure the video has public comments enabled

## Finding Video and Comment IDs

### Video ID

The video ID is the part of the YouTube URL after `v=`:
```
https://www.youtube.com/watch?v=VIDEO_ID
```

### Comment ID

Comment IDs are more difficult to find directly. The easiest way is to:

1. Run the test script with just the video ID:
   ```bash
   python test_youtube_reply.py --video-id VIDEO_ID
   ```

2. Look for the comment IDs in the output:
   ```
   INFO:__main__:Found X comments
   INFO:__main__:Selected comment: 'Comment text'
   ```

3. Use the browser developer tools to inspect the comment element on YouTube, which may contain the comment ID in the data attributes.
