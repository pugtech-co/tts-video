import subprocess
import cv2
import tempfile
import numpy as np
from src.video_composition.video.video_component import BaseVideoComponent

class LoopingMP4(BaseVideoComponent):
    def __init__(self, mp4_path, start=0, width=1080, height=1920, fps=30, duration=None, reverse_loop=False, speed_factor=0.5, *args, **kwargs):
        with tempfile.NamedTemporaryFile(suffix='.avi') as temp_video_file:
            subprocess.call(['ffmpeg', '-y', '-i', mp4_path, '-vcodec', 'rawvideo', '-pix_fmt', 'bgr24', temp_video_file.name])
            video_capture = cv2.VideoCapture(temp_video_file.name)
            self.frames = []
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break
                self.frames.append(self.scale_frame(frame, width, height))
            video_capture.release()
            self.reverse_loop = reverse_loop
            self.speed_factor = speed_factor
            super().__init__(duration=duration, start_time=start, width=width, height=height, fps=fps)

    @staticmethod
    def scale_frame(frame, target_width, target_height):
            # Calculate scaling factor to maintain aspect ratio
            original_height, original_width = frame.shape[:2]
            aspect_ratio = original_width / original_height
            target_aspect_ratio = target_width / target_height

            if aspect_ratio > target_aspect_ratio:
                new_width = target_height * aspect_ratio
                new_height = target_height
            else:
                new_width = target_width
                new_height = target_width / aspect_ratio

            # Resize the frame
            frame = cv2.resize(frame, (int(new_width), int(new_height)))

            # Crop the frame to match the target dimensions
            x_offset = int((frame.shape[1] - target_width) / 2)
            y_offset = int((frame.shape[0] - target_height) / 2)
            frame = frame[y_offset:y_offset+target_height, x_offset:x_offset+target_width]

            return frame
    
    def apply(self, frame):
        if not self.is_active():
            return frame

        total_frames = len(self.frames)

        adjusted_current_frame = int((self.current_frame - self.start_frame) * self.speed_factor)

        if self.reverse_loop:
            # Forward and backward loop: 0, 1, 2, ..., n, n-1, ..., 2, 1
            oscillating_frame_index = (adjusted_current_frame) % (2 * total_frames - 2)
            
            # Handle reverse part of the loop
            if oscillating_frame_index >= total_frames:
                oscillating_frame_index = 2 * total_frames - 2 - oscillating_frame_index
        else:
            # Regular loop: 0, 1, 2, ..., n, 0, 1, ...
            oscillating_frame_index = (adjusted_current_frame) % total_frames

        component_frame = self.frames[oscillating_frame_index]
        np.copyto(frame, component_frame)