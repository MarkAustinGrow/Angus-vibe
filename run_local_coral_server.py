#!/usr/bin/env python3
"""
Run Local Coral Protocol Server

This script sets up and runs a local Coral Protocol server for development and testing.
It uses the Coral Protocol server implementation from the Coral Protocol repository.
"""
import os
import sys
import logging
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Default Coral server directory
DEFAULT_CORAL_SERVER_DIR = os.getenv("CORAL_SERVER_DIR", "./coral-server")

def check_prerequisites():
    """Check if all prerequisites are installed."""
    logger.info("Checking prerequisites...")
    
    # Check if Node.js is installed
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        logger.info(f"Node.js version: {node_version}")
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("Node.js is not installed. Please install Node.js v18 or later.")
        return False
    
    # Check if npm is installed
    try:
        npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
        logger.info(f"npm version: {npm_version}")
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("npm is not installed. Please install npm.")
        return False
    
    # Check if git is installed
    try:
        git_version = subprocess.check_output(["git", "--version"], text=True).strip()
        logger.info(f"git version: {git_version}")
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("git is not installed. Please install git.")
        return False
    
    logger.info("✅ All prerequisites are installed")
    return True

def clone_coral_server(server_dir):
    """Clone the Coral Protocol server repository."""
    logger.info(f"Cloning Coral Protocol server to {server_dir}...")
    
    # Check if the directory already exists
    if os.path.exists(server_dir):
        logger.info(f"Directory {server_dir} already exists")
        
        # Check if it's a git repository
        if os.path.exists(os.path.join(server_dir, ".git")):
            logger.info("Pulling latest changes...")
            try:
                subprocess.run(["git", "pull"], cwd=server_dir, check=True)
                logger.info("✅ Successfully pulled latest changes")
                return True
            except subprocess.SubprocessError as e:
                logger.error(f"Failed to pull latest changes: {str(e)}")
                return False
        else:
            logger.error(f"Directory {server_dir} exists but is not a git repository")
            return False
    
    # Clone the repository
    try:
        subprocess.run(
            ["git", "clone", "https://github.com/Coral-Protocol/coral-server.git", server_dir],
            check=True
        )
        logger.info("✅ Successfully cloned Coral Protocol server")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to clone Coral Protocol server: {str(e)}")
        return False

def install_dependencies(server_dir):
    """Install dependencies for the Coral Protocol server."""
    logger.info("Installing dependencies...")
    
    try:
        subprocess.run(["npm", "install"], cwd=server_dir, check=True)
        logger.info("✅ Successfully installed dependencies")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to install dependencies: {str(e)}")
        return False

def build_server(server_dir):
    """Build the Coral Protocol server."""
    logger.info("Building Coral Protocol server...")
    
    try:
        subprocess.run(["npm", "run", "build"], cwd=server_dir, check=True)
        logger.info("✅ Successfully built Coral Protocol server")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to build Coral Protocol server: {str(e)}")
        return False

def run_server(server_dir, port=3001):
    """Run the Coral Protocol server."""
    logger.info(f"Starting Coral Protocol server on port {port}...")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env["PORT"] = str(port)
        
        # Run the server
        server_process = subprocess.Popen(
            ["npm", "run", "start"],
            cwd=server_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the server to start
        logger.info("Waiting for server to start...")
        time.sleep(5)
        
        # Check if the server is running
        if server_process.poll() is None:
            logger.info(f"✅ Coral Protocol server is running on port {port}")
            return server_process
        else:
            stdout, stderr = server_process.communicate()
            logger.error(f"Server failed to start: {stderr}")
            return None
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to start Coral Protocol server: {str(e)}")
        return None

def main():
    """Main function to run the local Coral Protocol server."""
    logger.info("Setting up local Coral Protocol server...")
    
    # Check prerequisites
    if not check_prerequisites():
        logger.error("Prerequisites check failed. Exiting.")
        sys.exit(1)
    
    # Get the server directory
    server_dir = os.getenv("CORAL_SERVER_DIR", DEFAULT_CORAL_SERVER_DIR)
    server_dir = Path(server_dir).resolve()
    
    # Clone the repository
    if not clone_coral_server(server_dir):
        logger.error("Failed to clone Coral Protocol server. Exiting.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies(server_dir):
        logger.error("Failed to install dependencies. Exiting.")
        sys.exit(1)
    
    # Build the server
    if not build_server(server_dir):
        logger.error("Failed to build Coral Protocol server. Exiting.")
        sys.exit(1)
    
    # Get the port
    port = int(os.getenv("CORAL_SERVER_PORT", "3001"))
    
    # Run the server
    server_process = run_server(server_dir, port)
    if server_process is None:
        logger.error("Failed to start Coral Protocol server. Exiting.")
        sys.exit(1)
    
    # Set environment variable for the Coral server URL
    os.environ["CORAL_SERVER_URL"] = f"http://localhost:{port}/sse"
    
    logger.info(f"Coral Protocol server is running at http://localhost:{port}")
    logger.info(f"SSE endpoint is available at http://localhost:{port}/sse")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        # Keep the server running
        while True:
            # Check if the server is still running
            if server_process.poll() is not None:
                stdout, stderr = server_process.communicate()
                logger.error(f"Server stopped unexpectedly: {stderr}")
                sys.exit(1)
            
            # Wait a bit
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping Coral Protocol server...")
        server_process.terminate()
        server_process.wait()
        logger.info("Coral Protocol server stopped")

if __name__ == "__main__":
    main()
