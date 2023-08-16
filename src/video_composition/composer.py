import numpy as np
import cv2
import soundfile as sf
import tempfile
import subprocess
from src.video_composition.componenet_container import ComponentContainer

class VideoComposition(ComponentContainer):
    VIDEO_CODEC = 'mp4v'

    def __init__(self, width, height, fps, audio_rate=22050):
        super().__init__()
        self.width = width
        self.height = height
        self.fps = fps
        self.audio_rate = audio_rate

    def create_video(self, output_file):
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video_file, tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio_file:
            self._create_video_frames(temp_video_file.name)
            self._create_audio_track(temp_audio_file.name)

            command = ['ffmpeg', '-y', '-i', temp_video_file.name, '-i', temp_audio_file.name, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', '-loglevel', 'error', output_file]
            subprocess.run(command, check=True)

    def _create_video_frames(self, video_output_file):
        fourcc = cv2.VideoWriter_fourcc(*VideoComposition.VIDEO_CODEC)
        out = cv2.VideoWriter(video_output_file, fourcc, self.fps, (self.width, self.height))

        for _ in range(self.total_frames()):
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)  # Blank frame
            for component in self.video_components:
                if component.is_active():
                    component.apply(frame)
                component.increment_frame()
            
            out.write(frame)  

        out.release()  

    def _create_audio_track(self, audio_output_file):
        total_samples = int(self.audio_rate * self.total_duration())
        audio_track = np.zeros(total_samples)

        for audio_component in self.audio_components:
            audio_component.apply(audio_track, self.audio_rate)

        sf.write(audio_output_file, audio_track, self.audio_rate)