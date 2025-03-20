"""
OpenAI utilities for Agent Angus.

This module provides functions for generating responses using OpenAI.
"""
import logging
from openai import OpenAI
from typing import Optional

# Import configuration
from config import OPENAI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

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
