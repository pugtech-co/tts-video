import cv2
import numpy as np
from src.video_composition.video.video_componenet import BaseVideoComponent

class TimedTextComponent(BaseVideoComponent):
    def __init__(self, words, timestamps, font=50, font_scale=2, font_thickness=2, color=(0, 0, 0), fps=30, *args, **kwargs):
        super().__init__(*args, fps=fps, **kwargs)
        self.words = words
        self.timestamps = [int(ts * fps) for ts in timestamps] # Convert timestamps to frames
        self.font = font
        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.color = color
        self.current_word_idx = 0
        

    def apply(self, frame):
        # Check if it's time to move to the next word
        if self.current_word_idx < len(self.words) - 1 and self.current_frame >= self.timestamps[self.current_word_idx + 1]:
            self.current_word_idx += 1

        # Get the current word
        word = self.words[self.current_word_idx]

        # Determine the position to place the text
        text_size = cv2.getTextSize(word, self.font, self.font_scale, self.font_thickness)[0]
        x = (frame.shape[1] - text_size[0]) // 2
        y = (frame.shape[0] + text_size[1]) // 2

        # Add the text to the frame
        cv2.putText(frame, word, (x, y), self.font, self.font_scale, self.color, self.font_thickness)
    