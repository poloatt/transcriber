import os
from pydub import AudioSegment

class AudioManager:
    def __init__(self, audio_dir):
        self.audio_dir = audio_dir

    def list_audio_files(self):
        return [f for f in os.listdir(self.audio_dir) if f.endswith('.mp3') or f.endswith('.wav')]

    def convert_to_wav(self, file_name):
        audio_path = os.path.join(self.audio_dir, file_name)
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"{file_name} not found in {self.audio_dir}")
        
        audio = AudioSegment.from_file(audio_path)
        wav_path = os.path.splitext(audio_path)[0] + '.wav'
        audio.export(wav_path, format='wav')
        return wav_path

    def get_audio_duration(self, file_name):
        audio_path = os.path.join(self.audio_dir, file_name)
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"{file_name} not found in {self.audio_dir}")
        
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0  # duration in seconds