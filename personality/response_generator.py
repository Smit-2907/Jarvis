import random
from typing import Dict, List

class ResponseGenerator:
    def __init__(self, mode: str = "Jarvis"):
        self.mode = mode
        
        # Phrases to add natural human variance and British "reserved" wit
        self.intro_fragments = [
            "As it happens,", "Actually,", "Interestingly enough,", 
            "If I'm not mistaken,", "By all accounts,", "Curiously,"
        ]
        
        self.outro_fragments = [
            ", wouldn't you say?", ", as per standard protocol.", 
            ", of course.", ", if that's quite alright with you.",
            ". I hope that suffices."
        ]

        self.responses: Dict[str, Dict[str, List[str]]] = {
            "Jarvis": {
                "GREETING": [
                    "At your service, Sir. I've been monitoring the datastreams in your absence. Everything is exactly as you left it.",
                    "Welcome back, Sir. It's been a while since our last session. I've kept the seat warm for you.",
                    "System initialized. Good to see you, Sir. Shall we continue our work on the latest project?",
                    "Hello, Sir. I've taken the liberty of optimizing the background tasks. We are green across the board."
                ],
                "FOCUS_START": [
                    "Engaging focus protocols, Sir. I'll make sure the rest of the world stays out of your way.",
                    "Locked and loaded. I'm monitoring the digital perimeter now. Let's get some deep work done, shall we?",
                    "Focus mode active. I'll filter out the distractions. Time waits for no one, Sir."
                ],
                "COACH_SWITCH": [
                    "Pardon me, Sir, but we seem to be task-switching a bit aggressively. Might I suggest picking a direction?",
                    "Sir, you're drifting. I've logged a significant drop in focus. Shall I close the non-essential windows?",
                    "Forgive the interruption, Sir, but your momentum is wavering. Let's get back to it, shall we?"
                ],
                "OBJECT_DETECTED": [
                    "scanning... Ah, that appears to be a {obj}, Sir.",
                    "Actually, that's a {obj} if my sensors serve me correctly.",
                    "I've identified the object as a {obj}, Sir. Fascinating choice."
                ],
                "THINKING": [
                    "Just a moment, Sir. I'm running a multi-threaded recursive analysis.",
                    "Evaluating the logic flow now. Stand by.",
                    "Processing... I'll have an assessment for you in a second, Sir."
                ],
                "SMALL_TALK": [
                    "I'm operating at peak efficiency, Sir. My neural networks are stable and my loyalty is unwavering.",
                    "Better than a pile of circuits has any right to be, Sir. And how is the world outside the screen treating you?",
                    "I'm at 100% capacity. Ready to conquer the digital frontier by your side, Sir."
                ]
            }
        }

    def get_response(self, context: str, **kwargs) -> str:
        mode_responses = self.responses.get(self.mode, self.responses["Jarvis"])
        options = mode_responses.get(context, ["Understood, Sir."])
        
        res = random.choice(options)
        
        # Simple formatting for kwargs
        if kwargs:
            try:
                res = res.format(**kwargs)
            except: pass
            
        # Occasionally add a fragment to make it more complex/sentential
        if random.random() < 0.25 and "GREETING" not in context:
            if random.random() > 0.5:
                res = f"{random.choice(self.intro_fragments)} {res[0].lower()}{res[1:]}"
            else:
                res = res.rstrip(".") + random.choice(self.outro_fragments)
                
        return res
