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
import collections

class AudioListener:
    def __init__(self, model_path: str, wake_word: str = "jarvis", intensity_threshold: int = 150):
        self.model_path = model_path
        self.wake_word = wake_word.lower()
        self.intensity_threshold = intensity_threshold
        self.q = queue.Queue()
        self.model = None
        self._running = False
        
        # Advanced Gating
        self.pre_buffer = collections.deque(maxlen=10) # ~0.5s of audio @ 16khz (8000 blocksize)
        self.gate_open = False
        self.last_sound_time = 0
        self.gate_hold_seconds = 1.8 # Increased for flow
        
        # Adaptive Thresholding
        self.ambient_levels = collections.deque(maxlen=50)
        self.calibrating = True
        self.calibration_start = time.time()
        self.listening_window = 8.0
        self.last_wake_time = 0
        
        # Filtering
        self.last_audio_data = None
        self.is_speaking = False
        
        # Subscribe to speech events to avoid hearing himself
        bus.subscribe("JARVIS_SPEAKING", self._handle_speech_event)

    def _handle_speech_event(self, data: dict):
        self.is_speaking = data.get("status", False)
        if self.is_speaking:
            # Clear pre-buffer when JARVIS starts talking to avoid stale audio
            self.pre_buffer.clear()
            self.gate_open = False

    def callback(self, indata, frames, time_info, status):
        """High-fidelity audio callback with self-deafness and pre-buffering."""
        if self.is_speaking:
            return # JARVIS is talking, don't listen to the feedback
            
        if status: print(status)
        
        audio_data = np.frombuffer(indata, dtype=np.int16).astype(np.float64)
        
        # Simple Low-Pass Filter (Smoothing)
        if self.last_audio_data is not None:
            audio_data = 0.8 * audio_data + 0.2 * self.last_audio_data
        self.last_audio_data = audio_data
        
        intensity = np.sqrt(np.mean(audio_data**2))
        now = time.time()

        # 1. Calibration phase (first 3 seconds)
        if self.calibrating:
            self.ambient_levels.append(intensity)
            if now - self.calibration_start > 3.0:
                avg_ambient = np.mean(self.ambient_levels)
                # Auto-adjust threshold: config value + ambient floor
                self.intensity_threshold = self.intensity_threshold + int(avg_ambient * 1.5)
                # Cap it at 600 to prevent deafness
                self.intensity_threshold = min(self.intensity_threshold, 600)
                self.calibrating = False
                print(f"\n✅ [AUDIO] Calibration Complete. Ambient: {int(avg_ambient)} | Threshold: {self.intensity_threshold}")
            return

        # 2. Gating Logic
        if intensity > self.intensity_threshold:
            if not self.gate_open:
                # Triggered! Flush pre-buffer first
                while self.pre_buffer:
                    self.q.put(self.pre_buffer.popleft())
                self.gate_open = True
            
            self.last_sound_time = now
            self.q.put(bytes(indata))
        
        elif self.gate_open and (now - self.last_sound_time < self.gate_hold_seconds):
            # Still in the "hold" window
            self.q.put(bytes(indata))
        
        else:
            # Silence: add to pre-buffer
            self.gate_open = False
            self.pre_buffer.append(bytes(indata))
            
            # Ambient logging
            if int(now) % 3 == 0 and intensity > 5:
                sys.stdout.write(f"\r🎤 Ambient: {int(intensity)}/{self.intensity_threshold}  ")
                sys.stdout.flush()

    def _loop(self):
        print(f"🎙 [DEBUG] Audio thread started. Model Path: {self.model_path}")
        try:
            if not os.path.exists(self.model_path):
                print(f"⚠️ [ERROR] Vosk model folder NOT FOUND at {self.model_path}")
                return

            print(f"🎙 [SYSTEM] Loading high-fidelity hearing model... (This will take 30s+)")
            start_time = time.time()
            self.model = Model(self.model_path)
            print(f"✅ [SYSTEM] Model loaded in {time.time() - start_time:.1f}s.")

            try:
                device_info = sd.query_devices(None, 'input')
                samplerate = int(device_info['default_samplerate'])
                print(f"🎙 [DEBUG] Input Device: {device_info['name']} | Rate: {samplerate}Hz")
            except Exception as e:
                samplerate = 16000
                print(f"⚠️ [WARNING] Device detection failed, defaulting to 16kHz. Error: {e}")

            with sd.RawInputStream(
                samplerate=samplerate,
                blocksize=4000,
                dtype='int16',
                channels=1,
                callback=self.callback
            ):
                rec = KaldiRecognizer(self.model, samplerate)
                self._running = True
                print(f"🎤 [SYSTEM] JARVIS is now actively listening. Threshold: {self.intensity_threshold}")

                while self._running:
                    try:
                        data = self.q.get(timeout=1)
                    except queue.Empty:
                        continue
                    
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "").lower().strip()
                        if text:
                            print(f"\n🎙 Heard: {text}")
                            now = time.time()
                            if self.wake_word in text:
                                self.last_wake_time = now
                                command = text.replace(self.wake_word, "").strip()
                                bus.publish("WAKE_WORD_DETECTED", {"command": command})
                            elif now - self.last_wake_time < self.listening_window:
                                bus.publish("USER_COMMAND", {"command": text})
                                self.last_wake_time = now
                    else:
                        partial = json.loads(rec.PartialResult()).get("partial", "")
                        if partial:
                            sys.stdout.write(f"\r🔍 {partial}")
                            sys.stdout.flush()

        except Exception as e:
            print(f"❌ [CRITICAL] Audio Thread Exception: {e}")
            import traceback
            traceback.print_exc()


    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self._running = False