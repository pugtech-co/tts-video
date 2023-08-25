from collections import namedtuple
import cv2
import os
import soundfile as sf
import subprocess
import tempfile


class VideoCreator:
    DEFAULT_FONT = cv2.FONT_HERSHEY_SIMPLEX
    DEFAULT_FPS = 30
    SAMPLE_RATE = 22050
    # This is the number of timestamps per second.  I don't know where it comes from. I calculated it by trial and error.
    TIMESTAMP_UNITS_PER_SECOND = 86 
    
    VIDEO_CODEC = 'mp4v'

    @staticmethod
    def create_word_video(word, duration, background_image_path, output_file, font=DEFAULT_FONT, font_scale=2, font_thickness=2, fps=DEFAULT_FPS, color=(0,0,0)):
        background_image = VideoCreator._read_background_image(background_image_path)
        height, width, _ = background_image.shape # Define width and height here

        out = VideoCreator._create_video_writer(background_image, output_file, fps)

        # The following code is unchanged from the original
        text_size = cv2.getTextSize(word, font, font_scale, font_thickness)[0]
        x = (width - text_size[0]) // 2
        y = (height + text_size[1]) // 2
        frames_to_write = int(fps * duration)
        for _ in range(frames_to_write):
            frame = background_image.copy()
            cv2.putText(frame, word, (x, y), font, font_scale, color, font_thickness)
            out.write(frame)
        out.release()

    @staticmethod
    def create_sentence_video(sentence, word_timestamps, audio_samples, background_image_path, output_file='output/sentence.mp4', fps=DEFAULT_FPS, audio_rate=SAMPLE_RATE):
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video_file, tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_word_file, tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio_file:
            background_image = VideoCreator._read_background_image(background_image_path)
            out = VideoCreator._create_video_writer(background_image, temp_video_file.name, fps)

            words = sentence.split()
            audio_duration = len(audio_samples) / audio_rate
            word_durations = [(word_timestamps[i + 1] - word_timestamps[i]) / VideoCreator.TIMESTAMP_UNITS_PER_SECOND for i in range(len(word_timestamps) - 1)]
            word_durations.append(audio_duration - word_timestamps[-1] / VideoCreator.TIMESTAMP_UNITS_PER_SECOND)

            for word, duration in zip(words, word_durations):
                VideoCreator.create_word_video(word, duration, background_image_path, temp_word_file.name)
                cap = cv2.VideoCapture(temp_word_file.name)
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out.write(frame)
                cap.release()
                os.remove(temp_word_file.name)
            out.release()

            # Handling the audio
            sf.write(temp_audio_file.name, audio_samples, audio_rate)
            command = ['ffmpeg', '-y', '-i', temp_video_file.name, '-i', temp_audio_file.name, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', '-loglevel', 'error', output_file]
            subprocess.run(command, check=True)
            os.remove(temp_video_file.name)
            os.remove(temp_audio_file.name)

    @staticmethod
    def _read_background_image(background_image_path):
        return cv2.imread(background_image_path)

    @staticmethod
    def _create_video_writer(image, output_file, fps):
        fourcc = cv2.VideoWriter_fourcc(*VideoCreator.VIDEO_CODEC)
        height, width, _ = image.shape
        return cv2.VideoWriter(output_file, fourcc, fps, (width, height))
