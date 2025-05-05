"""
Web UI module for Agent Angus.

This module provides a web interface for interacting with Agent Angus,
including a UI for analyzing music using the OpenAI API and a control panel
for the CrewAI integration.
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

# Import CrewAI integration
try:
    from angus_crew import AngusCrew
except ImportError:
    # If the CrewAI integration is not available, create a dummy class
    class AngusCrew:
        def __init__(self):
            pass
        def run_analysis_only(self):
            return {"error": "CrewAI integration not available"}
        def run_upload_only(self):
            return {"error": "CrewAI integration not available"}
        def run_engagement_only(self):
            return {"error": "CrewAI integration not available"}
        def run_full_workflow(self):
            return {"error": "CrewAI integration not available"}

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

# Remove the YouTubeAudioExtractor dependency since we're not using it anymore

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
    
    # Extract a title from the analysis or generate a default one
    title = analysis.get('title', '')
    if not title:
        # Generate a title from the filename or a default
        if 'youtube.com' in url or 'youtu.be' in url:
            title = "YouTube Song"
        else:
            title = os.path.basename(url)[:50]  # Limit to 50 chars
    
    # Make sure the title is not too long (max 50 chars)
    title = title[:50]
    
    # Store the URL in the url field, and ensure title is in the analysis
    influence_data = {
        'url': url,  # Store the actual URL in the url field
        'analysis': analysis
    }
    
    # Make sure the title is stored in the analysis
    if 'title' not in analysis:
        analysis['title'] = title
    
    # Make sure the original URL is stored in the analysis
    if 'original_url' not in analysis:
        analysis['original_url'] = url
    
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
    try:
        data = request.json
        url = data.get('url')
        model = data.get('model', 'gpt-4o')  # Default to gpt-4o if not specified
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Check if the URL is an MP3 URL
        if not url.lower().endswith('.mp3'):
            return jsonify({
                'error': 'Unsupported file format',
                'details': 'Only MP3 URLs are supported. Please convert your media to MP3 format first.'
            }), 400
        
        # Log the model being used
        logger.info(f"Analyzing MP3 URL with model: {model}")
        
        # Analyze the music using OpenAI
        analysis = analyze_music(url, is_youtube_url=False, model=model)
        
        # Check if there was an error in the analysis
        if 'error' in analysis:
            return jsonify({'error': analysis['error'], 'details': analysis.get('details', '')}), 500
        
        # Extract music creation parameters if they exist in the response
        music_creation_params = {}
        if 'music_creation_params' in analysis:
            music_creation_params = analysis.pop('music_creation_params')
            logger.info(f"Extracted music creation parameters for URL: {url}")
    except Exception as e:
        logger.error(f"Unexpected error in analyze: {str(e)}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500
    
    # Extract a title from the analysis or generate a default one
    title = analysis.get('title', '')
    if not title:
        # Generate a title from the filename or a default
        if 'youtube.com' in url or 'youtu.be' in url:
            title = "YouTube Song"
        else:
            title = os.path.basename(url)[:50]  # Limit to 50 chars
    
    # Make sure the title is not too long (max 50 chars)
    title = title[:50]
    
    # Store the URL in the url field, and ensure title is in the analysis
    influence_data = {
        'url': url,  # Store the actual URL in the url field
        'analysis': analysis
    }
    
    # Make sure the title is stored in the analysis
    if 'title' not in analysis:
        analysis['title'] = title
    
    # Make sure the original URL is stored in the analysis
    if 'original_url' not in analysis:
        analysis['original_url'] = url
    
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
            # Include music_creation_params in the response if they exist
            response_data = {
                'success': True, 
                'analysis': analysis, 
                'id': influence_id
            }
            if music_creation_params:
                response_data['music_creation_params'] = music_creation_params
                logger.info("Including music creation parameters in response")
            return jsonify(response_data)
        else:
            logger.error("No data returned from Supabase insert operation")
            return jsonify({'error': 'Failed to store analysis'}), 500
    except Exception as e:
        logger.error(f"Error storing analysis: {str(e)}")
        return jsonify({'error': f'Failed to store analysis: {str(e)}'}), 500

@app.route('/analyze_youtube', methods=['POST'])
def analyze_youtube():
    """Analyze a YouTube video using OpenAI."""
    try:
        data = request.json
        logger.info(f"Received analyze_youtube request with data: {data}")
        
        url = data.get('url')
        model = data.get('model', 'gpt-4o')  # Default to gpt-4o if not specified
        
        if not url:
            logger.error("No YouTube URL provided in request")
            return jsonify({'error': 'No YouTube URL provided'}), 400
        
        # Validate YouTube URL (simple check)
        if not ('youtube.com' in url or 'youtu.be' in url):
            logger.error(f"Invalid YouTube URL: {url}")
            return jsonify({
                'error': 'Invalid YouTube URL',
                'details': 'Please provide a valid YouTube URL'
            }), 400
        
        # Log the model being used
        logger.info(f"Analyzing YouTube URL: {url} with model: {model}")
        
        # Analyze the music using OpenAI
        analysis = analyze_music(url, is_youtube_url=True, model=model)
        logger.info(f"Analysis completed for YouTube URL: {url}")
        
        # Check if there was an error in the analysis
        if 'error' in analysis:
            logger.error(f"Error in analysis: {analysis['error']}, details: {analysis.get('details', '')}")
            return jsonify({'error': analysis['error'], 'details': analysis.get('details', '')}), 500
            
        # Extract music creation parameters if they exist in the response
        music_creation_params = {}
        if 'music_creation_params' in analysis:
            music_creation_params = analysis.pop('music_creation_params')
            logger.info(f"Extracted music creation parameters for URL: {url}")
    except Exception as e:
        logger.error(f"Unexpected error in analyze_youtube: {str(e)}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500
    
    # Extract a title from the analysis or generate a default one
    title = analysis.get('title', '')
    if not title:
        # Generate a title from the filename or a default
        if 'youtube.com' in url or 'youtu.be' in url:
            title = "YouTube Song"
        else:
            title = os.path.basename(url)[:50]  # Limit to 50 chars
    
    # Make sure the title is not too long (max 50 chars)
    title = title[:50]
    
    # Store the URL in the url field, and ensure title is in the analysis
    influence_data = {
        'url': url,  # Store the actual URL in the url field
        'analysis': analysis
    }
    
    # Make sure the title is stored in the analysis
    if 'title' not in analysis:
        analysis['title'] = title
    
    # Make sure the original URL is stored in the analysis
    if 'original_url' not in analysis:
        analysis['original_url'] = url
    
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
            # Include music_creation_params in the response if they exist
            response_data = {
                'success': True, 
                'analysis': analysis, 
                'id': influence_id
            }
            if music_creation_params:
                response_data['music_creation_params'] = music_creation_params
                logger.info("Including music creation parameters in response")
            return jsonify(response_data)
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

@app.route('/crew')
def crew_page():
    """Render the CrewAI control panel."""
    return render_template('crew.html')

@app.route(f'{URL_PREFIX}/crew')
def push_crew_page():
    """Render the CrewAI control panel for the push endpoint."""
    return render_template('crew.html')

@app.route('/api/crew/run', methods=['POST'])
def run_crew_task():
    """Run a CrewAI task."""
    try:
        data = request.json
        task_type = data.get('task_type', 'full')
        
        logger.info(f"Running CrewAI task: {task_type}")
        
        crew = AngusCrew()
        
        if task_type == 'analysis':
            # For analysis tasks, we need a URL
            url = data.get('url')
            is_youtube = data.get('is_youtube', False)
            
            if not url:
                return jsonify({'error': 'No URL provided for analysis task'}), 400
                
            # TODO: Implement analysis with URL parameter
            # For now, just run the analysis task
            result = crew.run_analysis_only()
        elif task_type == 'upload':
            limit = int(data.get('limit', 5))
            result = crew.run_upload_only()
        elif task_type == 'engagement':
            limit = int(data.get('limit', 5))
            result = crew.run_engagement_only()
        else:  # full workflow
            result = crew.run_full_workflow()
            
        logger.info(f"CrewAI task {task_type} completed successfully")
        return jsonify({'result': result})
    except Exception as e:
        logger.error(f"Error running CrewAI task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route(f'{URL_PREFIX}/api/crew/run', methods=['POST'])
def push_run_crew_task():
    """Run a CrewAI task for the push endpoint."""
    return run_crew_task()

def run_web_ui(host='0.0.0.0', port=5000, debug=False):
    """Run the web UI."""
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    logger.info(f"Starting web UI on http://{host}:{port}")
    logger.info(f"Push endpoint available at http://{host}:{port}{URL_PREFIX}/")
    app.run(host=host, port=port, debug=debug)
