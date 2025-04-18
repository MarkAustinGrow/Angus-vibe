"""
OpenAI utilities for Agent Angus.

This module provides functions for generating responses and analyzing music using OpenAI.
"""
import os
import json
import logging
import re
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
            3. Generate sample lyrics (max 2000 characters) inspired by this music
            4. Recommend parameters for music creation:
            5. Extract or suggest a concise title for this music (max 50 characters)
            
            For each category (themes, moods, genres, subgenres), provide multiple values with weightings from 0-100 to indicate their prominence.
            
            Your response MUST be a valid JSON object with this exact structure:
            {{
                "lyrics_analysis": {{
                    "summary": "Detailed summary of the lyrics",
                    "themes": [
                        {{"name": "Theme1", "weight": 90}},
                        {{"name": "Theme2", "weight": 70}},
                        {{"name": "Theme3", "weight": 50}}
                    ],
                    "moods": [
                        {{"name": "Mood1", "weight": 80}},
                        {{"name": "Mood2", "weight": 60}},
                        {{"name": "Mood3", "weight": 40}}
                    ],
                    "language": "Language of the lyrics",
                    "explicit": "Yes/No and explanation"
                }},
                "music_analysis": {{
                    "genres": [
                        {{"name": "Genre1", "weight": 80}},
                        {{"name": "Genre2", "weight": 60}},
                        {{"name": "Genre3", "weight": 40}}
                    ],
                    "subgenres": [
                        {{"name": "Subgenre1", "weight": 70}},
                        {{"name": "Subgenre2", "weight": 50}},
                        {{"name": "Subgenre3", "weight": 30}}
                    ],
                    "moods": [
                        {{"name": "Mood1", "weight": 80}},
                        {{"name": "Mood2", "weight": 60}},
                        {{"name": "Mood3", "weight": 40}}
                    ],
                    "instruments": ["instrument1", "instrument2", "instrument3"],
                    "bpm": "Estimated BPM",
                    "key": "Estimated key",
                    "vocals": "Detailed description of vocals"
                }},
                "generated_lyrics": "Sample lyrics inspired by this music (max 2000 characters)",
                "music_creation_params": {{
                    "genres": [
                        {{"name": "Genre1", "weight": 80}},
                        {{"name": "Genre2", "weight": 60}}
                    ],
                    "moods": [
                        {{"name": "Mood1", "weight": 80}},
                        {{"name": "Mood2", "weight": 60}}
                    ],
                    "timbres": [
                        {{"name": "Timbre1", "weight": 80}},
                        {{"name": "Timbre2", "weight": 60}}
                    ],
                    "duration": 120
                }},
                "title": "Extracted or suggested title for the music"
            }}
            
            For genres, choose from: Folk, Pop, Rock, Chinese Style, Hip Hop/Rap, R&B/Soul, Punk, Electronic, Jazz, Reggae, DJ, Pop Punk, Disco, Future Bass, Pop Rap, Trap Rap, R&B Rap, Chinoiserie Electronic, GuFeng Music, Pop Rock, Jazz Pop, Bossa Nova, Contemporary R&B.
            
            For moods, choose from: Happy, Dynamic/Energetic, Sentimental/Melancholic/Lonely, Inspirational/Hopeful, Nostalgic/Memory, Excited, Sorrow/Sad, Chill, Romantic, Miss, Groovy/Funky, Dreamy/Ethereal, Calm/Relaxing.
            
            For timbres, choose from: Warm, Bright, Husky, Electrified voice, Sweet, Cute, Loud and sonorous, Powerful, Sexy/Lazy.
            
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
            3. Generate sample lyrics (max 2000 characters) inspired by this music
            4. Recommend parameters for music creation:
            5. Extract or suggest a concise title for this music (max 50 characters)
            
            For each category (themes, moods, genres, subgenres), provide multiple values with weightings from 0-100 to indicate their prominence.
            
            Your response MUST be a valid JSON object with this exact structure:
            {{
                "lyrics_analysis": {{
                    "summary": "Detailed summary of the lyrics",
                    "themes": [
                        {{"name": "Theme1", "weight": 90}},
                        {{"name": "Theme2", "weight": 70}},
                        {{"name": "Theme3", "weight": 50}}
                    ],
                    "moods": [
                        {{"name": "Mood1", "weight": 80}},
                        {{"name": "Mood2", "weight": 60}},
                        {{"name": "Mood3", "weight": 40}}
                    ],
                    "language": "Language of the lyrics",
                    "explicit": "Yes/No and explanation"
                }},
                "music_analysis": {{
                    "genres": [
                        {{"name": "Genre1", "weight": 80}},
                        {{"name": "Genre2", "weight": 60}},
                        {{"name": "Genre3", "weight": 40}}
                    ],
                    "subgenres": [
                        {{"name": "Subgenre1", "weight": 70}},
                        {{"name": "Subgenre2", "weight": 50}},
                        {{"name": "Subgenre3", "weight": 30}}
                    ],
                    "moods": [
                        {{"name": "Mood1", "weight": 80}},
                        {{"name": "Mood2", "weight": 60}},
                        {{"name": "Mood3", "weight": 40}}
                    ],
                    "instruments": ["instrument1", "instrument2", "instrument3"],
                    "bpm": "Estimated BPM",
                    "key": "Estimated key",
                    "vocals": "Detailed description of vocals"
                }},
                "generated_lyrics": "Sample lyrics inspired by this music (max 2000 characters)",
                "music_creation_params": {{
                    "genres": [
                        {{"name": "Genre1", "weight": 80}},
                        {{"name": "Genre2", "weight": 60}}
                    ],
                    "moods": [
                        {{"name": "Mood1", "weight": 80}},
                        {{"name": "Mood2", "weight": 60}}
                    ],
                    "timbres": [
                        {{"name": "Timbre1", "weight": 80}},
                        {{"name": "Timbre2", "weight": 60}}
                    ],
                    "duration": 120
                }},
                "title": "Extracted or suggested title for the music"
            }}
            
            For genres, choose from: Folk, Pop, Rock, Chinese Style, Hip Hop/Rap, R&B/Soul, Punk, Electronic, Jazz, Reggae, DJ, Pop Punk, Disco, Future Bass, Pop Rap, Trap Rap, R&B Rap, Chinoiserie Electronic, GuFeng Music, Pop Rock, Jazz Pop, Bossa Nova, Contemporary R&B.
            
            For moods, choose from: Happy, Dynamic/Energetic, Sentimental/Melancholic/Lonely, Inspirational/Hopeful, Nostalgic/Memory, Excited, Sorrow/Sad, Chill, Romantic, Miss, Groovy/Funky, Dreamy/Ethereal, Calm/Relaxing.
            
            For timbres, choose from: Warm, Bright, Husky, Electrified voice, Sweet, Cute, Loud and sonorous, Powerful, Sexy/Lazy.
            
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
        
        # Function to fix common JSON formatting issues
        def fix_json(json_str):
            """
            Attempt to fix common JSON formatting issues.
            
            Args:
                json_str: The JSON string to fix
                
            Returns:
                Fixed JSON string
            """
            # Add missing commas between objects in arrays
            json_str = re.sub(r'}\s*{', '},{', json_str)
            
            # Add missing commas between key-value pairs
            json_str = re.sub(r'"\s*{', '",{', json_str)
            json_str = re.sub(r'"\s*"', '","', json_str)
            json_str = re.sub(r'"\s*\[', '",[', json_str)
            json_str = re.sub(r']\s*"', '],"', json_str)
            json_str = re.sub(r'}\s*"', '},"', json_str)
            
            return json_str
        
        # Try to parse the JSON response
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            logger.error(f"Response text: {analysis_text[:500]}...")
            
            # Try to fix common JSON formatting issues
            fixed_json = fix_json(analysis_text)
            try:
                analysis = json.loads(fixed_json)
                logger.info("Successfully parsed JSON after fixing formatting issues")
            except json.JSONDecodeError:
                # If still can't parse, try to extract JSON from the response
                json_match = re.search(r'({[\s\S]*})', analysis_text)
                if json_match:
                    extracted_json = json_match.group(1)
                    # Try to fix the extracted JSON
                    fixed_extracted_json = fix_json(extracted_json)
                    try:
                        analysis = json.loads(fixed_extracted_json)
                        logger.info("Successfully extracted and fixed JSON from response")
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
            "music_moods": analysis.get("music_analysis", {}).get("moods", []),
            
            # Add DDEX format for compatibility with existing code
            "ddex moods": [mood.get("name") for mood in analysis.get("lyrics_analysis", {}).get("moods", []) if isinstance(mood, dict) and "name" in mood],
            "ddex themes": [theme.get("name") for theme in analysis.get("lyrics_analysis", {}).get("themes", []) if isinstance(theme, dict) and "name" in theme],
            
            # Add music creation parameters for Nuro
            "music_creation_params": {
                "type": "vocal",  # Hard-coded as vocal
                "lyrics": analysis.get("generated_lyrics", ""),
                "gender": "Female",  # Hard-coded as Female
                "genres": analysis.get("music_creation_params", {}).get("genres", [{"name": "Pop", "weight": 100}]),
                "moods": analysis.get("music_creation_params", {}).get("moods", [{"name": "Happy", "weight": 100}]),
                "timbres": analysis.get("music_creation_params", {}).get("timbres", [{"name": "Warm", "weight": 100}]),
                "duration": analysis.get("music_creation_params", {}).get("duration", 120)  # Default to 120 seconds if not specified
            },
            # Add title and original URL
            "title": analysis.get("title", os.path.basename(input_source)),
            "original_url": input_source  # Store the original URL
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
