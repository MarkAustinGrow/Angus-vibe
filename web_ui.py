"""
Web UI module for Agent Angus.

This module provides a web interface for interacting with Agent Angus,
including a UI for analyzing music using the Sonoteller API.
"""
import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom modules
from sonoteller_client import SonotellerClient
from supabase_client import SupabaseClient
from config import SONOTELLER_API_KEY

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Initialize clients
supabase = SupabaseClient()
sonoteller = SonotellerClient(SONOTELLER_API_KEY)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze a music file using Sonoteller API."""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Analyze the music
    analysis = sonoteller.analyze_music(url)
    
    if not analysis:
        return jsonify({'error': 'Failed to analyze music'}), 500
    
    # Check if there was an error in the analysis
    if 'error' in analysis:
        return jsonify({'error': analysis['error'], 'details': analysis.get('details', ''), 'raw_response': analysis.get('raw_response', '')}), 500
    
    # Store the analysis in Supabase
    influence_data = {
        'url': url,
        'analysis': analysis
    }
    
    # If a song_id was provided, associate the analysis with that song
    song_id = data.get('song_id')
    if song_id:
        influence_data['song_id'] = song_id
    
    # Store in Supabase
    try:
        response = supabase.client.table("influence_music").insert(influence_data).execute()
        if response.data and len(response.data) > 0:
            influence_id = response.data[0].get('id')
            logger.info(f"Stored influence music analysis with ID: {influence_id}")
            return jsonify({'success': True, 'analysis': analysis, 'id': influence_id})
        else:
            logger.error("No data returned from Supabase insert operation")
            return jsonify({'error': 'Failed to store analysis'}), 500
    except Exception as e:
        logger.error(f"Error storing analysis: {str(e)}")
        return jsonify({'error': f'Failed to store analysis: {str(e)}'}), 500

def run_web_ui(host='0.0.0.0', port=5000, debug=False):
    """Run the web UI."""
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    logger.info(f"Starting web UI on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
