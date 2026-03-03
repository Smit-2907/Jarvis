import os
import threading
import subprocess
import time
import random
import re
import signal
from core.event_bus import bus

class TTSEngine:
    def __init__(self, rate: int = 175, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.lock = threading.Lock()
        self.active_process = None
        
        # Advanced Phonetic Phrasing for more human-like flow
        self.phonetics = {
            "Jarvis": "Jarvis",
            "J.A.R.V.I.S.": "Jarvis",
            "Sir": "Sir,",
            "Actually": "Actually,",
            "Interestingly": "Interestingly,",
            "CPU": "C P U",
            "RAM": "Ram",
            "HUD": "Hud",
            "don't": "dont",
            "can't": "cant"
        }

    def _apply_fluency(self, text: str) -> str:
        # Prevent XML entities issues
        text = text.replace("&", "and").replace("<", "").replace(">", "")
        words = text.split()
        new_words = []
        for word in words:
            clean = word.strip(",.!?\"")
            if clean in self.phonetics:
                new_words.append(word.replace(clean, self.phonetics[clean]))
            else:
                new_words.append(word)
        return " ".join(new_words)

    def stop_speaking(self):
        """Forcefully stops the current speech process."""
        if self.active_process:
            try:
                subprocess.run(f"taskkill /F /T /PID {self.active_process.pid}", shell=True, capture_output=True)
                self.active_process = None
                from colorama import Fore
                print(f"\n{Fore.YELLOW}🔇 Audio feed interrupted.")
            except Exception: pass

    def speak(self, text: str):
        """Non-blocking TTS using SSML for high-fidelity human-like prosody."""
        def _speak():
            with self.lock:
                if self.active_process:
                    self.stop_speaking()

                bus.publish("JARVIS_SPEAKING", {"status": True})

                from colorama import Fore, Style
                waves = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
                waveform = "".join(random.choice(waves) for _ in range(15))
                print(f"\n{Fore.CYAN}🔊 JARVIS: {waveform} {Fore.WHITE}{text}{Style.RESET_ALL}", flush=True)
                
                processed_text = self._apply_fluency(text).replace("'", "''")
                
                # Dynamic prosody settings
                # Rate 200 (config) -> ~1.2x multiplier
                prosody_rate = round(self.rate / 165, 2)
                # Pitch -1st (semitones) makes the voice sound more sophisticated/British
                pitch_shift = "-1st" 

                ps_script = f'''
                Add-Type -AssemblyName System.Speech
                $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
                $voices = $synth.GetInstalledVoices()
                $target = $voices | Where-Object {{ $_.VoiceInfo.Culture.Name -like "*en-GB*" -and $_.Enabled }} | Select-Object -First 1
                if (-not $target) {{ $target = $voices | Where-Object {{ $_.VoiceInfo.Culture.Name -like "*en-*" -and $_.Enabled }} | Select-Object -First 1 }}
                if ($target) {{ $synth.SelectVoice($target.VoiceInfo.Name) }}
                $synth.Volume = {int(self.volume * 100)}
                
                $ssml = @"
                <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-GB'>
                    <prosody rate='{prosody_rate}' pitch='{pitch_shift}'>
                        {processed_text}
                    </prosody>
                </speak>
"@
                $synth.SpeakSsml($ssml)
                '''
                
                try:
                    self.active_process = subprocess.Popen(
                        ["powershell", "-NoProfile", "-Command", ps_script],
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    self.active_process.wait()
                    self.active_process = None
                except Exception as e:
                    print(f"❌ TTS Error: {e}")
                finally:
                    bus.publish("JARVIS_SPEAKING", {"status": False})

        threading.Thread(target=_speak, daemon=True).start()


class AutomationEngine:
    def execute_command(self, command: str):
        print(f"⚙️ Executing: {command}")
        pass
