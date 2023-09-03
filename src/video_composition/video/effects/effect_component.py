from src.video_composition.video.video_component import BaseVideoComponent

class BaseEffectComponent(BaseVideoComponent):
    def __init__(self, position, size, transparency, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = position
        self.size = size
        self.transparency = transparency

    def apply(self, frame):
        pass