import random
from typing import Dict, List

class ResponseGenerator:
    def __init__(self, mode: str = "Jarvis"):
        self.mode = mode
        
        self.responses: Dict[str, Dict[str, List[str]]] = {
            "Jarvis": {
                "GREETING": [
                    "Welcome back, Sir. I have been keeping the systems idling in your absence. Everything appears to be in order.",
                    "At your service, Sir. Shall we continue where we left off?",
                    "System initialized. Good to see you, Sir. I've updated the diagnostic logs for your review.",
                    "Online and ready, Sir. The environment is stable.",
                    "Greeting, Sir. Always a pleasure to see you back at the console."
                ],
                "FOCUS_START": [
                    "Engaging focus protocols now, Sir. I'll filter out the digital noise and keep a watchful eye.",
                    "Focus mode active. I suggest you stay on course; time is of the essence.",
                    "Deep work session initiated. I'm prioritizing your primary workflow now.",
                    "Locking it down, Sir. Let's make some progress, shall we?"
                ],
                "COACH_SWITCH": [
                    "Sir, you seem to be multitasking quite aggressively. Might I suggest focusing on one task at a time?",
                    "Task switching detected. I'm noting a slight drop in efficiency, Sir. Perhaps we should stick to the current window?",
                    "Pardon me, Sir, but we seem to be drifting away from our objective. Shall I close the distractions?",
                    "Sir, your focus appears to be wavering. I've logged the switch."
                ],
                "USER_LEFT": [
                    "I'll be right here, Sir. Monitoring the background systems while you're away.",
                    "Idle mode engaged. Safe travels, Sir. I'll keep the lights on.",
                    "Standing by for your return, Sir. Everything is secure."
                ],
                "OBJECT_DETECTED": [
                    "Evaluating the frame now, Sir... Ah, it appears to be a {obj}.",
                    "Scanning complete. That looks like a {obj}, if I'm not mistaken.",
                    "I'm fairly certain I see a {obj} in your proximity, Sir.",
                    "I've identified a {obj} in the current view."
                ],
                "OBJECTS_MULTIPLE": [
                    "My sensors are picking up several items: a {obj_str}.",
                    "The room is quite busy, Sir. I can see a {obj_str}.",
                    "I've identified multiple objects here: a {obj_str}.",
                    "Scanning results show a {obj_str}. Quite the collection, Sir."
                ],
                "THINKING": [
                    "One moment while I process that, Sir.",
                    "Evaluating your request... just a second.",
                    "Analyzing the current data streams, Sir.",
                    "Processing... please stand by."
                ]
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
