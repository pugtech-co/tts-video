import subprocess
import cv2
import tempfile
import numpy as np
from src.video_composition.video.video_component import BaseVideoComponent

class LoopingMP4(BaseVideoComponent):
    def __init__(self, mp4_path, start=0, width=1080, height=1920, fps=30, duration=None, reverse_loop=False, speed_factor=0.5, *args, **kwargs):
        print(f"Initializing LoopingMP4 with mp4_path={mp4_path}, start={start}, width={width}, height={height}, fps={fps}, duration={duration}, reverse_loop={reverse_loop}, speed_factor={speed_factor}")
        
        with tempfile.NamedTemporaryFile(suffix='.avi', delete=True) as temp_video_file:

            command = ['ffmpeg', '-y', '-i', mp4_path, '-vcodec', 'libx264', '-pix_fmt', 'bgr24', temp_video_file.name]
            print(f"Running looping command for {mp4_path}: {' '.join(command)}")

            try:
                subprocess.call(command)
            except Exception as e:
                print(f"An exception occurred: {e}")
                raise e
            
            print("Finished running ffmpeg command")

            video_capture = cv2.VideoCapture(temp_video_file.name)
            original_fps = int(video_capture.get(cv2.CAP_PROP_FPS))

            speed_factor = speed_factor * (original_fps/fps)
            print(f"\n\nUpdated Speed factor: {speed_factor}\n\n")

            print(f"Video captured")
            self.frames = []
            i = 0
            while True:
                i += 1
                if i % 100 == 0:
                    print(f"Reading frame {i}")
                ret, frame = video_capture.read()
                if not ret:
                    break
                self.frames.append(self.scale_frame(frame, width, height))
            print(f"Finished reading frames")
            video_capture.release()
            print(f"Video released")
            self.reverse_loop = reverse_loop
            self.speed_factor = speed_factor
            print(f"Speed factor: {self.speed_factor}")
            if duration is None:
                duration = len(self.frames) / fps
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

        if(self.current_frame%100 == 0):
            print(f"Current frame: {self.current_frame}, adjusted current frame: {adjusted_current_frame}, total frames: {total_frames}")

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

    def close(self):
        self.frames = None


    @staticmethod
    def get_video_duration(video_path):
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        cap.release()
        return duration

