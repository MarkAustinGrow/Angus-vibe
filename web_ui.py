"""
Web UI module for Agent Angus.

This module provides a web interface for interacting with Agent Angus,
including a UI for analyzing music using the OpenAI API.
"""
import os
import logging
import uuid
import shutil
import time
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom modules
from supabase_client import SupabaseClient
from openai_utils import analyze_music

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Set up URL prefix for the push endpoint
URL_PREFIX = '/push'

# Initialize clients
supabase = SupabaseClient()

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'mp3'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max upload size
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup cleanup thread
cleanup_interval = 3600  # 1 hour
cleanup_age = 86400  # 24 hours

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Clean up old files in the upload folder."""
    while True:
        try:
            logger.info("Cleaning up old files...")
            now = time.time()
            count = 0
            
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # If the file is older than cleanup_age, delete it
                if os.path.isfile(file_path) and os.path.getmtime(file_path) < now - cleanup_age:
                    os.remove(file_path)
                    count += 1
                    
            logger.info(f"Cleaned up {count} old files")
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")
            
        # Sleep for the specified interval
        time.sleep(cleanup_interval)

# Start the cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route(f'{URL_PREFIX}/')
def push_index():
    """Render the main page for the push endpoint."""
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route(f'{URL_PREFIX}/uploads/<filename>')
def push_uploaded_file(filename):
    """Serve uploaded files for the push endpoint."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload a file and return its URL."""
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    # Check if the file is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    # Check if the file is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Only MP3 files are supported.'}), 400
        
    # Generate a unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    # Save the file
    file.save(file_path)
    logger.info(f"File uploaded: {file_path}")
    
    # Generate the URL
    host_url = request.host_url.rstrip('/')
    file_url = f"{host_url}/uploads/{unique_filename}"
    
    return jsonify({
        'success': True,
        'filename': unique_filename,
        'url': file_url
    })

@app.route(f'{URL_PREFIX}/upload', methods=['POST'])
def push_upload_file():
    """Upload a file and return its URL for the push endpoint."""
    return upload_file()

@app.route('/save_parsed_analysis', methods=['POST'])
def save_parsed_analysis():
    """Save parsed Sonoteller analysis to the database."""
    data = request.json
    analysis = data.get('analysis')
    
    if not analysis:
        return jsonify({'error': 'No analysis provided'}), 400
    
    # Create a dummy URL if none is provided
    url = data.get('url', 'https://sonoteller.com/manual_input')
    
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
            logger.info(f"Stored parsed analysis with ID: {influence_id}")
            return jsonify({'success': True, 'id': influence_id})
        else:
            logger.error("No data returned from Supabase insert operation")
            return jsonify({'error': 'Failed to store analysis'}), 500
    except Exception as e:
        logger.error(f"Error storing analysis: {str(e)}")
        return jsonify({'error': f'Failed to store analysis: {str(e)}'}), 500

@app.route(f'{URL_PREFIX}/save_parsed_analysis', methods=['POST'])
def push_save_parsed_analysis():
    """Save parsed Sonoteller analysis to the database for the push endpoint."""
    return save_parsed_analysis()

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze a music file using OpenAI."""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Check if the URL is an MP3 URL
    if not url.lower().endswith('.mp3'):
        return jsonify({
            'error': 'Unsupported file format',
            'details': 'Only MP3 URLs are supported. Please convert your media to MP3 format first.'
        }), 400
    
    # Analyze the music using OpenAI
    analysis = analyze_music(url, is_youtube_url=False)
    
    # Check if there was an error in the analysis
    if 'error' in analysis:
        return jsonify({'error': analysis['error'], 'details': analysis.get('details', '')}), 500
    
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

@app.route('/analyze_youtube', methods=['POST'])
def analyze_youtube():
    """Analyze a YouTube video using OpenAI."""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No YouTube URL provided'}), 400
    
    # Validate YouTube URL (simple check)
    if not ('youtube.com' in url or 'youtu.be' in url):
        return jsonify({
            'error': 'Invalid YouTube URL',
            'details': 'Please provide a valid YouTube URL'
        }), 400
    
    # Analyze the music using OpenAI
    analysis = analyze_music(url, is_youtube_url=True)
    
    # Check if there was an error in the analysis
    if 'error' in analysis:
        return jsonify({'error': analysis['error'], 'details': analysis.get('details', '')}), 500
    
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
            logger.info(f"Stored YouTube music analysis with ID: {influence_id}")
            return jsonify({'success': True, 'analysis': analysis, 'id': influence_id})
        else:
            logger.error("No data returned from Supabase insert operation")
            return jsonify({'error': 'Failed to store analysis'}), 500
    except Exception as e:
        logger.error(f"Error storing analysis: {str(e)}")
        return jsonify({'error': f'Failed to store analysis: {str(e)}'}), 500

@app.route(f'{URL_PREFIX}/analyze', methods=['POST'])
def push_analyze():
    """Analyze a music file using OpenAI for the push endpoint."""
    return analyze()

@app.route(f'{URL_PREFIX}/analyze_youtube', methods=['POST'])
def push_analyze_youtube():
    """Analyze a YouTube video using OpenAI for the push endpoint."""
    return analyze_youtube()

def run_web_ui(host='0.0.0.0', port=5000, debug=False):
    """Run the web UI."""
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    logger.info(f"Starting web UI on http://{host}:{port}")
    logger.info(f"Push endpoint available at http://{host}:{port}{URL_PREFIX}/")
    app.run(host=host, port=port, debug=debug)
