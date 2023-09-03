from src.video_composition.combo.component_container import ComponentContainer
from src.video_composition.audio.audio_component import AudioComponent
from src.video_composition.video.timed_text_component import TimedTextComponent
from src.tts import TextToSpeech

# Sound from TTS is kinda soft, so amplify it by default. 
AMPLIFICATION = 4
class TTSComponent(ComponentContainer):
    def __init__(self, text, width=1080, height=1920, fps=30, color=(0, 0, 0), *args, start = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.words = TextToSpeech.custom_split(text)

        output = TextToSpeech.text_to_audio(text)
        timestamps = [time + start for time in output.get_word_timestamps_seconds()]
        ttc = TimedTextComponent(self.words, timestamps, start_time=start, duration=output.total_running_time_s, width=width, height=height, fps=fps, color=color)
        ac = AudioComponent(output.audio * AMPLIFICATION, start_time=start)

        self.add_component(ttc)
        self.add_component(ac)
