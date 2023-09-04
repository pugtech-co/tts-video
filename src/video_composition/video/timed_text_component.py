import cv2
import numpy as np
from src.video_composition.video.video_component import BaseVideoComponent

class TimedTextComponent(BaseVideoComponent):
    def __init__(self, words, timestamps, font=50, font_scale=4, font_thickness=4, color=(0, 0, 0), fps=30, *args, **kwargs):
        super().__init__(*args, fps=fps, **kwargs)
        self.words = words
        self.timestamps = [int(ts * fps) for ts in timestamps] 
        self.font = font
        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.color = color
        self.current_word_idx = 0
        

    def apply(self, frame):
        if self.current_word_idx < len(self.words) - 1 and self.current_frame >= self.timestamps[self.current_word_idx + 1]:
            self.current_word_idx += 1

        word = self.words[self.current_word_idx]
        text_size = cv2.getTextSize(word, self.font, self.font_scale, self.font_thickness)[0]
        x = (frame.shape[1] - text_size[0]) // 2
        y = (frame.shape[0] + text_size[1]) // 2

        shadow_offset = (2, 2)  
        shadow_color = (0, 0, 0)  
        main_color = (255, 255, 255) 

        cv2.putText(frame, word, (x + shadow_offset[0], y + shadow_offset[1]), self.font, self.font_scale, shadow_color, self.font_thickness)
        cv2.putText(frame, word, (x, y), self.font, self.font_scale, main_color, self.font_thickness)
