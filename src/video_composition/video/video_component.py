class BaseVideoComponent:
    def __init__(self, width, height, fps, start_time, duration):
        self.width = width
        self.height = height
        self.fps = fps
        self.start_time = start_time  # Start time in seconds
        self.duration = duration
        self.start_frame = int(fps * start_time)  # Frame number when this component starts
        self.frame_count = int(fps * duration)  # Total number of frames for this component
        self.current_frame = 0  # Current frame counter

        print("Component: " + str(self.start_frame) + " - " + str(self.start_frame + self.frame_count))
        print("Duration: " + str(self.duration))

    def set_duration(self, duration):
        self.duration = duration
        self.frame_count = int(self.fps * duration)

    # Remember to modify the frame in place.
    def apply(self, frame):
        pass

    def is_active(self):
        return self.start_frame <= self.current_frame < self.start_frame + self.frame_count

    def increment_frame(self):
        self.current_frame += 1
