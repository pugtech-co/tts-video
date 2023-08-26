from moviepy.editor import VideoClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_resize
import cv2
import random
import numpy as np

class PanImageComponent:
    def __init__(self, background_image_path, width, height, fps, start_time, duration, direction=None):
        self.width = width
        self.height = height
        self.fps = fps
        self.start_time = start_time
        self.duration = duration
        self.frame_count = int(fps * duration)
        self.background_image = cv2.imread(background_image_path, cv2.IMREAD_UNCHANGED)
        
        if self.background_image.shape[2] == 3:  # If the image has no alpha channel
            alpha_channel = np.ones(self.background_image.shape[:2], dtype=self.background_image.dtype) * 255
            self.background_image = np.dstack([self.background_image, alpha_channel])
    
        self.background_image = cv2.cvtColor(self.background_image, cv2.COLOR_BGRA2RGBA)

        self.img_height, self.img_width, _ = self.background_image.shape

        self.viewframe_height = int(0.75 * self.img_height)
        self.viewframe_width = int(self.viewframe_height * 9 / 16)

        if self.viewframe_width > self.img_width:
            raise ValueError("The image isn't wide enough to maintain a 9:16 aspect ratio.")

        self.start_y = random.randint(0, self.img_height - self.viewframe_height)
        self.end_y = random.randint(0, self.img_height - self.viewframe_height)

        if direction is None:
            direction = random.choice(['left_to_right', 'right_to_left'])

        if direction == 'left_to_right':
            self.start_x = 0
            self.end_x = self.img_width - self.viewframe_width
        elif direction == 'right_to_left':
            self.start_x = self.img_width - self.viewframe_width
            self.end_x = 0
        else:
            raise ValueError("Invalid direction provided. Use 'left_to_right', 'right_to_left', or None.")

        self.clip = VideoClip(self.make_frame, duration=self.duration)
        self.mask = VideoClip(self.make_mask_frame, ismask=True, duration=self.duration)
        self.clip = self.clip.set_mask(self.mask)
        self.clip.fps = self.fps
        self.clip = self.clip.set_start(self.start_time)

    def make_frame(self, t):
        # print("Making frame for pan")
        frame_from_start = int(self.fps * t)
        current_y = int(self.start_y + (self.end_y - self.start_y) * frame_from_start / self.frame_count)
        current_x = int(self.start_x + (self.end_x - self.start_x) * frame_from_start / self.frame_count)

        crop_img = self.background_image[current_y:current_y + self.viewframe_height, 
                                        current_x:current_x + self.viewframe_width]

        resized_crop = cv2.resize(crop_img, (self.width, self.height))

        # we are using masks for the alpha channel, so we need to remove it from the frame
        return resized_crop[:, :, :3]

    def make_mask_frame(self, t):
        # print("Making mask frame for pan")
        frame_from_start = int(self.fps * t)
        current_y = int(self.start_y + (self.end_y - self.start_y) * frame_from_start / self.frame_count)
        current_x = int(self.start_x + (self.end_x - self.start_x) * frame_from_start / self.frame_count)

        crop_img = self.background_image[current_y:current_y + self.viewframe_height, 
                                         current_x:current_x + self.viewframe_width]
        resized_crop = cv2.resize(crop_img, (self.width, self.height))

        # Extract the alpha channel and return it
        alpha_frame = resized_crop[:, :, 3] / 255
        return alpha_frame

