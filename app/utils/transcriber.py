from typing import Optional
import speech_recognition as sr
from pydub import AudioSegment
import os
import logging
from ..config import Config  # Update import path

logger = logging.getLogger(__name__)

def convert_to_wav(file_path: str) -> Optional[str]:
    """Convert audio file to WAV format if needed"""
    try:
        if file_path.endswith('.wav'):
            return file_path
            
        audio = AudioSegment.from_file(file_path)
        wav_path = file_path + '.wav'
        audio = audio.set_channels(1)  # Convert to mono
        audio = audio.set_frame_rate(16000)  # Set sample rate to 16kHz
        audio.export(wav_path, format='wav')
        logger.info(f"Converted {file_path} to WAV format")
        return wav_path
    except Exception as e:
        logger.error(f"Error converting audio: {e}")
        return None

def transcribe_audio(file_path, language='en-US'):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
        try:
            # Cambia el idioma según el parámetro
            transcription = recognizer.recognize_google(audio, language=language)
            return transcription
        except sr.UnknownValueError:
            return "No se pudo entender el audio"
        except sr.RequestError as e:
            return f"Error en la solicitud; {e}"

def transcribe_file(file_path: str) -> str:
    """Transcribe an audio file to text with error handling"""
    temp_path = os.path.join(Config.UPLOADS_DIR, 'temp_wav_file.wav')
    try:
        # Convert to WAV if needed
        temp_path = convert_to_wav(file_path)
        if not temp_path:
            raise ValueError("Failed to convert audio file")

        # Initialize recognizer
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300  # Adjust for ambient noise
        recognizer.dynamic_energy_threshold = True
        
        # Perform transcription
        with sr.AudioFile(temp_path) as source:
            logger.info("Reading audio file...")
            audio_data = recognizer.record(source)
            logger.info("Transcribing audio...")
            text = recognizer.recognize_google(
                audio_data,
                language='en-US',  # Set language explicitly
                show_all=False     # Return best result only
            )
            logger.info("Transcription complete")
            return text

    except sr.UnknownValueError:
        logger.warning("Speech recognition could not understand audio")
        return "Could not understand audio"
    except sr.RequestError as e:
        logger.error(f"Could not request results from speech recognition service: {e}")
        return "Service error"
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise
    finally:
        # Clean up temporary WAV file
        if temp_path and temp_path != file_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.debug(f"Removed temporary file: {temp_path}")
            except Exception as e:
                logger.warning(f"Could not remove temporary file: {e}")

if __name__ == "__main__":
    file_path = "path_to_your_audio_file.wav"
    transcription = transcribe_file(file_path)
    print(transcription)