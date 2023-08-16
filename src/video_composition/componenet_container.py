
from src.video_composition.audio.audio_component import AudioComponent
from src.video_composition.video.video_componenet import BaseVideoComponent

class ComponentContainer:
    def __init__(self):
        self.video_components = []
        self.audio_components = []

    def add_component(self, component):
        if isinstance(component, ComponentContainer):
            self.add_component_container(component)
        elif isinstance(component, BaseVideoComponent):
            self.add_video_component(component)
        elif isinstance(component, AudioComponent):
            self.add_audio_component(component)
        else:
            raise TypeError("Invalid component type")
        
    def add_video_component(self, component):
        self.video_components.append(component)
    
    def add_audio_component(self, component):
        self.audio_components.append(component)

    def add_component_container(self, componenet):
        self.video_components.extend(componenet.video_components)
        self.audio_components.extend(componenet.audio_components)

    def total_duration(self):
        max_video = max([component.start_time + component.duration for component in self.video_components], default=0)
        max_audio = max([component.start_time + component.duration for component in self.audio_components], default=0)
        return max(max_video, max_audio)

    def total_frames(self):
        return max(component.start_time * self.fps + component.frame_count for component in self.video_components)
