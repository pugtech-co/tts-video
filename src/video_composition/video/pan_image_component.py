import cv2
import numpy as np
from src.video_composition.video.video_component import BaseVideoComponent
import random

class PanImageComponent(BaseVideoComponent):
    def __init__(self, background_image_path, width, height, fps, start_time, duration, direction=None):
        super().__init__(width, height, fps, start_time, duration)
        self.background_image = cv2.imread(background_image_path)
        height, width, layers = self.background_image.shape

        # Set the height to 75% of the original image (I want a diagonal pan, you could set to 100 if you wanted)
        self.viewframe_height = int(0.75 * height)
        
        # Compute width based on 9:16 aspect ratio
        self.viewframe_width = int(self.viewframe_height * 9 / 16)

        # Ensure our viewframe isn't larger than the image in either dimension
        if self.viewframe_width > width:
            print("The image isn't wide enough to maintain a 9:16 aspect ratio.")
            raise ValueError

        # Generate random start and end y-coordinates for panning
        self.start_y = random.randint(0, height - self.viewframe_height)
        self.end_y = random.randint(0, height - self.viewframe_height)

        # Determine direction of panning
        if direction is None:
            direction = random.choice(['left_to_right', 'right_to_left'])

        # for variety, you can pan R to L or L to R
        if direction == 'left_to_right':
            self.start_x = 0
            self.end_x = self.width - self.viewframe_width
        elif direction == 'right_to_left':
            self.start_x = self.width - self.viewframe_width
            self.end_x = 0
        else:
            print("Invalid direction provided. Use 'left_to_right', 'right_to_left', or None.")
            raise ValueError


    def apply(self, frame):
        if self.is_active():
            frame_from_start = self.current_frame - self.start_frame
            current_y = int(self.start_y + (self.end_y - self.start_y) * frame_from_start / self.frame_count)

            # Linearly interpolate the x-coordinate for horizontal panning
            current_x = int(self.start_x + (self.end_x - self.start_x) * frame_from_start / self.frame_count)

            # Crop the image for the panning effect
            crop_img = self.background_image[current_y:current_y+self.viewframe_height, current_x:current_x+self.viewframe_width]

            # Resize cropped image to 540x960
            resized_crop = cv2.resize(crop_img, (540, 960))

            frame[:,:,:] = resized_crop
