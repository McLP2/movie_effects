import numpy as np
import subprocess as sp
import os

FFMPEG_BINARY = "ffmpeg"  # the file path to ffmpeg
FFPROBE_BINARY = "ffprobe"  # the file path to ffprobe


class Movie:
    def __init__(self, filename, keep_last=-1):
        self.has_frames = True
        self.filename = filename
        if not os.path.exists(filename):
            raise FileNotFoundError
        self.current_frame = -1
        self.frame_dimensions, self.average_frame_rate = self.get_dimensions_and_frame_rate()
        self.pipe = self.open_video()
        self.keep_last = keep_last

    def get_dimensions_and_frame_rate(self):
        command = [FFPROBE_BINARY,
                   '-v', '0',
                   '-of', 'compact=nk=1:p=0',
                   '-select_streams', 'v:0',
                   '-show_entries', 'stream=width,height,avg_frame_rate',
                   self.filename]
        pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, bufsize=10 ** 8)
        (output, error) = pipe.communicate()
        info = output.decode('utf8').replace("|", "\n")
        lines = info.splitlines()
        frame_dimensions = (int(lines[1]), int(lines[0]), 3)
        average_frame_rate = eval(lines[2])
        return frame_dimensions, average_frame_rate

    def open_video(self):
        command = [FFMPEG_BINARY,
                   '-i', self.filename,
                   '-loglevel', 'error',
                   '-f', 'image2pipe',
                   '-pix_fmt', 'rgb24',
                   '-vcodec', 'rawvideo',
                   '-']
        return sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, bufsize=10 ** 5)

    def get_next_frame(self):
        raw_image = self.pipe.stdout.read(
            self.frame_dimensions[0] * self.frame_dimensions[1] * self.frame_dimensions[2])
        image = np.fromstring(raw_image, dtype='uint8')
        if image.size == 0:
            self.has_frames = False
            return
        image = image.reshape(self.frame_dimensions)
        self.current_frame += 1
        return image
