import numpy as np
import cv2

class VideoComposition:
    VIDEO_CODEC = 'mp4v'

    def __init__(self, width, height, fps):
        self.width = width
        self.height = height
        self.fps = fps
        self.components = []

    def create_video(self, output_file):
        # Define the codec and create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*VideoComposition.VIDEO_CODEC)
        out = cv2.VideoWriter(output_file, fourcc, self.fps, (self.width, self.height))

        for _ in range(self.total_frames()):
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)  # Blank frame
            for component in self.components:
                if component.is_active():
                    component.apply(frame)
                component.increment_frame()
            
            out.write(frame)  # Write frame to the video

        out.release()  # Release the VideoWriter object

    def add_component(self, component):
        self.components.append(component)
    

    def total_frames(self):
        print(self.components)
        return max(component.start_time * self.fps + component.frame_count for component in self.components)
