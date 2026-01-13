
# Copyright 2025 DatSciX
# ADK Web Application for Timekeeper Analysis Agent

"""
Entry point for launching the ADK Web UI.

This provides a web-based chat interface for interacting with the Timekeeper Analysis Agent.

Usage:
    python ui/adk_web_app.py
"""

import logging

from google.adk.serving import WebServer
from agents import timekeeper_director
from config.config import config

# Configure basic logging for the web server
logging.basicConfig(level=config.logging.level.upper(), format=config.logging.format)

def main():
    """Create and run the ADK Web Server."""
    web_config = config.ui.adk_web
    
    print("=" * 80)
    print("Launching Timekeeper Analysis Agent - ADK Web UI")
    print("=" * 80)
    print(f"Server starting on port: {web_config.port}")
    print(f"Open your browser to: http://localhost:{web_config.port}")
    print("Press Ctrl+C to stop the server.")
    
    # Create a WebServer instance with the main agent
    server = WebServer(
        agent=timekeeper_director,
        app_name="timekeeper_analysis_agent",
        port=web_config.port,
        enable_auth=web_config.enable_auth
    )
    
    # Run the server
    server.run()

if __name__ == "__main__":
    main()
