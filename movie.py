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
        self.frames = np.array([])
        self.frame_dimensions, self.average_frame_rate = self.get_dimensions_and_maximum_start_time()
        self.pipe = self.open_video()
        self.keep_last = keep_last
        self.buffer_offset = 0

    def get_dimensions_and_maximum_start_time(self):
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

    def read_next_frame(self):
        raw_image = self.pipe.stdout.read(
            self.frame_dimensions[0] * self.frame_dimensions[1] * self.frame_dimensions[2])
        self.pipe.stdout.flush()
        image = np.fromstring(raw_image, dtype='uint8')
        if image.size == 0:
            self.has_frames = False
            return
        image = image.reshape((1,) + self.frame_dimensions)
        if self.frames.size == 0:
            self.frames = image
        else:
            self.frames = np.concatenate((self.frames, image))

    def next_frame(self):
        self.current_frame += 1
        if self.frames.shape[0] <= self.current_frame:
            self.read_next_frame()
        if self.keep_last >= 0 and self.frames.shape[0] > self.keep_last + 1:
            self.frames = self.frames[1:]
            self.buffer_offset += 1

    def previous_frame(self):
        self.current_frame -= 1
        if self.current_frame < 0:
            self.current_frame = -1

    def get_frame(self):
        if self.current_frame - self.buffer_offset < 0:
            return None
        elif self.current_frame - self.buffer_offset >= self.frames.shape[0]:
            return None
        else:
            return self.frames[self.current_frame - self.buffer_offset]
