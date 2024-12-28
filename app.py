from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
import logging
import speech_recognition as sr
import os
from pydub import AudioSegment
import tempfile

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure logging
    logger = logging.getLogger(__name__)
    
    # Move static folder configuration here
    app.static_folder = 'static'
    app.static_url_path = ''
    
    print(f"[DEBUG] Static folder configured as: {app.static_folder}")

    @app.before_request
    def before_request():
        print(f"[DEBUG] Request Method: {request.method}")
        print(f"[DEBUG] Request Path: {request.path}")
        print(f"[DEBUG] Request Headers: {dict(request.headers)}")

    @app.errorhandler(Exception)
    def handle_error(error):
        logger.error(f"Unhandled error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500

    # Rewrite the upload endpoint
    @app.route('/upload', methods=['POST'])
    def upload_audio():
        print(f"[DEBUG] Request Method: {request.method}")
        print(f"[DEBUG] Content-Type: {request.content_type}")
        print(f"[DEBUG] Request Headers: {dict(request.headers)}")
        print(f"[DEBUG] Files: {list(request.files.keys())}")

        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        try:
            audio_file = request.files['audio']
            temp_dir = os.path.join(os.getcwd(), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_path = os.path.join(temp_dir, 'temp.webm')
            audio_file.save(temp_path)
            
            audio = AudioSegment.from_file(temp_path)
            wav_path = os.path.join(temp_dir, 'temp.wav')
            audio.export(wav_path, format='wav')
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
            
            # Cleanup
            os.remove(temp_path)
            os.remove(wav_path)
            
            return jsonify({'transcription': text})
            
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # Serve index.html at root
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5002, debug=True)
