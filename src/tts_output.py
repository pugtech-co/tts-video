import numpy as np

MAGIC_NUMBER = 86 # This is the number of timestamps per second.  I don't know where it comes from. I calculated it by trial and error.
SAMPLE_RATE = 22050

class TTSOutput:
    def __init__(self, audio, pre_tokenized_text, phoneme_timestamps, total_running_time_s, word_timestamps, word_indices):
        self.audio = audio # this makes sure the array is flat
        self.pre_tokenized_text = pre_tokenized_text
        self.phoneme_timestamps = phoneme_timestamps
        self.total_running_time_s = total_running_time_s
        self.word_timestamps = word_timestamps
        self.word_indices = word_indices

    def combine_with(self, other):
        combined_audio = np.concatenate([self.audio, other.audio])
        offset_time = self.total_running_time_s * MAGIC_NUMBER
        combined_phoneme_timestamps = np.concatenate([self.phoneme_timestamps, [ts + offset_time for ts in other.phoneme_timestamps]])
        combined_word_timestamps = self.word_timestamps + [ts + offset_time for ts in  other.word_timestamps]
        combined_pre_tokenized_text = self.pre_tokenized_text + other.pre_tokenized_text
        combined_running_time = self.total_running_time_s + other.total_running_time_s
        combined_word_indices = self.word_indices + [idx + len(self.phoneme_timestamps) for idx in other.word_indices]

        return TTSOutput(combined_audio, combined_pre_tokenized_text, combined_phoneme_timestamps, combined_running_time, combined_word_timestamps, combined_word_indices)

    def get_word_timestamps_seconds(self):
        return [t / MAGIC_NUMBER for t in self.word_timestamps]

    @staticmethod
    def from_output(output, text, synthesizer):
        pre_tokenized_text, phoneme_timestamps = TTSOutput.get_phoneme_durations_and_timestamps(text, output, synthesizer)
        audio = np.array(output[0])
        running_time = len(output[0]) / SAMPLE_RATE
        word_timestamps, word_indices = TTSOutput.get_word_timestamps_and_indices(pre_tokenized_text, phoneme_timestamps)

        return TTSOutput(audio, pre_tokenized_text, phoneme_timestamps, running_time, word_timestamps, word_indices)
   
    @staticmethod
    def get_phoneme_durations_and_timestamps(text, output, synthesizer):
        tokens = synthesizer.tts_model.tokenizer.text_to_ids(text)
        pre_tokenized_text_blnk = [synthesizer.tts_model.tokenizer.decode([y]) for y in tokens]
        pre_tokenized_text = [x if x != '<BLNK>' else '_' for x in pre_tokenized_text_blnk]
        phoneme_durations = output[1]['outputs']['durations'].cpu().data.numpy()
        phoneme_timestamps = np.cumsum(phoneme_durations)
        return pre_tokenized_text, phoneme_timestamps
    
    @staticmethod
    def get_word_timestamps_and_indices(pre_tokenized_text, phoneme_timestamps):        
        word_indices = [0] + [i for i, phoneme in enumerate(pre_tokenized_text) if phoneme == ' ']
        word_timestamps=[float(phoneme_timestamps[space_idx]) for space_idx in word_indices]
        return word_timestamps, word_indices


# I made this cause there was a method i wanted in here.  Now I don't remember. 