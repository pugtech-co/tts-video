from moviepy.editor import TextClip, VideoClip
import numpy as np

class TimedTextComponent:
    def __init__(self, words, timestamps, font_scale=2, font_thickness=2, color=(0, 0, 0), fps=30, width=640, height=480, start_time=0, duration=10):
        self.words = words
        self.timestamps = timestamps
        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.color = color
        self.width = width
        self.height = height
        self.fps = fps
        self.start_time = start_time
        self.duration = duration
        self.current_frame = np.ones((self.height, self.width, 3), dtype=np.uint8) * 100
        self.current_mask_frame = np.ones((self.height, self.width))  # Placeholder for alpha
        self.current_word_timestamp = 0

        self.clip = VideoClip(self.make_frame, duration=self.duration)
        self.mask = VideoClip(self.make_mask_frame, ismask=True, duration=self.duration)
        self.clip = self.clip.set_mask(self.mask)
        self.clip.fps = self.fps
        self.clip = self.clip.set_start(self.start_time)


    def update_current_frame(self, t):
        '''
        Uses TextClip to generate a single color text and mask frame for the current word.
        In the future, we can change this to use PIL or whatever, as long as we can get an alpha channel out of it.
        '''
        for i, ts in reversed(list(enumerate(self.timestamps))):
            if t >= ts:
                if ts != self.current_word_timestamp:
                    self.current_word_timestamp = ts

                    # Create a black on white TextClip to be used for alpha channel
                    temp_alpha_clip = TextClip(self.words[i], fontsize=self.font_scale, color="white", bg_color="black").set_duration(self.duration).on_color(size=(self.width, self.height))
                    alpha_frame = temp_alpha_clip.get_frame(t)[:, :, 0]  # Use any channel as they are all the same in grayscale
                    self.current_mask_frame = alpha_frame / 255.0  # Normalize to [0, 1]

                    # Create a colored frame for RGB channels
                    self.current_frame = np.full((self.height, self.width, 3), self.color, dtype=np.uint8)
                break
            
    def make_frame(self, t):
        # print("Making frame for text at time " + str(t) + " seconds")
        if t >= self.current_word_timestamp:
            self.update_current_frame(t)
        
        return self.current_frame  # Return only the RGB channels

    def make_mask_frame(self, t):
        # print("Making mask frame for text at time " + str(t) + " seconds")
        if self.current_mask_frame is not None:
            # print("Alpha channel found. Using it.")
            return self.current_mask_frame
        else:
            # print("No alpha channel found. Assuming fully opaque.")
            return np.zeros((self.height, self.width))  # Assume fully opaque if alpha channel is missing
