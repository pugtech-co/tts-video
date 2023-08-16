import cv2
import numpy as np
from src.video_composition.video.video_componenet import BaseVideoComponent

class StaticBackgroundImageComponent(BaseVideoComponent):
    def __init__(self, background_image_path, width, height, fps, start_time, duration):
        super().__init__(width, height, fps, start_time, duration)
        self.background_image = cv2.imread(background_image_path)

    def apply(self, frame):
        if self.is_active():
            frame[:,:,:] = self.background_image
