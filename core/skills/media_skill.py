import pyautogui
from core.skills.base import BaseSkill

class MediaSkill(BaseSkill):
    def __init__(self):
        super().__init__("Media", "Controls system volume and media playback.")
        self.keywords = ["volume", "mute", "unmute", "music", "play", "pause", "skip", "next", "previous", "track"]

    def matches(self, command: str) -> bool:
        return any(word in command for word in self.keywords)

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        
        # Volume
        if "volume up" in command or "louder" in command:
            for _ in range(5):
                pyautogui.press("volumeup")
            return {"action": "SPEAK", "text": f"Increasing volume for you, {name}."}
            
        if "volume down" in command or "quieter" in command:
            for _ in range(5):
                pyautogui.press("volumedown")
            return {"action": "SPEAK", "text": f"Lowering the volume now, {name}."}
            
        if "mute" in command and "unmute" not in command:
            pyautogui.press("volumemute")
            return {"action": "SPEAK", "text": "Systems muted, Sir."}
            
        if "unmute" in command:
            pyautogui.press("volumemute")
            return {"action": "SPEAK", "text": "Restoring audio feed, Sir."}

        # Media Keys
        if "pause" in command or "stop music" in command:
            pyautogui.press("playpause")
            return {"action": "SPEAK", "text": "Pausing playback, Sir."}
            
        if "play" in command or "resume" in command:
            pyautogui.press("playpause")
            return {"action": "SPEAK", "text": "Resuming media, {name}."}
            
        if "next" in command or "skip" in command:
            pyautogui.press("nexttrack")
            return {"action": "SPEAK", "text": "Very well. Skipping to the next track."}
            
        if "previous" in command:
            pyautogui.press("prevtrack")
            return {"action": "SPEAK", "text": "Returning to the previous track, Sir."}

        return {}
