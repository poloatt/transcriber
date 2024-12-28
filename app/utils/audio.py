import os
from pydub import AudioSegment

class AudioHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.audio = None
        self.load_audio()

    def load_audio(self):
        if os.path.exists(self.file_path):
            self.audio = AudioSegment.from_file(self.file_path)
        else:
            raise FileNotFoundError(f"File {self.file_path} not found")

    def save_audio(self, output_path, format="wav"):
        if self.audio:
            self.audio.export(output_path, format=format)
        else:
            raise ValueError("No audio loaded to save")

    def get_duration(self):
        if self.audio:
            return len(self.audio) / 1000.0  # duration in seconds
        else:
            raise ValueError("No audio loaded to get duration")

    def split_audio(self, start_time, end_time):
        if self.audio:
            start_ms = start_time * 1000
            end_ms = end_time * 1000
            return self.audio[start_ms:end_ms]
        else:
            raise ValueError("No audio loaded to split")

    def change_volume(self, db):
        if self.audio:
            self.audio = self.audio + db
        else:
            raise ValueError("No audio loaded to change volume")

# Example usage:
# handler = AudioHandler("path/to/audio/file.mp3")
# handler.change_volume(5)
# handler.save_audio("path/to/output/file.wav")