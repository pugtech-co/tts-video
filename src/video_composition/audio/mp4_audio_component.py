import subprocess
import wave
import numpy as np
import tempfile
from src.video_composition.audio.audio_file_component import AudioFileComponent

class AudioFromMP4Component(AudioFileComponent):
    def __init__(self, mp4_path, sample_rate=22050, *args, **kwargs):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio_file:
            self.temp_audio_path = temp_audio_file.name

            # Command to extract audio, resample, and trim the start time if needed
            command = [
                'ffmpeg',
                '-i', mp4_path,           # Input file path
                '-ar', str(sample_rate),  # Set sample rate
                '-vn',                    # No video
                '-y',                     # Overwrite output file if it exists
                '-acodec', 'pcm_s16le',   # Codec for WAV
                self.temp_audio_path      # Output temporary file path
            ]
            subprocess.run(command)

            super().__init__(audio_file_path=temp_audio_file, *args, **kwargs)