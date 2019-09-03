import sys
import importlib
import inspect
from movie import Movie
from movie_out import MovieOutput
import numpy as np
import threading
import multiprocessing
from queue import Queue


class effect_thread(threading.Thread):
    def __init__(self, effect, frame, current_frame, applied_frames):
        threading.Thread.__init__(self)
        self.effect = effect
        self.frame = frame
        self.current_frame = current_frame
        self.applied_frames = applied_frames

    def run(self):
        self.applied_frames[0] = self.effect.apply(self.frame, self.current_frame)


if __name__ == '__main__':
    movie = Movie(sys.argv[1], 0)
    output = None
    effect_name = sys.argv[2].split("=")[0]
    effect_params = sys.argv[2][len(effect_name) + 1:]
    effect = None
    effect_module = importlib.import_module(effect_name)
    for name, obj in inspect.getmembers(effect_module):
        if inspect.isclass(obj) and obj.__name__.lower() == effect_name.lower():
            effect = obj(effect_params, movie)
    n_threads = 1
    if effect.allow_multiprocessing:
        n_threads = multiprocessing.cpu_count()
        print("using %i threads" % n_threads)
    thread_queue = None
    frame_queue = None
    if effect.allow_multiprocessing:
        thread_queue = Queue(n_threads)
        frame_queue = Queue(n_threads)
    while movie.has_frames:
        frame = movie.get_next_frame()
        current_frame = movie.current_frame
        if frame is not None:
            if effect.allow_multiprocessing:
                applied_frames = [None]
                thread = effect_thread(effect, frame, current_frame, applied_frames)
                thread.start()
                thread_queue.put(thread)
                frame_queue.put(applied_frames)
                if thread_queue.full():
                    thread_queue.get().join()
                    applied_frame = frame_queue.get()[0]
                else:
                    continue
            else:
                applied_frame = effect.apply(frame, current_frame)
            movie.current_frame = current_frame
            if applied_frame is not None:
                if output is None:
                    output = MovieOutput(sys.argv[-1], applied_frame.shape, movie.average_frame_rate)
                output.append(np.clip(applied_frame, 0, 255))
    if effect.allow_multiprocessing:
        while not thread_queue.empty():
            thread_queue.get().join()
            applied_frame = frame_queue.get()[0]
            if applied_frame is not None:
                output.append(np.clip(applied_frame, 0, 255))
    while effect.has_frames:
        applied_frame = effect.next_frame()
        if applied_frame is not None:
            output.append(np.clip(applied_frame, 0, 255))
