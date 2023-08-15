from collections import namedtuple
from TTS.utils.synthesizer import Synthesizer
from IPython.display import Audio
import numpy as np

class TextToSpeech:
    synthesizer = None
    AudioOutput = namedtuple("AudioOutput", ["audio", "pre_tokenized_text", "phoneme_timestamps", "total_running_time_s", "word_timestamps", "space_indices"])

    @staticmethod
    def initialize_synthesizer(tts_path, tts_config_path, speakers_file_path):
        TextToSpeech.synthesizer = Synthesizer(
            tts_checkpoint=tts_path,
            tts_config_path=tts_config_path,
            tts_speakers_file=speakers_file_path,
            use_cuda=False
        )
    
    @staticmethod
    def text_to_audio(text, plt=None, speaker_name="p225"):
        sentences = text.split('. ')
        final_audio = []
        final_pre_tokenized_text = []
        final_phoneme_timestamps = []
        total_running_time_s = 0

        final_word_timestamps = []
        final_space_indices = []
        
        for sentence in sentences:
            output = TextToSpeech.synthesizer.tts(text=sentence, speaker_name=speaker_name, return_extra_outputs=True)
            pre_tokenized_text, phoneme_timestamps = TextToSpeech.get_phoneme_durations_and_timestamps(sentence, output)
            
            final_audio.append(output[0])
            phonemes_before_sentence = len(final_phoneme_timestamps)
            magic_number = 86 # what is this?
            final_phoneme_timestamps.extend([timestamp + total_running_time_s * magic_number for timestamp in phoneme_timestamps])

            final_pre_tokenized_text.extend(pre_tokenized_text)
            
            space_indices_for_sentence = [0] + [i + 1 for i, phoneme in enumerate(pre_tokenized_text) if phoneme == ' ']
            space_indices = [index + phonemes_before_sentence for index in space_indices_for_sentence]
            final_space_indices.extend(space_indices)


            running_time = len(output[0]) / 22050.
            total_running_time_s += running_time
            if(plt):
                plt.figure()

                audio_output_for_sentence = TextToSpeech.AudioOutput(
                    audio=np.array(output[0]), 
                    pre_tokenized_text=pre_tokenized_text, 
                    phoneme_timestamps=phoneme_timestamps, 
                    total_running_time_s=running_time, 
                    word_timestamps=[float(phoneme_timestamps[space_idx]) for space_idx in space_indices_for_sentence], 
                    space_indices=space_indices_for_sentence)

                TextToSpeech.plot_spectrogram_with_words(plt, TextToSpeech.add_beeps(audio_output_for_sentence))


        # final_space_indices = [0] + [i for i, phoneme in enumerate(final_pre_tokenized_text) if phoneme == ' ']
        final_word_timestamps = [float(final_phoneme_timestamps[space_idx]) for space_idx in final_space_indices]

        return TextToSpeech.AudioOutput(audio=np.concatenate(final_audio), pre_tokenized_text=final_pre_tokenized_text, phoneme_timestamps=final_phoneme_timestamps, total_running_time_s=total_running_time_s, word_timestamps=final_word_timestamps, space_indices=final_space_indices)


    @staticmethod
    def get_phoneme_durations_and_timestamps(text, output):
        tokens = TextToSpeech.synthesizer.tts_model.tokenizer.text_to_ids(text)
        pre_tokenized_text_blnk = [TextToSpeech.synthesizer.tts_model.tokenizer.decode([y]) for y in tokens]
        pre_tokenized_text = [x if x != '<BLNK>' else '_' for x in pre_tokenized_text_blnk]
        phoneme_durations = output[1]['outputs']['durations'].cpu().data.numpy()
        phoneme_timestamps = np.cumsum(phoneme_durations)
        return pre_tokenized_text, phoneme_timestamps
    
    @staticmethod
    def plot_spectrogram_with_words(plt, audio_output):
        spec = TextToSpeech.synthesizer.tts_model.ap.melspectrogram(audio_output.audio)

        plt.figure(figsize=(20, 5))
        plt.imshow(spec, origin="lower", aspect='auto', interpolation='none')

        # Calculate the differences between consecutive timestamps to get the durations
        phoneme_durations = np.diff(audio_output.phoneme_timestamps, prepend=0)

        # Cumulative sum to get the locations of the x-ticks
        cumulative_durations = np.cumsum(phoneme_durations)

        # Shift by half the duration to center the labels
        plt.xticks(cumulative_durations, audio_output.pre_tokenized_text, rotation=0)

        for x in audio_output.word_timestamps:
            plt.axvline(x, color="red", linewidth=4)

        plt.gca().xaxis.tick_top()
        plt.title("Word durations")
        plt.show()

    @staticmethod
    def add_beeps(audio_output):
        beep = np.sin(2 * np.pi * 1000 * np.arange(0, 0.1, 1/22050))
        # Get the audio samples
        audio_samples = np.array(audio_output.audio)

        # Convert the word start timestamps to sample indices using the space indices
        word_sample_indices = [int(audio_output.phoneme_timestamps[idx] / 86. * 22050) for idx in audio_output.space_indices]

        # Insert the beep at each word start
        for start_sample in word_sample_indices:
            end_sample = start_sample + len(beep)
            if end_sample > len(audio_samples):
                end_sample = len(audio_samples)
                beep = beep[:end_sample - start_sample]  # Truncate beep if necessary
            audio_samples[start_sample:end_sample] += beep

        # Replace the audio in the AudioOutput tuple
        return TextToSpeech.AudioOutput(audio=audio_samples, pre_tokenized_text=audio_output.pre_tokenized_text, phoneme_timestamps=audio_output.phoneme_timestamps, total_running_time_s=audio_output.total_running_time_s, word_timestamps=audio_output.word_timestamps, space_indices=audio_output.space_indices)

# Paths and Parameters
tts_path = "/Users/tindelllockett/Library/Application Support/tts/tts_models--en--vctk--vits/model_file.pth"
tts_config_path = "/Users/tindelllockett/Library/Application Support/tts/tts_models--en--vctk--vits/config.json"
speakers_file_path = "/Users/tindelllockett/Library/Application Support/tts/tts_models--en--vctk--vits/speaker_ids.json"
text = "hello world; this is an example sentence"

# Initialization and execution
TextToSpeech.initialize_synthesizer(tts_path, tts_config_path, speakers_file_path)

