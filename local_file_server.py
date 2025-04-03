"""
Local file server for serving files over HTTP.
"""
import os
import http.server
import socketserver
import threading
import tempfile
import socket
import logging
import time
import shutil
from typing import Optional, Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalFileServer:
    """
    A simple HTTP server for serving local files.
    """
    
    def __init__(self, base_dir: Optional[str] = None, port: int = 0):
        """
        Initialize the local file server.
        
        Args:
            base_dir: Base directory to serve files from. If None, a temporary directory will be created.
            port: Port to run the server on. If 0, a random available port will be used.
        """
        self.base_dir = base_dir or tempfile.mkdtemp()
        self.port = port
        self.server = None
        self.server_thread = None
        self.is_running = False
        self.files = {}  # Map of file IDs to file paths
        
        # Create base directory if it doesn't exist
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            
        logger.info(f"Initialized local file server with base directory: {self.base_dir}")
    
    def start(self) -> bool:
        """
        Start the HTTP server in a background thread.
        
        Returns:
            True if the server was started successfully, False otherwise
        """
        if self.is_running:
            logger.info("Server is already running")
            return True
            
        try:
            # Find an available port if not specified
            if self.port == 0:
                self.port = self._find_available_port()
                
            # Create a simple HTTP server
            handler = http.server.SimpleHTTPRequestHandler
            
            # Change to the base directory
            os.chdir(self.base_dir)
            
            # Create the server
            self.server = socketserver.TCPServer(("", self.port), handler)
            
            # Start the server in a separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.is_running = True
            logger.info(f"Started local file server on port {self.port}")
            
            # Wait a moment for the server to start
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting local file server: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the HTTP server and clean up.
        
        Returns:
            True if the server was stopped successfully, False otherwise
        """
        if not self.is_running:
            logger.info("Server is not running")
            return True
            
        try:
            # Stop the server
            if self.server:
                self.server.shutdown()
                self.server.server_close()
                
            # Wait for the thread to finish
            if self.server_thread:
                self.server_thread.join(timeout=5)
                
            self.is_running = False
            logger.info("Stopped local file server")
            
            # Clean up the temporary directory if it was created by us
            if self.base_dir and os.path.exists(self.base_dir) and self.base_dir.startswith(tempfile.gettempdir()):
                shutil.rmtree(self.base_dir)
                logger.info(f"Cleaned up temporary directory: {self.base_dir}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error stopping local file server: {str(e)}")
            return False
    
    def add_file(self, file_path: str, file_id: Optional[str] = None) -> Optional[str]:
        """
        Add a file to the server.
        
        Args:
            file_path: Path to the file to add
            file_id: Optional ID for the file. If None, the basename will be used.
            
        Returns:
            URL of the file, or None if the file could not be added
        """
        if not self.is_running:
            if not self.start():
                logger.error("Failed to start server")
                return None
                
        try:
            # Use the basename if no file ID is provided
            if not file_id:
                file_id = os.path.basename(file_path)
                
            # Copy the file to the base directory
            dest_path = os.path.join(self.base_dir, file_id)
            shutil.copy2(file_path, dest_path)
            
            # Store the file path
            self.files[file_id] = dest_path
            
            # Return the URL
            url = f"http://localhost:{self.port}/{file_id}"
            logger.info(f"Added file to server: {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"Error adding file to server: {str(e)}")
            return None
    
    def remove_file(self, file_id: str) -> bool:
        """
        Remove a file from the server.
        
        Args:
            file_id: ID of the file to remove
            
        Returns:
            True if the file was removed successfully, False otherwise
        """
        if file_id not in self.files:
            logger.warning(f"File not found: {file_id}")
            return False
            
        try:
            # Get the file path
            file_path = self.files[file_id]
            
            # Remove the file
            if os.path.exists(file_path):
                os.remove(file_path)
                
            # Remove the file from the dictionary
            del self.files[file_id]
            
            logger.info(f"Removed file from server: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing file from server: {str(e)}")
            return False
    
    def _find_available_port(self) -> int:
        """
        Find an available port.
        
        Returns:
            An available port number
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def __del__(self):
        """
        Clean up when the object is deleted.
        """
        self.stop()
