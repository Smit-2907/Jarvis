import random
from datetime import datetime
from core.skills.base import BaseSkill

class SystemSkill(BaseSkill):
    def __init__(self):
        super().__init__("System", "Handles core system operations like status, time, and shutdown.")
        self.keywords = ["status", "time", "clock", "date", "who are you", "who is jarvis", "shutdown", "offline", "exit", "goodbye", "sleep", "hello", "hi", "hey"]

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        
        if any(word in command for word in ["hello", "hi", "hey"]):
            return {"action": "SPEAK", "text": f"Gretings, {name}. All systems are active and ready for your instruction."}
            
        if "who are you" in command or "who is jarvis" in command:
            return {"action": "SPEAK", "text": f"I am Jarvis, a personal autonomous intelligence designed by Stark Industries. I am here to facilitate your primary workflows, {name}."}

        if any(word in command for word in ["time", "clock", "date"]):
            return {"action": "SPEAK", "text": f"The current time is {datetime.now().strftime('%I:%M %p')}, Sir."}

        if any(word in command for word in ["system shutdown", "go offline jarvis", "exit system", "goodbye jarvis", "go to sleep now"]):
            return {"action": "LOG", "text": "Exiting", "terminate": True}

        if "status" in command:
            status_phrases = [
                f"All internal systems are nominal, {name}.",
                "Primary logic cores are stable. Connectivity is established at 100 percent.",
                "Environment is clear. Primary functions are at maximum capacity, Sir.",
                "Diagnostics indicate all modules are performing within optimal parameters."
            ]
            return {"action": "SPEAK", "text": random.choice(status_phrases)}

        return {}
