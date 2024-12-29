"""
Transcriber application package.
"""
import logging
import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from .config import Config
from .utils.transcriber import transcribe_audio  # Adjust the import path

__version__ = '0.1.0'

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure logging with correct path
    logging.basicConfig(
        filename=os.path.join(Config.LOGS_DIR, 'transcriber.log'),
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Use Config paths consistently
    app.static_folder = Config.STATIC_DIR
    app.static_url_path = '/static'
    
    # Import and register blueprint
    from .routes import transcriber_bp  # Ensure this is correct
    app.register_blueprint(transcriber_bp, url_prefix='/api')  # Register the new blueprint
    
    @app.route('/')
    def serve_index():
        return send_from_directory(Config.STATIC_DIR, 'index.html')
    
    return app
