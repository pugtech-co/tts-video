from src.video_composition.video.effects.effect_component import BaseEffectComponent
import cv2

class StaticImageEffect(BaseEffectComponent):
    def __init__(self, image_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        self.image = cv2.resize(self.image, self.size)

        # Check if the image has an alpha channel
        if self.image.shape[2] == 4:
            # Splitting the image into RGB and alpha channels
            self.image_rgb = self.image[:, :, :3]
            self.image_alpha = self.image[:, :, 3] / 255.0
        else:
            self.image_rgb = self.image
            self.image_alpha = None

    def apply(self, frame):
        if self.is_active():
            x, y = self.position
            h, w, _ = self.image_rgb.shape

            if self.image_alpha is not None:
                # Applying the static image effect considering the alpha channel
                for c in range(0, 3):
                    frame[y:y+h, x:x+w, c] = frame[y:y+h, x:x+w, c] * (1 - self.image_alpha) + self.image_rgb[:, :, c] * self.image_alpha
            else:
                # No alpha channel, so directly apply the RGB image
                frame[y:y+h, x:x+w, :] = self.image_rgb
