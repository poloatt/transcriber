"""
Transcriber application package.
"""
import logging
import os
import json
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from .config import Config
from .utils.transcriber import transcribe_audio  # Ensure this imports the Google Cloud Speech function
from .utils.llm import process_with_llm  # Ensure this imports the LLM processing function

__version__ = '0.1.0'

# Lista para almacenar las transcripciones
transcriptions = []

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
    
    @app.route('/transcribe', methods=['POST'])
    def transcribe():
        if 'audio' not in request.files:
            return jsonify({'error': 'No se encontró el archivo de audio.'}), 400

        audio_file = request.files['audio']
        
        # Guardar el archivo de audio temporalmente
        temp_file_path = f"/tmp/{audio_file.filename}"
        audio_file.save(temp_file_path)  # Guardar el archivo en el servidor

        print("Audio recibido y guardado en el servidor.")  # Log de recepción

        # Llamar a la función de transcripción
        transcription = transcribe_audio(temp_file_path, language='es-AR')
        
        print(f"Transcripción generada: {transcription}")  # Log de transcripción

        return jsonify({'transcription': transcription})
    
    @app.route('/evaluate', methods=['POST'])
    def evaluate():
        # Aquí puedes manejar las transcripciones recibidas
        transcriptions = request.form.to_dict()  # Obtener las transcripciones del formulario
        print(transcriptions)  # Imprimir en la consola para verificar
        return jsonify({'status': 'success', 'data': transcriptions})
    
    @app.route('/save_transcriptions', methods=['POST'])
    def save_transcriptions():
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Guardar las transcripciones en un archivo o base de datos
        with open(os.path.join(Config.LOGS_DIR, 'final_transcriptions.json'), 'w') as f:
            json.dump(data, f)

        # Enviar las transcripciones al LLM para procesamiento
        llm_response = process_with_llm(data)
        if 'error' in llm_response:
            return jsonify({'status': 'error', 'message': 'Failed to process with LLM', 'error': llm_response['error']}), 500

        return jsonify({'status': 'success', 'message': 'Transcriptions saved and processed successfully', 'llm_response': llm_response})
    
    return app
