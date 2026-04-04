import pyaudio
import numpy as np
import threading
import time

class AudioMonitor:
    def __init__(self, threshold=150):
        self.threshold = threshold
        self.is_monitoring = False
        self.audio_violation = False
        self.last_violation_time = 0
        self.thread = None
        self.p = None
        self.stream = None

    def start(self):
        self.is_monitoring = True
        self.audio_violation = False
        self.last_violation_time = 0
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_monitoring = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()

    def _monitor_loop(self):
        self.p = pyaudio.PyAudio()
        
        try:
            device_info = self.p.get_default_input_device_info()
            device_idx = device_info['index']
            
            # Dynamically fetch the mic's preferred settings so Intel arrays don't flatline
            rate = int(device_info['defaultSampleRate'])
            channels = min(2, int(device_info['maxInputChannels'])) 
            
            print(f"\n[AUDIO DEBUG] Connected to Mic: {device_info.get('name')}")
            print(f"[AUDIO DEBUG] Using settings -> Rate: {rate}, Channels: {channels}")
            
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=channels,
                                      rate=rate,
                                      input=True,
                                      input_device_index=device_idx,
                                      frames_per_buffer=1024)
            
            print("[AUDIO DEBUG] Listening for noise...\n")
            
            loop_count = 0
            while self.is_monitoring:
                data = np.frombuffer(self.stream.read(1024, exception_on_overflow=False), dtype=np.int16)
                rms = np.sqrt(np.mean(np.square(data.astype(np.float32))))
                
                # Unconditionally print the volume every 20 loops (~1 second)
                loop_count += 1
                if loop_count % 20 == 0:
                    print(f"-> Mic check: Current Volume Level is {rms:.1f}")

                if rms > self.threshold:
                    if not self.audio_violation:
                        print(f"!!! TRIGGERED LOUD NOISE (Volume: {rms:.1f}) !!!")
                    self.audio_violation = True
                    self.last_violation_time = time.time()
                else:
                    if time.time() - self.last_violation_time > 2.0:
                        self.audio_violation = False
                        
                time.sleep(0.05)
                
        except Exception as e:
            print(f"[AUDIO ERROR] Crashed: {e}")
        finally:
            self.is_monitoring = False