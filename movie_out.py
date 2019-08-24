import numpy as np
import subprocess as sp
import os

FFMPEG_BINARY = "ffmpeg"  # the file path to ffmpeg
FFPROBE_BINARY = "ffprobe"  # the file path to ffprobe


class MovieOutput:
    def __init__(self, filename, frame_dimensions, frame_rate):
        self.filename = filename
        if os.path.exists(filename):
            raise FileExistsError
        self.frame_dimensions = frame_dimensions
        self.frame_rate = frame_rate
        self.pipe = self.open_video()

    def open_video(self):
        command = [FFMPEG_BINARY,
                   '-f', 'rawvideo',
                   '-loglevel', 'error',
                   '-vcodec', 'rawvideo',
                   '-s', '{}x{}'.format(self.frame_dimensions[1], self.frame_dimensions[0]),
                   '-pix_fmt', 'rgb24',
                   '-r', str(self.frame_rate),
                   '-i', '-',
                   '-an',  # no audio
                   '-b:v', '16M',
                   self.filename]
        return sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)

    def append(self, frame):
        self.pipe.stdin.write(frame.tostring())
