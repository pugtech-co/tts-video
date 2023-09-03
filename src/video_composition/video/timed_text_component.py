from PIL import Image, ImageDraw, ImageFont
import textwrap
import cv2
import numpy as np
from src.video_composition.video.video_component import BaseVideoComponent

class TimedTextComponent(BaseVideoComponent):
    def __init__(self, words, timestamps, font=50, font_scale=4, font_thickness=4, color=(0, 0, 0), fps=30, font_path='fonts/Roboto-Regular.ttf', *args, **kwargs, ):
        super().__init__(*args, fps=fps, **kwargs)
        self.words = words
        self.timestamps = [int(ts * fps) for ts in timestamps] 
        self.font = font
        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.color = color
        self.current_group_idx = 0
        self.ttc_frame_count = 0
        self.font_path = font_path

    def apply(self, frame):
        height, width, _ = frame.shape

        # Convert frame to RGB (for PIL compatibility)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        
        # Draw object for PIL image
        draw = ImageDraw.Draw(pil_image)

        # If there are still groups of words to display (since you can have a longer video than there are groups available)
        if self.current_group_idx < len(self.words):
            group = self.words[self.current_group_idx]
            duration = self.timestamps[self.current_group_idx]

            font_size = 180
            font = ImageFont.truetype(self.font_path, font_size)
            
            # Estimate average character width using a sample string
            sample_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            sample_width = font.getlength(sample_string)
            avg_char_width = sample_width / len(sample_string)

            # Compute the number of characters that fit into max_width pixels
            max_width = int(width * 0.95)  # Using 95% of the frame width for text
            char_count = max_width / avg_char_width
            char_count = int(char_count)  # Convert to integer

            # Use textwrap to split the group into multiple lines based on char_count
            lines = textwrap.wrap(group, width=char_count, break_long_words=True)

            # Calculate total text block height
            total_text_height = len(lines) * (font_size + 5)  # The 5 is spacing between lines

            # Calculate starting y position to center the text vertically
            y_start = (height - total_text_height) // 2

            if self.ttc_frame_count < duration:
                for i, line in enumerate(lines):
                    y = y_start + i * (font_size + 5)
                    text_width = font.getlength(line)
                    x = (width - text_width) // 2
                    draw.text((x, y), line, font=font, fill=(255, 255, 255), stroke_width=5, stroke_fill='black')
                self.ttc_frame_count += 1
            else:
                self.current_group_idx += 1
                self.ttc_frame_count += 1
        
        frame_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        frame[:,:,:] = frame_bgr[:,:,:]
