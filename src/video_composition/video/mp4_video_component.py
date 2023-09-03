import subprocess
import cv2
import tempfile
import numpy as np
from src.video_composition.video.video_component import BaseVideoComponent

class VideoFromMP4Component(BaseVideoComponent):
    def __init__(self, mp4_path, start=0, width=1080, height=1920, fps=30):
        with tempfile.NamedTemporaryFile(suffix='.avi') as temp_video_file:
            subprocess.call(['ffmpeg', '-y', '-i', mp4_path, '-vcodec', 'rawvideo', '-pix_fmt', 'bgr24', temp_video_file.name])
            video_capture = cv2.VideoCapture(temp_video_file.name)
            self.frames = []
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break
                self.frames.append(frame)
            video_capture.release()
            duration = len(self.frames) / fps
            super().__init__(duration=duration, start_time=start, width=width, height=height, fps=fps)

    def apply(self, frame):
        if not self.is_active():
            return frame
        component_frame = self.frames[self.current_frame - self.start_frame]
        np.copyto(frame, component_frame)  # Copies the contents of component_frame into frame
