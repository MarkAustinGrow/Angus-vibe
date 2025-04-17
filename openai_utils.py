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

def analyze_music(input_source: str, is_youtube_url: bool = False, model: str = "gpt-4o") -> Dict[str, Any]:
    """
    Analyze music using OpenAI.
    
    Args:
        input_source: Either a path to an MP3 file or a YouTube URL
        is_youtube_url: Whether the input_source is a YouTube URL
        model: OpenAI model to use (default: gpt-4o)
        
    Returns:
        Dictionary with analysis results
    """
    try:
        # Prepare the prompt based on the input type
        if is_youtube_url:
            logger.info(f"Analyzing YouTube URL: {input_source} with model {model}")
            
            # Create a prompt for OpenAI to analyze the YouTube video
            prompt = f"""
            Analyze the music in this YouTube video:
            
            YouTube URL: {input_source}
            
            Please provide a detailed analysis of the music in this video including:
            1. Lyrics analysis (themes, moods, language, explicit content)
            2. Music analysis (genres, subgenres, instruments, BPM, key)
            
            Your response MUST be a valid JSON object with this exact structure:
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
            
            Do not include any text outside of the JSON structure. Your entire response should be valid JSON.
            """
        else:
            # For MP3 files, we have limited info
            title = os.path.basename(input_source)
            logger.info(f"Analyzing MP3 file: {title} with model {model}")
            
            # Create a prompt for OpenAI to analyze the MP3 file
            prompt = f"""
            Analyze the following music track:
            
            Filename: {title}
            
            Please provide a detailed analysis including:
            1. Lyrics analysis (themes, moods, language, explicit content)
            2. Music analysis (genres, subgenres, instruments, BPM, key)
            
            Your response MUST be a valid JSON object with this exact structure:
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
            
            Do not include any text outside of the JSON structure. Your entire response should be valid JSON.
            """
        
        # Prepare API call parameters
        api_params = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a music analysis expert. Provide detailed analysis of music tracks in JSON format."},
                {"role": "user", "content": prompt}
            ]
        }
        
        # Add response_format parameter only for models that support it
        # GPT-4 and GPT-3.5-turbo support it, but GPT-4o doesn't
        if model in ["gpt-4", "gpt-3.5-turbo"]:
            api_params["response_format"] = {"type": "json_object"}
        
        # Send to OpenAI
        logger.info(f"Sending request to OpenAI with model: {model}")
        response = client.chat.completions.create(**api_params)
        
        # Parse the response
        analysis_text = response.choices[0].message.content.strip()
        
        # Try to parse the JSON response
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            logger.error(f"Response text: {analysis_text[:500]}...")
            
            # Try to extract JSON from the response if it contains additional text
            import re
            json_match = re.search(r'({[\s\S]*})', analysis_text)
            if json_match:
                try:
                    analysis = json.loads(json_match.group(1))
                    logger.info("Successfully extracted JSON from response")
                except json.JSONDecodeError:
                    # If still can't parse, return a structured error
                    return {
                        "error": "Failed to parse JSON response",
                        "details": str(e),
                        "raw_response": analysis_text[:1000]  # Include part of the response for debugging
                    }
            else:
                # If no JSON-like structure found, return a structured error
                return {
                    "error": "Response did not contain valid JSON",
                    "details": str(e),
                    "raw_response": analysis_text[:1000]  # Include part of the response for debugging
                }
                
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
