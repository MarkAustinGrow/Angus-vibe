#!/usr/bin/env python3
"""
Test script for the enhanced music analysis functionality.

This script tests the analyze_music function with a YouTube URL and prints the results.
"""
import json
import argparse
import logging
from openai_utils import analyze_music

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main function to test the analyze_music function.
    """
    parser = argparse.ArgumentParser(description='Test the music analysis functionality')
    parser.add_argument('--url', type=str, required=False, 
                        default="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        help='YouTube URL to analyze (default: Rick Astley - Never Gonna Give You Up)')
    parser.add_argument('--model', type=str, default="gpt-4o", 
                        choices=["gpt-4o", "gpt-4", "gpt-3.5-turbo"],
                        help='OpenAI model to use (default: gpt-4o)')
    args = parser.parse_args()
    
    youtube_url = args.url
    model = args.model
    
    logger.info(f"Analyzing YouTube URL: {youtube_url} with model: {model}")
    
    try:
        # Call the analyze_music function with the YouTube URL
        analysis_results = analyze_music(youtube_url, is_youtube_url=True, model=model)
        
        # Check if there was an error
        if "error" in analysis_results:
            logger.error(f"Error analyzing music: {analysis_results['error']}")
            if "details" in analysis_results:
                logger.error(f"Details: {analysis_results['details']}")
            return
        
        # Print the results in a formatted way
        print("\n" + "="*80)
        print("MUSIC ANALYSIS RESULTS")
        print("="*80)
        
        # Print summary
        if "summary" in analysis_results:
            print("\nSUMMARY:")
            print(analysis_results["summary"])
        
        # Print themes with weights
        if "themes" in analysis_results and analysis_results["themes"]:
            print("\nTHEMES:")
            for theme in analysis_results["themes"]:
                if isinstance(theme, dict) and "name" in theme and "weight" in theme:
                    print(f"- {theme['name']} ({theme['weight']})")
                else:
                    print(f"- {theme}")
        
        # Print moods with weights
        if "moods" in analysis_results and analysis_results["moods"]:
            print("\nMOODS:")
            for mood in analysis_results["moods"]:
                if isinstance(mood, dict) and "name" in mood and "weight" in mood:
                    print(f"- {mood['name']} ({mood['weight']})")
                else:
                    print(f"- {mood}")
        
        # Print language and explicit content
        if "language" in analysis_results:
            print(f"\nLANGUAGE: {analysis_results['language']}")
        
        if "explicit" in analysis_results:
            print(f"EXPLICIT: {analysis_results['explicit']}")
        
        # Print genres with weights
        if "genres" in analysis_results and analysis_results["genres"]:
            print("\nGENRES:")
            for genre in analysis_results["genres"]:
                if isinstance(genre, dict) and "name" in genre and "weight" in genre:
                    print(f"- {genre['name']} ({genre['weight']})")
                else:
                    print(f"- {genre}")
        
        # Print subgenres with weights
        if "subgenres" in analysis_results and analysis_results["subgenres"]:
            print("\nSUBGENRES:")
            for subgenre in analysis_results["subgenres"]:
                if isinstance(subgenre, dict) and "name" in subgenre and "weight" in subgenre:
                    print(f"- {subgenre['name']} ({subgenre['weight']})")
                else:
                    print(f"- {subgenre}")
        
        # Print music moods with weights
        if "music_moods" in analysis_results and analysis_results["music_moods"]:
            print("\nMUSIC MOODS:")
            for mood in analysis_results["music_moods"]:
                if isinstance(mood, dict) and "name" in mood and "weight" in mood:
                    print(f"- {mood['name']} ({mood['weight']})")
                else:
                    print(f"- {mood}")
        
        # Print instruments
        if "instruments" in analysis_results and analysis_results["instruments"]:
            print("\nINSTRUMENTS:")
            print(", ".join(analysis_results["instruments"]))
        
        # Print BPM and key
        if "bpm" in analysis_results or "key" in analysis_results:
            print("\nBPM & KEY:")
            if "bpm" in analysis_results:
                print(f"- BPM: {analysis_results['bpm']}")
            if "key" in analysis_results:
                print(f"- Key: {analysis_results['key']}")
        
        # Print vocals
        if "vocals" in analysis_results:
            print(f"\nVOCALS: {analysis_results['vocals']}")
        
        # Print music creation parameters
        if "music_creation_params" in analysis_results:
            print("\nMUSIC CREATION PARAMETERS:")
            params = analysis_results["music_creation_params"]
            
            if "genres" in params:
                print("\nGenres:")
                for genre in params["genres"]:
                    if isinstance(genre, dict) and "name" in genre and "weight" in genre:
                        print(f"- {genre['name']} ({genre['weight']})")
                    else:
                        print(f"- {genre}")
            
            if "moods" in params:
                print("\nMoods:")
                for mood in params["moods"]:
                    if isinstance(mood, dict) and "name" in mood and "weight" in mood:
                        print(f"- {mood['name']} ({mood['weight']})")
                    else:
                        print(f"- {mood}")
            
            if "timbres" in params:
                print("\nTimbres:")
                for timbre in params["timbres"]:
                    if isinstance(timbre, dict) and "name" in timbre and "weight" in timbre:
                        print(f"- {timbre['name']} ({timbre['weight']})")
                    else:
                        print(f"- {timbre}")
            
            if "duration" in params:
                print(f"\nDuration: {params['duration']} seconds")
        
        # Print the full JSON for reference
        print("\n" + "="*80)
        print("FULL JSON RESPONSE:")
        print("="*80)
        print(json.dumps(analysis_results, indent=2))
        
    except Exception as e:
        logger.error(f"Error in test script: {str(e)}")

if __name__ == "__main__":
    main()
