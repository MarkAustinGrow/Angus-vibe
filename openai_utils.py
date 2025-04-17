"""
OpenAI utilities for Agent Angus.

This module provides functions for generating responses and analyzing music using OpenAI.
"""
import os
import json
import logging
from openai import OpenAI
from typing import Optional, Dict, Any, Union

# Import configuration
from config import OPENAI_API_KEY

# Import YouTube audio extractor
from youtube_audio_extractor import YouTubeAudioExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_music(input_source: str, is_youtube_url: bool = False) -> Dict[str, Any]:
    """
    Analyze music using OpenAI.
    
    Args:
        input_source: Either a path to an MP3 file or a YouTube URL
        is_youtube_url: Whether the input_source is a YouTube URL
        
    Returns:
        Dictionary with analysis results
    """
    try:
        # If it's a YouTube URL, extract the audio first
        if is_youtube_url:
            logger.info(f"Extracting audio from YouTube URL: {input_source}")
            extractor = YouTubeAudioExtractor()
            mp3_path = extractor.extract_audio(input_source)
            # Get video title for better analysis
            from pytube import YouTube
            yt = YouTube(input_source)
            title = yt.title
            description = yt.description
        else:
            mp3_path = input_source
            # For uploaded files, we have limited info
            title = os.path.basename(mp3_path)
            description = ''
            
        logger.info(f"Analyzing music: {title}")
            
        # Create a prompt for OpenAI to analyze the music based on metadata
        prompt = f"""
        Analyze the following music track:
        
        Title: {title}
        Description: {description}
        
        Please provide a detailed analysis including:
        1. Lyrics analysis (themes, moods, language, explicit content)
        2. Music analysis (genres, subgenres, instruments, BPM, key)
        
        Format the response as a structured JSON object with these sections:
        {{
            "lyrics_analysis": {{
                "summary": "Brief summary of the lyrics",
                "themes": ["theme1", "theme2"],
                "moods": ["mood1", "mood2"],
                "language": "Language of the lyrics",
                "explicit": "Yes/No and explanation"
            }},
            "music_analysis": {{
                "genres": ["genre1", "genre2"],
                "subgenres": ["subgenre1", "subgenre2"],
                "instruments": ["instrument1", "instrument2"],
                "bpm": "Estimated BPM",
                "key": "Estimated key",
                "vocals": "Description of vocals"
            }}
        }}
        """
        
        # Send to OpenAI
        response = client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for better analysis
            messages=[
                {"role": "system", "content": "You are a music analysis expert. Provide detailed analysis of music tracks in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        analysis_text = response.choices[0].message.content.strip()
        analysis = json.loads(analysis_text)
        
        # Clean up temporary files if needed
        if is_youtube_url and 'mp3_path' in locals():
            try:
                os.remove(mp3_path)
                logger.info(f"Removed temporary file: {mp3_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {str(e)}")
                
        # Format the analysis to match the expected structure
        formatted_analysis = {
            "summary": analysis.get("lyrics_analysis", {}).get("summary", ""),
            "themes": analysis.get("lyrics_analysis", {}).get("themes", []),
            "moods": analysis.get("lyrics_analysis", {}).get("moods", []),
            "language": analysis.get("lyrics_analysis", {}).get("language", ""),
            "explicit": analysis.get("lyrics_analysis", {}).get("explicit", ""),
            "genres": analysis.get("music_analysis", {}).get("genres", []),
            "subgenres": analysis.get("music_analysis", {}).get("subgenres", []),
            "instruments": analysis.get("music_analysis", {}).get("instruments", []),
            "bpm": analysis.get("music_analysis", {}).get("bpm", ""),
            "key": analysis.get("music_analysis", {}).get("key", ""),
            "vocals": analysis.get("music_analysis", {}).get("vocals", ""),
            # Add DDEX format for compatibility with existing code
            "ddex moods": analysis.get("lyrics_analysis", {}).get("moods", []),
            "ddex themes": analysis.get("lyrics_analysis", {}).get("themes", [])
        }
        
        return formatted_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing music: {str(e)}")
        return {
            "error": "Error analyzing music",
            "details": str(e)
        }

def generate_response(comment_text: str, song_title: str, song_style: Optional[str] = None) -> Optional[str]:
    """
    Generate a response to a YouTube comment using OpenAI.
    
    Args:
        comment_text: The text of the comment
        song_title: The title of the song
        song_style: Optional style information about the song
        
    Returns:
        Generated response text
    """
    try:
        # Create a system prompt that includes context about the song
        system_prompt = f"You are a friendly assistant responding to comments on a music video for the song '{song_title}'"
        if song_style:
            system_prompt += f" which is in the style of {song_style}."
        system_prompt += " Keep responses brief (max 2 sentences), friendly, and engaging. Thank the user for their feedback."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Someone commented: '{comment_text}'. Write a brief, friendly response."}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        reply_text = response.choices[0].message.content.strip()
        logger.info(f"Generated response for comment: {reply_text}")
        return reply_text
        
    except Exception as e:
        logger.error(f"Error generating response with OpenAI: {str(e)}")
        return None
