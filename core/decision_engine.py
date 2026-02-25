import time
import json
import os
import re
import random
import difflib
from datetime import datetime
from core.state_machine import JarvisState
from memory.database import ShortTermMemory, DatabaseManager
from personality.response_generator import ResponseGenerator

class DecisionEngine:
    def __init__(self, state_machine, memory: ShortTermMemory, db: DatabaseManager, personality: ResponseGenerator, vision=None):
        self.sm = state_machine
        self.memory = memory
        self.db = db
        self.personality = personality
        self.vision = vision
        self.rules_path = os.path.join("config", "rules.json")
        self.user_memory_path = os.path.join("config", "user_memory.json")
        
        # Expanded Error Correction Map for noisy Windows/Vosk audio
        self.corrections = {
            "canada": "can you",
            "kenya": "can you",
            "horrendous": "focus",
            "obvious": "jarvis",
            "service": "jarvis",
            "database": "jarvis",
            "hell is our": "hello jarvis",
            "over us": "jarvis",
            "it was obvious": "jarvis",
            "to blast you": "2 plus 2",
            "blast you": "plus 2",
            "others": "jarvis",
            "home and": "how many",
            "england": "fingers",
            "either": "are there",
            "dollars": "jarvis",
            "ford": "jarvis",
            "haugen": "how can",
            "lungs": "learn",
            "pinterest": "interest",
            "as am i": "jarvis",
            "my miss me": "my name is",
            "miss me as": "my name is",
            "higher heard": "i heard",
            "what detection": "object detection",
            "see something": "detect objects",
            "holding up": "what am i holding",
            "jobless": "jarvis",
            "dharavish": "jarvis",
            "charvis": "jarvis",
            "garbage": "jarvis",
            "travis": "jarvis",
            "harvest": "jarvis",
            "service": "jarvis",
            "status": "status",
            "see you": "see",
            "look at": "look",
            "who are": "who",
            "time is it": "time",
            "what time": "time",
            "shut down": "shutdown",
            "go to sleep": "shutdown",
            "lock in": "focus",
            "focus mode": "focus"
        }

        # Intent mapping with keywords
        self.intents = {
            "focus_mode": ["focus", "lock in", "deep work", "work", "online"],
            "stop_mode": ["stop", "cancel", "never mind", "back", "idle", "break", "offline", "shutdown", "exit", "goodbye", "sleep"],
            "status_check": ["status", "how are you", "are you okay", "nominal", "doing", "check systems"],
            "vision_check": ["see", "look", "who", "camera", "scanning", "presence"],
            "object_detection": ["what is this", "detect objects", "scan objects", "what do you see", "holding", "identify"],
            "time_check": ["time", "clock", "date"],
            "humor": ["joke", "funny", "laugh", "humour"],
            "math": ["plus", "minus", "times", "divided", "calculate", "what is", "+", "-", "*", "/", "sum"],
            "learning": ["learn", "remember", "means"]
        }
        
        self.jokes = [
            "Why did the developer go broke? Because he used up all his cache.",
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "How many programmers does it take to change a light bulb? None, it's a hardware problem.",
            "There are only 10 kinds of people: those who understand binary, and those who don't.",
            "Why do Java programmers have to wear glasses? Because they don't C#."
        ]

    def _clean_command(self, cmd: str):
        """Pre-processes command to fix common speech recognition errors."""
        # 1. Hard corrections
        sorted_keys = sorted(self.corrections.keys(), key=len, reverse=True)
        for error in sorted_keys:
            if error in cmd:
                cmd = cmd.replace(error, self.corrections[error])
        
        # 2. Key phrase fuzzy matching
        # If the command contains words that sound like intents, steer it there
        words = cmd.split()
        for i_name, i_keywords in self.intents.items():
            for kw in i_keywords:
                for word in words:
                    # If word is very similar to a keyword, replace it
                    if difflib.SequenceMatcher(None, word, kw).ratio() > 0.85:
                        cmd = cmd.replace(word, kw)
        
        return cmd

    def _load_rules(self):
        if os.path.exists(self.rules_path):
            try:
                with open(self.rules_path, 'r') as f:
                    return json.load(f)
            except: pass
        return {}

    def _save_rule(self, trigger, response):
        rules = self._load_rules()
        rules[trigger.lower()] = response
        os.makedirs(os.path.dirname(self.rules_path), exist_ok=True)
        with open(self.rules_path, 'w') as f:
            json.dump(rules, f)

    def _get_user_name(self):
        if os.path.exists(self.user_memory_path):
            try:
                with open(self.user_memory_path, 'r') as f:
                    return json.load(f).get("name", "Sir")
            except: pass
        return "Sir"

    def _set_user_name(self, name: str):
        if len(name.split()) > 2:
            return False
        os.makedirs(os.path.dirname(self.user_memory_path), exist_ok=True)
        with open(self.user_memory_path, 'w') as f:
            json.dump({"name": name}, f)
        return True

    def evaluate(self, event_type: str, data: dict):
        now = time.time()
        name = self._get_user_name()
        
        if event_type == "USER_PRESENT":
            if now - self.memory.get("last_greeting_time", 0) > 1200:
                self.memory.update("last_greeting_time", now)
                return {"action": "SPEAK", "text": f"Welcome back, {name}. I am active and ready for your instructions."}

        elif event_type in ["USER_COMMAND", "WAKE_WORD_DETECTED"]:
            raw_cmd = data.get("command", "").strip().lower()
            if not raw_cmd:
                return {"action": "SPEAK", "text": f"Yes, {name}? I am at your service."}

            cmd = self._clean_command(raw_cmd)
            print(f"🧠 Brain processing: '{raw_cmd}' -> '{cmd}'")

            # 1. Identity & Names
            if "my name is" in cmd:
                new_name = cmd.split("my name is")[-1].strip().replace(".", "").capitalize()
                if self._set_user_name(new_name):
                    return {"action": "SPEAK", "text": f"Very well. I shall address you as {new_name} from now on."}
                else:
                    return {"action": "SPEAK", "text": f"I'm sorry, that name sounds a bit too complex for my current database. Perhaps something shorter, {name}?"}

            if "who are you" in cmd:
                return {"action": "SPEAK", "text": f"I am Jarvis, your personal autonomous intelligence. Always here to assist you, {name}."}

            # 2. Dynamic Rule Learning
            if any(word in cmd for word in self.intents["learning"]) and "means" in cmd:
                match = re.search(r"(?:learn that|remember that)? (.*) means (.*)", cmd)
                if match:
                    t, r = match.groups()
                    self._save_rule(t.strip(), r.strip())
                    return {"action": "SPEAK", "text": f"Acknowledged. I have logged that '{t.strip()}' corresponds to '{r.strip()}'."}

            # Check learned rules
            rules = self._load_rules()
            if cmd in rules:
                return {"action": "SPEAK", "text": rules[cmd]}

            # 3. Object Detection (NEW)
            if any(word in cmd for word in self.intents["object_detection"]):
                if self.vision:
                    objects = self.vision.get_detected_objects()
                    if objects:
                        if len(objects) == 1:
                            resp = self.personality.get_response("OBJECT_DETECTED")
                            return {"action": "SPEAK", "text": resp.format(obj=objects[0])}
                        else:
                            obj_str = ", ".join(objects[:-1]) + " and a " + objects[-1]
                            resp = self.personality.get_response("OBJECTS_MULTIPLE")
                            return {"action": "SPEAK", "text": resp.format(obj_str=obj_str)}
                    else:
                        return {"action": "SPEAK", "text": f"I'm looking, {name}, but I can't quite identify any specific objects in the frame right now. Perhaps if you move the item closer?"}

            # 4. Math Calculation
            if any(word in cmd for word in self.intents["math"]) or re.search(r'[0-9]', cmd):
                try:
                    math_input = cmd.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")
                    expr = re.sub(r'[^0-9+\-*/().]', '', math_input)
                    if expr:
                        res = eval(expr, {"__builtins__": None}, {})
                        math_phrases = [
                            f"According to my calculations, that would be {res}.",
                            f"The result is {res}, Sir.",
                            f"That comes out to {res}.",
                            f"I've computed the value for you: {res}."
                        ]
                        return {"action": "SPEAK", "text": random.choice(math_phrases)}
                except: pass

            # 5. Vision Check (Presence)
            if any(word in cmd for word in self.intents["vision_check"]):
                if self.vision:
                    count = self.vision.get_face_count()
                    if count > 0:
                        return {"action": "SPEAK", "text": f"I see you clearly, {name}. Monitoring your present state."}
                    return {"action": "SPEAK", "text": "I can see the room, but I don't see any faces in the frame."}

            # 6. Modes & System
            if any(word in cmd for word in self.intents["focus_mode"]):
                self.sm.transition(JarvisState.FOCUS_MODE)
                return {"action": "SPEAK", "text": f"Focus mode initiated, {name}. I will now log any potential distractions."}

            if any(word in cmd for word in ["shutdown", "offline", "exit", "goodbye", "sleep"]):
                # Only exit if the command specifically addresses Jarvis or uses a direct command
                if "jarvis" in raw_cmd or "system" in raw_cmd or len(cmd.split()) == 1:
                    return {"action": "LOG", "text": "Exiting", "terminate": True}
                else:
                    print(f"👂 Ignored potential shutdown: '{cmd}' (No direct address)")

                status_phrases = [
                    f"All systems are operational and nominal, {name}.",
                    "The neural network is stable and internal diagnostics are clear, Sir.",
                    "Primary functions are at 100% capacity. We are fully operational.",
                    "No issues to report, Sir. Everything is running smoothly."
                ]
                return {"action": "SPEAK", "text": random.choice(status_phrases)}

            if any(word in cmd for word in self.intents["time_check"]):
                return {"action": "SPEAK", "text": f"The current time is exactly {datetime.now().strftime('%I:%M %p')}."}

            # 7. Small Talk & Humor
            if any(word in cmd for word in ["hello", "hi", "hey"]):
                return {"action": "SPEAK", "text": f"Hello {name}. How can I assist you in your work today?"}

            if any(word in cmd for word in self.intents["humor"]):
                return {"action": "SPEAK", "text": "A little levity? Very well. " + random.choice(self.jokes)}

            if "thank" in cmd:
                return {"action": "SPEAK", "text": f"You are most welcome, {name}."}

            # 8. Fallback
            if len(cmd) > 5:
                return {"action": "SPEAK", "text": f"I'm afraid I didn't quite catch that, {name}. My audio model heard something about '{cmd[:20]}'. Would you care to repeat?"}

        return None
