from collections import namedtuple
from TTS.utils.synthesizer import Synthesizer
from IPython.display import Audio
import numpy as np
import re
from src.tts_output import TTSOutput

class TextToSpeech:
    SAMPLE_RATE = 22050

    synthesizer = None

    @staticmethod
    def initialize_synthesizer(tts_path, tts_config_path, speakers_file_path):
        TextToSpeech.synthesizer = Synthesizer(
            tts_checkpoint=tts_path,
            tts_config_path=tts_config_path,
            tts_speakers_file=speakers_file_path,
            use_cuda=False
        )
    
    @staticmethod
    def text_to_audio(text, plt=None, speaker_name="p225", speed=1.0):
        sum_sp = 0
        sum_wi = 0
        sentences = re.split(r'(?<=[.!?]) ', text)  # Split after punctuation followed by a space
        # trim each sentence 
        sentences = [sentence.strip() for sentence in sentences]

        combined_output = None

        for sentence in sentences:
            output = TextToSpeech.synthesizer.tts(text=sentence, speaker_name=speaker_name, return_extra_outputs=True)
            
            if(speed != 1.0):
                new_durations = output[1]['outputs']['durations'].clone() / speed
                output = TextToSpeech.synthesizer.tts(text=sentence,speaker_name="p227",return_extra_outputs=True,durations=new_durations[0])

            sentence_output = TTSOutput.from_output(output, sentence, TextToSpeech.synthesizer)

            if(plt):
                print(" ---- ")
                print( "sentence: " + sentence)
                sp = str(len(TextToSpeech.custom_split(sentence, len(sentence_output.word_indices))))
                wi = str(len(sentence_output.word_indices))
                sum_sp += int(sp)
                sum_wi += int(wi)
                print("split: " + sp + " word indices: " + wi)
                print("sum split: " + str(sum_sp) + " sum word indices: " + str(sum_wi))
                if(sp != wi):
                    print("split: " + sp + " word indices: " + wi)
                    plt.figure()
                    TextToSpeech.plot_spectrogram_with_words(plt, TextToSpeech.add_beeps(sentence_output))

            if combined_output is None:
                combined_output = sentence_output
            else:
                combined_output = combined_output.combine_with(sentence_output)

        return combined_output

    @staticmethod
    def custom_split(text, expected_word_count=-1):
        words = re.split('[ -]', text)
        if len(words) == expected_word_count:
            return words

        common_fused_words = [
            'to be', 
            'for the', 
            'of the',
            'as the', 
            'for an', 
            'have been', 
            "I shall", 
            "in the", 
            "of events"]
        common_fused_words_regex = [r'\b' + re.escape(word) + r'\b' for word in common_fused_words]

        for i, fused in enumerate(common_fused_words):
            regex_pattern = common_fused_words_regex[i]
            replacement_pattern = fused.replace(' ', '_')
            text = re.sub(regex_pattern, replacement_pattern, text)

        words = text.split(' ')

        words = [word.replace('_', ' ') for word in words]
        
        return words



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
        beep = np.sin(2 * np.pi * 1000 * np.arange(0, 0.1, 1/TextToSpeech.SAMPLE_RATE))

        audio_samples = np.array(audio_output.audio)

        word_sample_indices = [int(audio_output.phoneme_timestamps[idx] / 86. * TextToSpeech.SAMPLE_RATE) for idx in audio_output.word_indices]

        for start_sample in word_sample_indices:
            end_sample = start_sample + len(beep)
            if end_sample > len(audio_samples):
                end_sample = len(audio_samples)
                beep = beep[:end_sample - start_sample]  # Truncate beep if necessary
            audio_samples[start_sample:end_sample] += beep

        return TTSOutput(audio=audio_samples, pre_tokenized_text=audio_output.pre_tokenized_text, phoneme_timestamps=audio_output.phoneme_timestamps, total_running_time_s=audio_output.total_running_time_s, word_timestamps=audio_output.word_timestamps, word_indices=audio_output.word_indices)

# Paths and Parameters
tts_path = "/Users/tindelllockett/Library/Application Support/tts/tts_models--en--vctk--vits/model_file.pth"
tts_config_path = "/Users/tindelllockett/Library/Application Support/tts/tts_models--en--vctk--vits/config.json"
speakers_file_path = "/Users/tindelllockett/Library/Application Support/tts/tts_models--en--vctk--vits/speaker_ids.json"
text = "hello world; this is an example sentence"

# Initialization and execution
TextToSpeech.initialize_synthesizer(tts_path, tts_config_path, speakers_file_path)

