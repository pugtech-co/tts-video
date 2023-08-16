from src.video_composition.combo.componenet_container import ComponentContainer
from src.video_composition.audio.mp4_audio_component import AudioFromMP4Component
from src.video_composition.video.mp4_video_componenet import VideoFromMP4Component

class MP4Component(ComponentContainer):
    def __init__(self, mp4_path, start=0, width=1080, height=1920, fps=30,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        ac = AudioFromMP4Component(mp4_path, start_time=start)
        vc = VideoFromMP4Component(mp4_path, start=start, width=width, height=height, fps=fps)
        self.add_component(vc)
        self.add_component(ac)