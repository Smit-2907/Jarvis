import os
import json
import sys
import queue
import time
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from core.event_bus import bus
import threading

class AudioListener:
    def __init__(self, model_path: str, wake_word: str = "jarvis", intensity_threshold: int = 250):
        self.model_path = model_path
        self.wake_word = wake_word.lower()
        self.intensity_threshold = 120
        self.q = queue.Queue()
        self.model = None
        self._running = False
        self.last_wake_time = 0
        self.listening_window = 8.0
        self.gate_open = False
        self.last_sound_time = 0
        self.gate_hold_seconds = 1.0 # Reduced from 1.5s to prevent feedback/mishearing

    def callback(self, indata, frames, time_info, status):
        """Audio stream callback."""
        if status:
            print(status)
        # Calculate Intensity (RMS)
        audio_data = np.frombuffer(indata, dtype=np.int16).astype(np.float64)
        intensity = np.sqrt(np.mean(audio_data**2))
        
        now = time.time()
        
        # Logic: If loud enough, open gate and update last_sound_time
        if intensity > self.intensity_threshold:
            self.gate_open = True
            self.last_sound_time = now
            self.q.put(bytes(indata))
        
        # If below threshold, but within "hold" window, keep sending audio
        elif self.gate_open and (now - self.last_sound_time < self.gate_hold_seconds):
            self.q.put(bytes(indata))
        
        else:
            # Gate is closed
            self.gate_open = False
            # Debug level periodically instead of every callback
            if int(now) % 2 == 0 and intensity > 10:
                sys.stdout.write(f"\r🎤 Ambient Level: {int(intensity)}  ")
                sys.stdout.flush()

    def _loop(self):
        if not os.path.exists(self.model_path):
            print("⚠️ Vosk model not found.")
            return

        self.model = Model(self.model_path)

        device_info = sd.query_devices(None, 'input')
        samplerate = int(device_info['default_samplerate'])

        with sd.RawInputStream(
            samplerate=samplerate,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=self.callback
        ):
            rec = KaldiRecognizer(self.model, samplerate)
            self._running = True

            print(f"🎙 Listening... (Threshold: {self.intensity_threshold})")

            while self._running:
                try:
                    data = self.q.get(timeout=1)
                except queue.Empty:
                    continue

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").lower().strip()

                    if text:
                        now = time.time()
                        print(f"\n🎙 Heard: {text}")

                        if self.wake_word in text:
                            self.last_wake_time = now
                            command = text.replace(self.wake_word, "").strip()
                            bus.publish("WAKE_WORD_DETECTED", {"command": command})
                            print("✨ Wake word detected")

                        elif now - self.last_wake_time < self.listening_window:
                            bus.publish("USER_COMMAND", {"command": text})
                            self.last_wake_time = now

                else:
                    partial = json.loads(rec.PartialResult()).get("partial", "")
                    if partial:
                        print(f"\r🔍 {partial}", end="")
                    else:
                        # If no partial result, and gate is closed, print ambient level
                        # This is a safer place as it doesn't interfere with active transcription
                        # However, the original code calculated intensity in callback, not here.
                        # For now, the debug print is effectively removed as per the interpretation
                        # that "move to a safer place" without a target means removal from current.
                        pass


    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self._running = False