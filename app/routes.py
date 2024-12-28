from flask import jsonify, request, Blueprint
from .config import Config
from .utils.audio_manager import AudioManager
from .utils.transcriber import transcribe_file
import os
import logging

# Usar un nombre único para el blueprint
transcriber_bp = Blueprint('transcriber_v7', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@transcriber_bp.route('/')
def index():
    return 'Transcriber service is running!'

@transcriber_bp.route('/test')
def test():
    return 'Test endpoint working!'

@transcriber_bp.route('/health')
def health():
    return jsonify({"status": "healthy"})

@transcriber_bp.route('/record', methods=['POST'])
def record():
    if not audio_manager:
        return jsonify({'error': 'Audio manager not initialized'}), 500

    try:
        duration = int(request.form.get('duration', 5))
        if duration <= 0:
            return jsonify({'error': 'Duration must be positive'}), 400
            
        filename = audio_manager.record(duration)
        return jsonify({
            'status': 'success',
            'filename': filename
        })
    except Exception as e:
        logger.error(f"Error recording audio: {e}")
        return jsonify({'error': str(e)}), 500

@transcriber_bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Handle both file upload and existing file transcription"""
    try:
        temp_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
                
            if not any(file.filename.lower().endswith(fmt) for fmt in Config.SUPPORTED_FORMATS):
                return jsonify({'error': f'Unsupported format. Supported: {Config.SUPPORTED_FORMATS}'}), 400
            
            temp_path = os.path.join(Config.OUTPUT_DIR, "temp_" + file.filename)
            file.save(temp_path)
            
        elif 'filename' in request.form:
            temp_path = os.path.join(Config.OUTPUT_DIR, request.form['filename'])
            if not os.path.exists(temp_path):
                return jsonify({'error': 'File not found'}), 404
                
        else:
            return jsonify({'error': 'No file or filename provided'}), 400
        
        text = transcribe_file(temp_path)
        
        # Clean up temp file only if it was uploaded
        if 'file' in request.files and temp_path:
            os.remove(temp_path)
            
        return jsonify({
            'text': text,
            'status': 'success'
        })
            
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        logger.error(f"Error transcribing audio: {e}")
        return jsonify({'error': str(e)}), 500

@transcriber_bp.route('/upload', methods=['POST'])
def upload_audio():
    logger.info("Received upload request")
    try:
        if 'audio' not in request.files:
            logger.error("No audio file in request")
            return jsonify({'error': 'No audio file provided'}), 400
            
        audio_file = request.files['audio']
        if audio_file.filename == '':
            logger.error("Empty filename")
            return jsonify({'error': 'No selected file'}), 400
            
        # Save the uploaded file with correct path
        temp_path = os.path.join(Config.UPLOADS_DIR, 'temp_recording.webm')
        logger.info(f"Saving file to {temp_path}")
        
        audio_file.save(temp_path)
        
        # Transcribe the audio
        try:
            text = transcribe_file(temp_path)
            return jsonify({
                'status': 'success',
                'transcription': text
            })
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@transcriber_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@transcriber_bp.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500
