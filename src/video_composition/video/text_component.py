import cv2
import numpy as np
from src.video_composition.video.video_component import BaseVideoComponent


class TextComponent(BaseVideoComponent):
    def __init__(self, text, font, font_scale=2, font_thickness=2, color=(0, 0, 0), x=None, y=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.font = font
        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.color = color
        self.x = x
        self.y = y

    def apply(self, frame):
        # Determine the position to place the text if not provided
        if self.x is None or self.y is None:
            text_size = cv2.getTextSize(self.text, self.font, self.font_scale, self.font_thickness)[0]
            self.x = (frame.shape[1] - text_size[0]) // 2
            self.y = (frame.shape[0] + text_size[1]) // 2
        
        # Add the text to the frame
        cv2.putText(frame, self.text, (self.x, self.y), self.font, self.font_scale, self.color, self.font_thickness)