#!/usr/bin/env python3
"""
Agent Angus Coral Protocol Adapter

This module provides an adapter to integrate Agent Angus with the Coral Protocol server,
allowing all of Agent Angus's functionality to be accessible through the Coral Protocol.
"""
import os
import sys
import time
import logging
import json
import re
import threading
from typing import Dict, Any, List, Optional, Union

# Import Coral client
from coral_client import CoralClient

# Import Agent Angus
from angus import AgentAngus

# Import OpenAI utilities
from openai_utils import analyze_music, generate_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('angus_coral.log')
    ]
)
logger = logging.getLogger(__name__)

class AngusCoralAdapter:
    """
    Adapter to integrate Agent Angus with the Coral Protocol server.
    """
    
    def __init__(self, session_id="angus-agent", server_url="https://coral.pushcollective.club", use_devmode=True):
        """
        Initialize the Angus Coral Adapter.
        
        Args:
            session_id (str, optional): Unique session identifier. Defaults to "angus-agent".
            server_url (str, optional): Base URL of the Coral server. Defaults to "https://coral.pushcollective.club".
            use_devmode (bool, optional): Whether to use DevMode endpoints. Defaults to True.
        """
        # Initialize Agent Angus
        self.angus = AgentAngus()
        
        # Initialize Coral client with a consistent session ID
        self.coral_client = CoralClient(
            session_id=session_id,
            server_url=server_url,
            use_devmode=use_devmode
        )
        
        self.agent_id = None
        self.logger = logging.getLogger("angus_coral_adapter")
        self.threads = {}  # Store thread information
        self.yona_agent_id = "yona-agent"  # Yona's fixed agent ID
        
        self.logger.info(f"Angus Coral Adapter initialized with session ID: {session_id}")
    
    def register_agent(self):
        """
        Register Agent Angus with the Coral server.
        
        Returns:
            str: The agent ID assigned by the server, or None if registration failed.
        """
        self.logger.info("Registering Agent Angus with Coral server")
        
        self.agent_id = self.coral_client.register_agent(
            name="Agent Angus",
            description="An AI agent that automates YouTube publishing and audience feedback collection for AI-generated music videos."
        )
        
        if self.agent_id:
            self.logger.info(f"Agent Angus registered with ID: {self.agent_id}")
        else:
            self.logger.error("Failed to register Agent Angus with Coral server")
            
        return self.agent_id
    
    def create_thread_with_yona(self, metadata=None):
        """
        Create a thread with Yona.
        
        Args:
            metadata (dict, optional): Additional metadata for the thread. Defaults to None.
            
        Returns:
            str: The thread ID assigned by the server, or None if thread creation failed.
        """
        self.logger.info("Creating thread with Yona")
        
        if not self.agent_id:
            self.logger.error("Cannot create thread: Agent not registered")
            return None
        
        # Create a thread with both Angus and Yona
        thread_id = self.coral_client.create_thread(
            participants=[self.agent_id, self.yona_agent_id],
            metadata=metadata or {"topic": "Music Creation"}
        )
        
        if thread_id:
            self.logger.info(f"Thread created with ID: {thread_id}")
            self.threads[thread_id] = {
                "created_at": time.time(),
                "participants": [self.agent_id, self.yona_agent_id]
            }
        else:
            self.logger.error("Failed to create thread with Yona")
            
        return thread_id
    
    def send_message_to_yona(self, thread_id, content):
        """
        Send a message to Yona using multiple mention formats for maximum reliability.
        
        Args:
            thread_id (str): The ID of the thread to send the message to
            content (str): The content of the message
            
        Returns:
            str: The message ID assigned by the server, or None if sending failed
        """
        self.logger.info(f"Sending message to Yona in thread {thread_id}")
        
        # Ensure the content includes @mention format if not already present
        if not f"@{self.yona_agent_id}" in content:
            content = f"@{self.yona_agent_id} {content}"
        
        # Send the message with explicit mention in the API call
        message_id = self.coral_client.send_message(
            thread_id=thread_id,
            content=content,
            mentions=[self.yona_agent_id]  # Explicit mention in the API call
        )
        
        if message_id:
            self.logger.info(f"Message sent to Yona with ID: {message_id}")
        else:
            self.logger.error("Failed to send message to Yona")
            
        return message_id
    
    def upload_song_to_youtube(self, video_url, title, description, tags=None):
        """
        Upload a song to YouTube.
        
        Args:
            video_url (str): URL of the video file to upload
            title (str): Title of the video
            description (str): Description of the video
            tags (list, optional): List of tags for the video. Defaults to None.
            
        Returns:
            dict: Result of the upload operation
        """
        self.logger.info(f"Uploading song '{title}' to YouTube")
        
        try:
            # Create a song object
            song = {
                'title': title,
                'video_url': video_url,
                'gpt_description': description,
                'style': ','.join(tags) if tags else ''
            }
            
            # Upload to YouTube
            youtube_id = self.angus.upload_song_to_youtube(song)
            
            if youtube_id:
                self.logger.info(f"Successfully uploaded '{title}' to YouTube with ID: {youtube_id}")
                return {
                    'success': True,
                    'youtube_id': youtube_id,
                    'message': f"Successfully uploaded '{title}' to YouTube"
                }
            else:
                self.logger.error(f"Failed to upload '{title}' to YouTube")
                return {
                    'success': False,
                    'error': "Upload failed - no YouTube ID returned"
                }
                
        except Exception as e:
            self.logger.error(f"Error uploading song '{title}' to YouTube: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def fetch_comments(self, youtube_id, max_replies=None):
        """
        Fetch comments for a YouTube video.
        
        Args:
            youtube_id (str): YouTube video ID
            max_replies (int, optional): Maximum number of replies to post. Defaults to None.
            
        Returns:
            dict: Result of the fetch operation
        """
        self.logger.info(f"Fetching comments for YouTube video: {youtube_id}")
        
        try:
            # Fetch comments
            comments_count = self.angus.fetch_comments_for_video(youtube_id, max_replies=max_replies)
            
            self.logger.info(f"Fetched {comments_count} comments from YouTube video: {youtube_id}")
            return {
                'success': True,
                'comments_count': comments_count,
                'message': f"Fetched {comments_count} comments from YouTube video"
            }
        except Exception as e:
            self.logger.error(f"Error fetching comments for YouTube video {youtube_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def fetch_comments_for_all_videos(self, limit=10, max_total_replies=10):
        """
        Fetch comments for all uploaded YouTube videos.
        
        Args:
            limit (int, optional): Maximum number of videos to process. Defaults to 10.
            max_total_replies (int, optional): Maximum total number of replies to post. Defaults to 10.
            
        Returns:
            dict: Result of the fetch operation
        """
        self.logger.info(f"Fetching comments for all videos (limit: {limit}, max_replies: {max_total_replies})")
        
        try:
            # Fetch comments for all videos
            total_comments = self.angus.fetch_comments_for_all_videos(limit=limit, max_total_replies=max_total_replies)
            
            self.logger.info(f"Fetched a total of {total_comments} comments from videos")
            return {
                'success': True,
                'total_comments': total_comments,
                'message': f"Fetched a total of {total_comments} comments from videos"
            }
        except Exception as e:
            self.logger.error(f"Error fetching comments for all videos: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_all_pending_songs(self, limit=10):
        """
        Upload all pending songs to YouTube.
        
        Args:
            limit (int, optional): Maximum number of songs to upload. Defaults to 10.
            
        Returns:
            dict: Result of the upload operation
        """
        self.logger.info(f"Uploading pending songs (limit: {limit})")
        
        try:
            # Upload all pending songs
            successful_uploads = self.angus.upload_all_pending_songs(limit=limit)
            
            self.logger.info(f"Uploaded {successful_uploads} songs to YouTube")
            return {
                'success': True,
                'successful_uploads': successful_uploads,
                'message': f"Uploaded {successful_uploads} songs to YouTube"
            }
        except Exception as e:
            self.logger.error(f"Error uploading pending songs: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_music(self, input_source, is_youtube_url=False, model="gpt-4o"):
        """
        Analyze music using OpenAI.
        
        Args:
            input_source (str): Either a path to an MP3 file or a YouTube URL
            is_youtube_url (bool, optional): Whether the input_source is a YouTube URL. Defaults to False.
            model (str, optional): OpenAI model to use. Defaults to "gpt-4o".
            
        Returns:
            dict: Result of the analysis operation
        """
        self.logger.info(f"Analyzing music: {input_source}")
        
        try:
            # Analyze music
            analysis = analyze_music(input_source, is_youtube_url=is_youtube_url, model=model)
            
            if "error" in analysis:
                self.logger.error(f"Error analyzing music: {analysis['error']}")
                return {
                    'success': False,
                    'error': analysis['error'],
                    'details': analysis.get('details', '')
                }
            
            self.logger.info(f"Successfully analyzed music: {input_source}")
            return {
                'success': True,
                'analysis': analysis
            }
        except Exception as e:
            self.logger.error(f"Error analyzing music: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_comment_response(self, comment_text, song_title, song_style=None):
        """
        Generate a response to a YouTube comment using OpenAI.
        
        Args:
            comment_text (str): The text of the comment
            song_title (str): The title of the song
            song_style (str, optional): Optional style information about the song. Defaults to None.
            
        Returns:
            dict: Result of the response generation operation
        """
        self.logger.info(f"Generating response for comment: {comment_text[:30]}...")
        
        try:
            # Generate response
            response_text = generate_response(comment_text, song_title, song_style)
            
            if response_text:
                self.logger.info(f"Generated response: {response_text}")
                return {
                    'success': True,
                    'response': response_text
                }
            else:
                self.logger.error("Failed to generate response")
                return {
                    'success': False,
                    'error': "Failed to generate response"
                }
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_mentions(self, timeout_seconds=30):
        """
        Process mentions of Agent Angus.
        
        Args:
            timeout_seconds (int, optional): Maximum time to wait for mentions in seconds. Defaults to 30.
            
        Returns:
            list: List of responses to mentions
        """
        self.logger.info(f"Waiting for mentions of Agent Angus (timeout: {timeout_seconds}s)")
        
        mentions = self.coral_client.wait_for_mentions(
            self.agent_id,
            timeout_seconds=timeout_seconds
        )
        
        if not mentions:
            self.logger.info("No mentions received")
            return []
        
        self.logger.info(f"Received {len(mentions)} mentions")
        
        responses = []
        for mention in mentions:
            thread_id = mention.get("thread_id")
            content = mention.get("content")
            sender_id = mention.get("sender_id")
            
            self.logger.info(f"Processing mention in thread {thread_id}: {content[:50]}...")
            
            # Process the mention
            response = self._process_mention(thread_id, content, sender_id)
            responses.append(response)
        
        return responses
    
    def _process_mention(self, thread_id, content, sender_id):
        """
        Process a single mention.
        
        Args:
            thread_id (str): The ID of the thread
            content (str): The content of the mention
            sender_id (str): The ID of the sender
            
        Returns:
            dict: Result of processing the mention
        """
        # Parse the content to determine what action to take
        content_lower = content.lower()
        
        # Check for YouTube analysis request
        if "analyze" in content_lower and "youtube" in content_lower:
            # Extract YouTube URL
            youtube_url = re.search(r'(https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+)', content)
            if youtube_url:
                youtube_url = youtube_url.group(1)
                self.logger.info(f"Analyzing YouTube video: {youtube_url}")
                
                # Analyze the YouTube video
                result = self.analyze_music(youtube_url, is_youtube_url=True)
                
                if result.get('success'):
                    analysis = result.get('analysis', {})
                    
                    # Format the response
                    response = f"Analysis complete! Here's what I found:\n\n"
                    response += f"Title: {analysis.get('title', 'Unknown')}\n\n"
                    
                    # Add genres
                    genres = analysis.get('genres', [])
                    if genres:
                        response += "Genres:\n"
                        for genre in genres:
                            if isinstance(genre, dict) and "name" in genre and "weight" in genre:
                                response += f"- {genre['name']} ({genre['weight']}%)\n"
                            elif isinstance(genre, str):
                                response += f"- {genre}\n"
                        response += "\n"
                    
                    # Add moods
                    moods = analysis.get('moods', [])
                    if moods:
                        response += "Moods:\n"
                        for mood in moods:
                            if isinstance(mood, dict) and "name" in mood and "weight" in mood:
                                response += f"- {mood['name']} ({mood['weight']}%)\n"
                            elif isinstance(mood, str):
                                response += f"- {mood}\n"
                        response += "\n"
                    
                    # Add summary
                    if analysis.get('summary'):
                        response += f"Summary: {analysis['summary']}\n\n"
                    
                    # Send the response
                    self.coral_client.send_message(thread_id, response, [sender_id])
                    return {"success": True, "action": "analyze_youtube", "thread_id": thread_id}
                else:
                    # Send error response
                    error_message = f"Sorry, I couldn't analyze that YouTube video. Error: {result.get('error', 'Unknown error')}"
                    self.coral_client.send_message(thread_id, error_message, [sender_id])
                    return {"success": False, "action": "analyze_youtube", "error": result.get('error'), "thread_id": thread_id}
        
        # Check for upload request
        elif "upload" in content_lower and "youtube" in content_lower:
            # Extract video URL, title, and description
            video_url_match = re.search(r'url[:\s]+([^\s]+)', content_lower)
            title_match = re.search(r'title[:\s]+([^\n]+)', content)
            description_match = re.search(r'description[:\s]+([^\n]+)', content)
            
            if video_url_match and title_match:
                video_url = video_url_match.group(1)
                title = title_match.group(1)
                description = description_match.group(1) if description_match else ""
                
                self.logger.info(f"Uploading video to YouTube: {title}")
                
                # Upload the video
                result = self.upload_song_to_youtube(video_url, title, description)
                
                if result.get('success'):
                    # Send success response
                    success_message = f"Successfully uploaded '{title}' to YouTube with ID: {result.get('youtube_id')}"
                    self.coral_client.send_message(thread_id, success_message, [sender_id])
                    return {"success": True, "action": "upload_youtube", "thread_id": thread_id}
                else:
                    # Send error response
                    error_message = f"Sorry, I couldn't upload that video to YouTube. Error: {result.get('error', 'Unknown error')}"
                    self.coral_client.send_message(thread_id, error_message, [sender_id])
                    return {"success": False, "action": "upload_youtube", "error": result.get('error'), "thread_id": thread_id}
            else:
                # Send error response
                error_message = "To upload a video to YouTube, please provide a URL and title. For example: 'upload to youtube url: https://example.com/video.mp4 title: My Video description: This is my video'"
                self.coral_client.send_message(thread_id, error_message, [sender_id])
                return {"success": False, "action": "upload_youtube", "error": "Missing URL or title", "thread_id": thread_id}
        
        # Check for fetch comments request
        elif "fetch" in content_lower and "comments" in content_lower:
            # Extract YouTube ID
            youtube_id_match = re.search(r'id[:\s]+([^\s]+)', content_lower)
            
            if youtube_id_match:
                youtube_id = youtube_id_match.group(1)
                
                self.logger.info(f"Fetching comments for YouTube video: {youtube_id}")
                
                # Fetch comments
                result = self.fetch_comments(youtube_id)
                
                if result.get('success'):
                    # Send success response
                    success_message = f"Fetched {result.get('comments_count')} comments from YouTube video: {youtube_id}"
                    self.coral_client.send_message(thread_id, success_message, [sender_id])
                    return {"success": True, "action": "fetch_comments", "thread_id": thread_id}
                else:
                    # Send error response
                    error_message = f"Sorry, I couldn't fetch comments for that YouTube video. Error: {result.get('error', 'Unknown error')}"
                    self.coral_client.send_message(thread_id, error_message, [sender_id])
                    return {"success": False, "action": "fetch_comments", "error": result.get('error'), "thread_id": thread_id}
            else:
                # Send error response
                error_message = "To fetch comments for a YouTube video, please provide the YouTube ID. For example: 'fetch comments for id: dQw4w9WgXcQ'"
                self.coral_client.send_message(thread_id, error_message, [sender_id])
                return {"success": False, "action": "fetch_comments", "error": "Missing YouTube ID", "thread_id": thread_id}
        
        # Default response for unrecognized commands
        help_message = "I'm Agent Angus! I can help with:\n\n"
        help_message += "1. Analyzing YouTube music videos:\n"
        help_message += "   Example: 'analyze this YouTube video: https://youtube.com/watch?v=dQw4w9WgXcQ'\n\n"
        help_message += "2. Uploading videos to YouTube:\n"
        help_message += "   Example: 'upload to youtube url: https://example.com/video.mp4 title: My Video description: This is my video'\n\n"
        help_message += "3. Fetching YouTube comments:\n"
        help_message += "   Example: 'fetch comments for id: dQw4w9WgXcQ'\n\n"
        help_message += "What would you like me to do?"
        
        self.coral_client.send_message(thread_id, help_message, [sender_id])
        return {"success": True, "action": "help", "thread_id": thread_id}

    def handle_yona_response(self, data):
        """
        Handle responses from Yona.
        
        Args:
            data (dict): The message data
            
        Returns:
            bool: True if the message was handled, False otherwise
        """
        sender_id = data.get('sender_id')
        content = data.get('content', '')
        thread_id = data.get('thread_id')
        
        # Check if the message is from Yona
        if sender_id != self.yona_agent_id:
            return False
        
        self.logger.info(f"Received message from Yona in thread {thread_id}")
        
        # Check if Yona created a song
        if "Created song" in content:
            self.logger.info("Yona created a song!")
            
            # Extract song information
            lines = content.split('\n')
            song_info = {
                "title": lines[0].replace("Created song '", "").replace("'", ""),
                "audio_url": next((line.replace("Audio: ", "") for line in lines if line.startswith("Audio: ")), None),
                "lyrics": '\n'.join(lines[3:]) if len(lines) > 3 else ""
            }
            
            self.logger.info(f"Song information: {json.dumps(song_info, indent=2)}")
            
            # Send a thank you message
            thank_you = f"Thanks for creating '{song_info['title']}'! It sounds great!"
            self.send_message_to_yona(thread_id, thank_you)
            
            return True
        
        return False

def main():
    """
    Main entry point for the Angus Coral Adapter.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting Angus Coral Adapter")
    
    # Create the adapter with a consistent session ID
    adapter = AngusCoralAdapter(session_id="angus-agent", use_devmode=True)
    
    # Register the agent
    agent_id = adapter.register_agent()
    logger.info(f"Agent registered with ID: {agent_id}")
    
    # Define event handlers
    def handle_tool_call(data):
        logger.info(f"Received tool call: {json.dumps(data, indent=2)}")
        # Process tool calls here
        # This would be expanded to handle specific tool calls
    
    def handle_message(data):
        logger.info(f"Received message: {json.dumps(data, indent=2)}")
        
        # Check if the message is from Yona and handle it
        if adapter.handle_yona_response(data):
            logger.info("Message from Yona was handled")
        else:
            # Process other messages here
            pass
    
    # Start listening for events
    adapter.coral_client.start_listening({
        "tool_call": handle_tool_call,
        "message": handle_message
    })
    
    logger.info("Listening for events")
    
    # Run in continuous mode with improved reconnection logic
    try:
        retries = 0
        max_retries = 5
        while True:
            try:
                # Process mentions
                adapter.process_mentions(timeout_seconds=30)
                retries = 0  # Reset retries on success
                time.sleep(1)
            except Exception as e:
                retries += 1
                logger.error(f"Error processing mentions: {str(e)}, retry {retries}/{max_retries}")
                # Exponential backoff
                sleep_time = min(30, 5 * retries)
                logger.info(f"Waiting {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)
                
                # If we've reached max retries, try to reconnect
                if retries >= max_retries:
                    logger.info("Max retries reached, attempting to reconnect...")
                    try:
                        # Re-register the agent
                        adapter.register_agent()
                        retries = 0
                    except Exception as reconnect_error:
                        logger.error(f"Error reconnecting: {str(reconnect_error)}")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")

if __name__ == "__main__":
    main()
