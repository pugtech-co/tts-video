import soundfile as sf
from scipy.signal import resample

class AudioFileComponent:
    def __init__(self, audio_file_path, start_time=0):
        self.audio_data, self.sample_rate = self._load_audio_file(audio_file_path)
        self.start_time = start_time
        self.duration = len(self.audio_data) / self.sample_rate  # Calculate duration in seconds


    def _load_audio_file(self, file_path):
        audio_data, sample_rate = sf.read(file_path)
        return audio_data, sample_rate

    def apply(self, audio_track, audio_rate):
        # Resample audio_data if the sample rate doesn't match the target audio_rate
        if self.sample_rate != audio_rate:
            self.audio_data = resample(self.audio_data, num=self.audio_data.shape[0] * audio_rate // self.sample_rate)

        start_sample = int(self.start_time * audio_rate)
        end_sample = start_sample + len(self.audio_data)

        if end_sample > len(audio_track):
            end_sample = len(audio_track)

        if len(self.audio_data) > (end_sample - start_sample):
            self.audio_data = self.audio_data[:end_sample - start_sample]

        audio_track[start_sample:end_sample] += self.audio_data
