class AudioComponent:
    def __init__(self, audio_object, start_time, sample_rate=22050):
        self.audio_data = audio_object
        self.start_time = start_time
        self.sample_rate = sample_rate
        self.duration = len(self.audio_data) / self.sample_rate

    def apply(self, audio_track, audio_rate):
        start_sample = int(self.start_time * audio_rate)
        end_sample = start_sample + len(self.audio_data)

        # Ensure that the end_sample is within the bounds of the audio_track
        if end_sample > len(audio_track):
            end_sample = len(audio_track)

        # Ensure that the audio_data fits within the specified start and end samples
        if len(self.audio_data) > (end_sample - start_sample):
            self.audio_data = self.audio_data[:end_sample - start_sample]

        audio_track[start_sample:end_sample] += self.audio_data
