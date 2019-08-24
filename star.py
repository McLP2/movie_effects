from effect import Effect
from PIL import Image
from PIL import ImageDraw
import numpy as np


class Star(Effect):
    def apply(self, frame, frame_number):
        slices = int(self.params)
        frame_image = Image.fromarray(frame)
        w, h = frame_image.size
        mask = Image.new('L', frame_image.size, color=0)
        draw = ImageDraw.Draw(mask)
        draw.pieslice([(-w, h / 2 - w), (w, h / 2 + w)], -180 / slices, 180 / slices, fill=255, outline=254, width=4)
        frame_image.putalpha(mask)
        final_image = Image.new('RGB', frame_image.size)
        for i in range(slices):
            flipped_image = frame_image if i % 2 == 0 else frame_image.transpose(Image.FLIP_TOP_BOTTOM)
            rotated_frame = flipped_image.rotate(i * 360 / slices, center=(0, h / 2), translate=(w / 2, 0))
            final_image.paste(rotated_frame, (0, 0), rotated_frame)
        frame = np.array(final_image)
        return frame
