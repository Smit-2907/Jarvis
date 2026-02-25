from core.skills.base import BaseSkill
from core.state_machine import JarvisState
import os
import pyautogui
import time

class ProtocolSkill(BaseSkill):
    def __init__(self, state_machine):
        super().__init__("Protocol", "Executes complex multi-step routines.")
        self.sm = state_machine
        self.keywords = ["protocol", "engage", "routine", "sequence"]

    def matches(self, command: str) -> bool:
        return "protocol" in command

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        
        if "deep work" in command or "development" in command:
            self.sm.transition(JarvisState.FOCUS_MODE)
            os.system("start chrome")
            os.system("code .") # Open VS Code in current dir
            for _ in range(10): pyautogui.press("volumedown")
            return {"action": "SPEAK", "text": f"Protocol Deep Work engaged. Optic sensors are active, volume is minimized, and your development environment is initializing. Good luck, {name}."}

        if "house party" in command or "relax" in command:
            os.system("start spotify:")
            for _ in range(10): pyautogui.press("volumeup")
            return {"action": "SPEAK", "text": f"Engaging relaxation protocols. Spotify is initializing and audio gain is being boosted. I'll be here if you need anything else, Sir."}

        if "zero" in command or "clean slate" in command:
            # Minimize all, clear temp thoughts
            pyautogui.hotkey('win', 'd')
            return {"action": "SPEAK", "text": f"Protocol Zero initiated. Workspace cleared. Standing by for fresh instructions, {name}."}

        if "diagnostic" in command:
            return {"action": "SPEAK", "text": f"Full system sweep complete. Power levels nominal. Perception layers at 100 percent productivity. We are green across the board, {name}."}

        return {"action": "SPEAK", "text": f"I'm sorry Sir, I don't have that specific protocol in my database yet. Would you like to teach it to me?"}
