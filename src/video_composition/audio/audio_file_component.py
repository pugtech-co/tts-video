from src.video_composition.audio.audio_component import AudioComponent
import soundfile as sf

class AudioFileComponent(AudioComponent):
    def __init__(self, audio_file_path, start_time=0, *args, **kwargs):
        self.audio_data, self.sample_rate = self._load_audio_file(audio_file_path)

        # If the audio_data is stereo, average the two channels to create mono
        if self.audio_data.ndim == 2 and self.audio_data.shape[1] == 2:
            self.audio_data = self.audio_data.mean(axis=1)
            
        self.duration = len(self.audio_data) / self.sample_rate  # Calculate duration in seconds
        super().__init__(self.audio_data, *args, sample_rate=self.sample_rate, start_time=start_time, **kwargs)



    def _load_audio_file(self, file_path):
        audio_data, sample_rate = sf.read(file_path)
        return audio_data, sample_rate