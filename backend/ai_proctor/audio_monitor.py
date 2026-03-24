import pyaudio
import numpy as np

class AudioMonitor:
    def __init__(self, threshold=0.05):
        self.chunk = 1024
        self.rate = 44100
        self.threshold = threshold
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.rate, 
                                  input=True, frames_per_buffer=self.chunk)

    def is_noisy(self):
        try:
            data = np.frombuffer(self.stream.read(self.chunk, exception_on_overflow=False), dtype=np.int16)
            rms = np.sqrt(np.mean(data**2)) / 32768.0 # Normalize audio
            return rms > self.threshold
        except:
            return False

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()