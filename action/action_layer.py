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
        
        # Phonetic replacements for smoother Microsoft British voice
        self.phonetics = {
            "Jarvis": "Jarvis",
            "J.A.R.V.I.S.": "Jarvis",
            "Sir": "Sir,",
            "Actually": "Actually,",
            "Interestingly": "Interestingly,",
            "CPU": "C P U",
            "RAM": "Ram",
            "HUD": "Hud"
        }

    def _apply_fluency(self, text: str) -> str:
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
                # On Windows, we need to kill the process tree to stop PowerShell properly
                subprocess.run(f"taskkill /F /T /PID {self.active_process.pid}", shell=True, capture_output=True)
                self.active_process = None
                from colorama import Fore
                print(f"\n{Fore.YELLOW}🔇 Audio feed interrupted by user command.")
            except Exception as e:
                print(f"❌ Error stopping speech: {e}")

    def speak(self, text: str):
        """Non-blocking TTS using Windows System.Speech with interruptible process control."""
        def _speak():
            with self.lock:
                # If already speaking, we don't necessarily want to stack them, 
                # but for simplicity we allow sequential. However, we should stop prev one if preferred.
                # In this companion mode, we'll stop the previous if a new one starts.
                if self.active_process:
                    self.stop_speaking()

                # Signal that JARVIS is starting to speak
                bus.publish("JARVIS_SPEAKING", {"status": True})

                from colorama import Fore, Style
                waves = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
                waveform = "".join(random.choice(waves) for _ in range(25))
                print(f"\n{Fore.CYAN}🔊 JARVIS: {waveform} {Fore.WHITE}{text}{Style.RESET_ALL}", flush=True)
                
                processed_text = self._apply_fluency(text).replace("'", "''")
                sentences = re.split(r'(?<=[.?!])\s+', processed_text)
                
                script_body = ""
                for s in sentences:
                    if not s.strip(): continue
                    local_rate = int((self.rate - 175) / 10) + random.randint(-1, 0)
                    script_body += f'''
                    $synth.Rate = {local_rate}
                    $synth.Speak('{s.strip()}')
                    Start-Sleep -Milliseconds 150
                    '''

                ps_script = f'''
                Add-Type -AssemblyName System.Speech
                $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
                $voices = $synth.GetInstalledVoices()
                $target = $voices | Where-Object {{ $_.VoiceInfo.Culture.Name -like "*en-GB*" -and $_.Enabled }} | Select-Object -First 1
                if (-not $target) {{ $target = $voices | Where-Object {{ $_.VoiceInfo.Culture.Name -like "*en-*" -and $_.Enabled }} | Select-Object -First 1 }}
                if ($target) {{ $synth.SelectVoice($target.VoiceInfo.Name) }}
                $synth.Volume = {int(self.volume * 100)}
                {script_body}
                '''
                
                try:
                    # Use Popen to keep track of the process handle for interruptions
                    self.active_process = subprocess.Popen(
                        ["powershell", "-NoProfile", "-Command", ps_script],
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    self.active_process.wait()
                    self.active_process = None
                except Exception as e:
                    print(f"❌ TTS Execution Error: {e}")
                finally:
                    # Always signal that JARVIS has finished speaking
                    bus.publish("JARVIS_SPEAKING", {"status": False})

        threading.Thread(target=_speak, daemon=True).start()

class AutomationEngine:
    def execute_command(self, command: str):
        print(f"⚙️ Executing: {command}")
        pass
