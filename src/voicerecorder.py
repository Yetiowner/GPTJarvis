import threading
import queue
import time
import sounddevice as sd
import soundfile as sf
import numpy as np
import os
from pydub import AudioSegment
import sys

class Recorder:
    def __init__(self, filename="recording"):
        self.frames = queue.Queue()
        self.samplerate = 44100
        self.channels = sd.default.channels
        self.filename = filename
        self.is_recording = False

    def start_recording(self):
        self.frames.queue.clear()
        self.stream = sd.InputStream(channels=1, blocksize=2048, samplerate=self.samplerate, callback=self._callback)
        self.thread = threading.Thread(target=self._record)
        self.is_recording = True
        self.thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.thread.join()
        self._save_file()

    def _record(self):
        with self.stream:
            sd.sleep(int(0.2 * 1000))
            self.stream.start()
            while self.is_recording:
                time.sleep(0.1)
            self.stream.stop()

    def _callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.frames.put(indata.copy())

    def _save_file(self):
        data = np.concatenate([self.frames.get() for i in range(self.frames.qsize())])
        filename_wav = f'{self.filename}.wav'
        sf.write(filename_wav, data, self.samplerate)

        audio = AudioSegment.from_wav(filename_wav)
        filename_mp3 = f'{self.filename}.mp3'
        audio.export(filename_mp3, format='mp3')
        
        os.remove(filename_wav)