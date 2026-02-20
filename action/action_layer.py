import os
import threading
import subprocess
from core.event_bus import bus

class TTSEngine:
    def __init__(self, rate: int = 175, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.lock = threading.Lock()

    def speak(self, text: str):
        """Non-blocking TTS using PowerShell. Optimized for an 'Iron Man' Jarvis vibe."""
        def _speak():
            with self.lock:
                print(f"🔊 Jarvis: {text}")
                # Escape single quotes and backticks for PowerShell
                sanitized_text = text.replace("'", "''").replace("`", "``")
                
                # PowerShell script to find a British voice (en-GB) and speak with it
                # If no British voice is found, it falls back to the default system voice.
                command = f'''
                Add-Type -AssemblyName System.Speech;
                $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer;
                $voices = $speak.GetInstalledVoices();
                $jarvisVoice = $voices | Where-Object {{ $_.VoiceInfo.Culture.Name -eq "en-GB" -and $_.Enabled }} | Select-Object -First 1;
                
                if ($jarvisVoice -ne $null) {{
                    $speak.SelectVoice($jarvisVoice.VoiceInfo.Name);
                }}
                
                $speak.Rate = {(self.rate - 175) // 10};
                $speak.Volume = {int(self.volume * 100)};
                $speak.Speak('{sanitized_text}');
                '''
                try:
                    subprocess.run(["powershell", "-Command", command], capture_output=True)
                except Exception as e:
                    print(f"❌ TTS Error: {e}")

        threading.Thread(target=_speak, daemon=True).start()

class AutomationEngine:
    def execute_command(self, command: str):
        import pyautogui
        import subprocess
        
        print(f"⚙️ Executing: {command}")
        if "focus" in command:
            pass
        elif "close" in command and "distractions" in command:
            distractions = ["Spotify.exe", "Discord.exe"]
            for app in distractions:
                try:
                    subprocess.run(["taskkill", "/F", "/IM", app], capture_output=True)
                except:
                    pass
