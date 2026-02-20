import os
import json
import sys
import queue
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from core.event_bus import bus
import threading

class AudioListener:
    def __init__(self, model_path: str, wake_word: str = "jarvis"):
        self.model_path = model_path
        self.wake_word = wake_word.lower()
        self.q = queue.Queue()
        self.model = None
        self._running = False
        self.last_wake_time = 0
        self.listening_window = 8.0 # Seconds to keep "ears open" after hearing wake word

    def callback(self, indata, frames, time, status):
        """Audio stream callback."""
        self.q.put(bytes(indata))

    def listen_loop(self):
        if not os.path.exists(self.model_path):
            print(f"⚠️ Vosk model not found at {self.model_path}. Audio commands disabled.")
            return

        try:
            self.model = Model(self.model_path)
            device_info = sd.query_devices(None, 'input')
            samplerate = int(device_info['default_samplerate'])
            
            with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                                   channels=1, callback=self.callback):
                rec = KaldiRecognizer(self.model, samplerate)
                self._running = True
                print("🎙 Jarvis is listening... (Say 'Jarvis' to start)")
                
                while self._running:
                    data = self.q.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "").lower().strip()
                        
                        if text:
                            now = time.time()
                            print(f"🎙 Heard: {text}")
                            
                            # 1. Check for wake word
                            if self.wake_word in text:
                                self.last_wake_time = now
                                cmd = text.replace(self.wake_word, "").strip()
                                bus.publish("WAKE_WORD_DETECTED", {"command": cmd})
                                print("✨ Wake word detected!")
                            
                            # 2. Check if we are in the "active conversation" window
                            elif now - self.last_wake_time < self.listening_window:
                                bus.publish("USER_COMMAND", {"command": text})
                                # Reset timer to keep the window open during active talking
                                self.last_wake_time = now
                    else:
                        # Partial results for feedback
                        partial = json.loads(rec.PartialResult()).get("partial", "")
                        if partial:
                            sys.stdout.write(f"\r🔍 {partial}      ")
                            sys.stdout.flush()
                            
        except Exception as e:
            print(f"❌ Audio error: {e}")

    def start(self):
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def stop(self):
        self._running = False
