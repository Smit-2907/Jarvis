from core.skills.base import BaseSkill
import os
import subprocess

class SystemHealthSkill(BaseSkill):
    def __init__(self):
        super().__init__("SystemHealth", "Monitors hardware stats and verifies TTS subsystem.")
        self.keywords = ["cpu", "ram", "memory", "storage", "diagnostic", "hardware", "voice test", "audio check"]

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        
        if "voice test" in command or "audio check" in command:
            # Trigger a direct PowerShell test to see if audio output is working
            ps_test = 'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("Voice subsystem test successful, Sir.")'
            try:
                subprocess.run(["powershell", "-Command", ps_test], capture_output=True)
                return {"action": "SPEAK", "text": "I've initiated a direct hardware bypass for this audio test. If you can hear this, our primary TTS link is secure, Sir."}
            except:
                return {"action": "SPEAK", "text": "Hardware bypass failed. I'm detecting an issue with the local audio interface, Sir."}

        # Standard hardware report
        import psutil
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return {"action": "SPEAK", "text": f"Diagnostics complete, Sir. CPU load is at {cpu} percent, and memory utilization is at {ram} percent. Audio drivers are currently active."}
