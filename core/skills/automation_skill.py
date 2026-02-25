import os
import subprocess
import pyautogui
from datetime import datetime
from core.skills.base import BaseSkill

class AutomationSkill(BaseSkill):
    def __init__(self):
        super().__init__("Automation", "Handles system-level actions like screenshots and locking.")
        self.keywords = ["screenshot", "capture screen", "lock computer", "minimize all", "clear desktop", "hibernate", "brightness"]

    def matches(self, command: str) -> bool:
        return any(word in command for word in self.keywords)

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        
        if "screenshot" in command or "capture" in command:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            # Ensure a screenshots folder exists
            os.makedirs("screenshots", exist_ok=True)
            path = os.path.join("screenshots", filename)
            pyautogui.screenshot(path)
            return {"action": "SPEAK", "text": f"Screen capture saved to your screenshots folder, {name}."}

        if "lock" in command:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return {"action": "SPEAK", "text": "Systems locked. Standing by for your return, Sir."}

        if "minimize" in command or "clear desktop" in command:
            pyautogui.hotkey('win', 'd')
            return {"action": "SPEAK", "text": "Clearing the workspace now."}

        if "hibernate" in command:
            os.system("shutdown /h")
            return {"action": "SPEAK", "text": "Engaging hibernation sequence. Farewell, Sir."}

        if "brightness" in command:
            # Simple brightness control via Powershell (Windows)
            level = 50
            if "up" in command or "increase" in command: level = 80
            if "down" in command or "decrease" in command: level = 20
            
            ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
            return {"action": "SPEAK", "text": f"Adjusting display luminance to {level} percent, Sir."}

        return {}
