import random
from typing import Dict, List

class ResponseGenerator:
    def __init__(self, mode: str = "Jarvis"):
        self.mode = mode
        
        self.responses: Dict[str, Dict[str, List[str]]] = {
            "Jarvis": {
                "GREETING": [
                    "Welcome back, Sir. I have been keeping the systems idling in your absence.",
                    "At your service, Sir. Shall we continue with the project?",
                    "System initialized. Good to see you, Sir."
                ],
                "FOCUS_START": [
                    "Engaging focus protocols now, Sir. I'll filter out the noise.",
                    "Focus mode active. I suggest you stay on course.",
                    "Deep work session initiated. I'm keeping a watchful eye on your progress."
                ],
                "COACH_SWITCH": [
                    "Sir, you seem to be multitasking quite aggressively. Might I suggest focusing on one task?",
                    "Task switching detected. I'm noting a drop in efficiency, Sir.",
                    "Pardon me, Sir, but we seem to be drifting away from our objective."
                ],
                "USER_LEFT": [
                    "I'll be right here, Sir. Monitoring the background.",
                    "Idle mode engaged. Safe travels, Sir."
                ],
            },
            "Professional": {
                "GREETING": ["Good day. Shall we resume our session?", "Welcome back. I am ready for your instructions."],
                "FOCUS_START": ["Focus mode engaged. Minimizing distractions.", "Deep work timer started. I will monitor for interruptions."],
                "COACH_SWITCH": ["You have switched tasks frequently. Please maintain focus on your primary objective."],
                "USER_LEFT": ["Context saved. I will be awaiting your return."],
            },
            "Friendly": {
                "GREETING": ["Hey there! Ready to get some work done?", "Welcome back! What are we building today?", "Good to see you! Ready to focus?"],
                "FOCUS_START": ["Awesome, let's lock in! Distractions are now silenced.", "Focus mode on! You've got this."],
                "COACH_SWITCH": ["Hey, seeing quite a few switches here. Let's try to stick to one thing for a bit! :)"],
                "USER_LEFT": ["Take care! I'll be right here when you're back."],
            }
        }

    def get_response(self, context: str) -> str:
        mode_responses = self.responses.get(self.mode, self.responses["Jarvis"])
        options = mode_responses.get(context, ["Understood, Sir."])
        return random.choice(options)
