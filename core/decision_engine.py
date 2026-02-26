import time
import json
import os
import random
from datetime import datetime

# Core Imports
from core.state_machine import JarvisState
from memory.database import ShortTermMemory, DatabaseManager
from memory.conversation_history import ConversationHistory
from personality.response_generator import ResponseGenerator

# Skill Imports
from core.skills.system_skill import SystemSkill
from core.skills.math_skill import MathSkill
from core.skills.vision_skill import VisionSkill
from core.skills.learning_skill import LearningSkill
from core.skills.productivity_skill import ProductivitySkill
from core.skills.fun_skill import FunSkill
from core.skills.system_health_skill import SystemHealthSkill
from core.skills.media_skill import MediaSkill
from core.skills.app_launcher_skill import AppLauncherSkill
from core.skills.protocol_skill import ProtocolSkill
from core.skills.web_search_skill import WebSearchSkill
from core.skills.automation_skill import AutomationSkill
from core.skills.tactical_vision_skill import TacticalVisionSkill
from core.skills.deep_thought_skill import DeepThoughtSkill
from core.skills.conversation_skill import ConversationSkill
from core.skills.omni_brain_skill import OmniBrainSkill
from core.skills.vision_learning_skill import VisionLearningSkill

class DecisionEngine:
    def __init__(self, state_machine, memory: ShortTermMemory, db: DatabaseManager, personality: ResponseGenerator, vision=None):
        self.sm = state_machine
        self.memory = memory
        self.db = db
        self.personality = personality
        self.vision = vision
        self.chat_history = ConversationHistory(capacity=8)
        
        self.rules_path = os.path.join("config", "rules.json")
        self.user_memory_path = os.path.join("config", "user_memory.json")

        self.skills = [
            ProtocolSkill(self.sm),
            LearningSkill(self.rules_path, self.user_memory_path),
            OmniBrainSkill(), # Primary Intelligence
            AutomationSkill(),
            WebSearchSkill(),
            VisionLearningSkill(),
            AppLauncherSkill(),
            TacticalVisionSkill(),
            ProductivitySkill(self.sm),
            MediaSkill(),
            SystemHealthSkill(),
            VisionSkill(),
            MathSkill(),
            FunSkill(),
            SystemSkill()
        ]
        
        self.corrections = {
            "canada": "can you", "kenya": "can you", "horrendous": "focus",
            "obvious": "jarvis", "service": "jarvis", "database": "jarvis",
            "hell is our": "hello jarvis", "over us": "jarvis", "it was obvious": "jarvis",
            "holding up": "what am i holding", "jobless": "jarvis", "dharavish": "jarvis",
            "charvis": "jarvis", "garbage": "jarvis", "travis": "jarvis",
            "harvest": "jarvis", "see you": "see", "look at": "look",
            "who are": "who", "time is it": "time", "what time": "time",
            "shut down": "shutdown", "go to sleep": "shutdown", "lock in": "focus",
            "focus mode": "focus", "system hill": "system health",
            "charges check": "jarvis check", "nuclear billy": "you clearly",
            "you nuclear": "you clearly", "i needed a search torture": "i need a search for",
            "search torture": "search for", "how are u": "how are you",
            "status sessoins": "focus sessions", "he didn't": "hidden",
            "give mjarvis": "give me jarvis", "jarvijarvis": "jarvis",
            "who you again": "who are you again", "day gping": "day going",
            "search voucher": "search for", "search warrant": "search for",
            "years": "sir", "for years": "sir", "active and ready for years": "active and ready for sir",
            "pigeon": "vision", "visit": "vision", "i'd apply": "identify", "i'd enter fee": "identify",
            "old in": "holding", "cold in": "holding", "what am i old inside": "what am i holding",
            "scan the room": "scan the room", "scandalous": "scan the room", "skandham": "scan the room",
            "look at me": "see me", "hear me": "you there", "charles": "jarvis", "dharavi": "jarvis",
            "shows hours": "are you", "do ever": "do you ever", "ihat": "what", "myve": "i've",
            "listen to have": "jarvis", "of his do": "do you", "how do you saw": "how are you",
            "he's very": "jarvis", "is thereir": "jarvis",
            "i read years": "jarvis", "i met": "jarvis", "hines me": "see me",
            "rightas your": "how is your", "whatever was": "whatever",
            "might be": "jarvis", "as youweir": "as you were",
            "ittify": "identify", "i was do i": "do you", "daughter is do": "jarvis do",
            "is there": "jarvis", "service": "jarvis", "configure": "computer",
            "configured": "computer", "hell of a": "hello jarvis",
            "u n hurt me": "can you hear me", "genres": "jarvis",
            "golf land": "offline", "go offline and": "go offline",
            "can you here me": "can you hear me", "stop dollars": "stop",
            "stop jarvis": "stop", "i'm good": "shutdown", "i'm listening": "jarvis",
            "stark": "stark", "ropen": "open", "hopen": "open", "lopen": "open",
            "tell me mouse": "tell me about", "use latest": "news"
        }

    def _clean_command(self, cmd: str):
        sorted_keys = sorted(self.corrections.keys(), key=len, reverse=True)
        for error in sorted_keys:
            if error in cmd:
                cmd = cmd.replace(error, self.corrections[error])
        return cmd

    def _get_user_name(self):
        if os.path.exists(self.user_memory_path):
            try:
                with open(self.user_memory_path, 'r') as f:
                    return json.load(f).get("name", "Sir")
            except: pass
        return "Sir"

    def evaluate(self, event_type: str, data: dict):
        now = time.time()
        user_name = self._get_user_name()
        
        # Idle -> Social timeout
        if self.sm.current_state == JarvisState.CHATTING:
            if now - self.sm.last_transition_time > 60:
                self.sm.transition(JarvisState.IDLE)

        # 1. Passive Event Handling
        if event_type == "USER_PRESENT":
            if now - self.memory.get("last_greeting_time", 0) > 1200:
                self.memory.update("last_greeting_time", now)
                resp = self.personality.get_response("GREETING")
                self.chat_history.add("JARVIS", resp)
                return {"action": "SPEAK", "text": resp}

        elif event_type == "APP_SWITCHED":
            app_name = data.get("app_name")
            if self.sm.current_state == JarvisState.FOCUS_MODE:
                switch_count = self.memory.get("switch_count", 0) + 1
                self.memory.update("switch_count", switch_count)
                if switch_count >= 3:
                    self.memory.update("switch_count", 0) 
                    resp = self.personality.get_response("COACH_SWITCH")
                    self.chat_history.add("JARVIS", resp)
                    return {"action": "SPEAK", "text": resp}
            self.memory.update("current_app", app_name)
            self.memory.update("window_title", data.get("window_title", ""))
            self.db.log_activity(app_name, data.get("window_title", ""), data.get("duration", 0))

        # 2. Command Handling
        elif event_type in ["USER_COMMAND", "WAKE_WORD_DETECTED"]:
            raw_cmd = data.get("command", "").strip().lower()
            if not raw_cmd:
                return {"action": "SPEAK", "text": "At your service, Sir. I'm listening."}

            cmd = self._clean_command(raw_cmd)
            self.chat_history.add("USER", cmd)

            # Context
            context = {
                "user_name": user_name,
                "vision": self.vision,
                "personality": self.personality,
                "db": self.db,
                "memory": self.memory,
                "history": self.chat_history
            }

            # 1. System Overrides (Highest Priority)
            if any(word in cmd for word in ["shutdown", "offline", "exit", "goodbye"]):
                system_skill = next((s for s in self.skills if isinstance(s, SystemSkill)), None)
                if system_skill: return system_skill.execute(cmd, context)

            # 2. Action Skills (If user says 'open', 'play', etc., prioritize doing it)
            for skill in self.skills:
                if isinstance(skill, (AppLauncherSkill, MediaSkill, SystemHealthSkill)):
                    if skill.matches(cmd):
                        return skill.execute(cmd, context)

            # 3. Intelligence Pass (Catch-all for reasoning/search/vision)
            brain = next((s for s in self.skills if isinstance(s, OmniBrainSkill)), None)
            if brain and brain.matches(cmd):
                self.sm.transition(JarvisState.CHATTING)
                result = brain.execute(cmd, context)
                if result:
                    if result.get("action") == "SPEAK":
                        self.chat_history.add("JARVIS", result["text"])
                    return result

            # 4. Fallback Skill Check
            for skill in self.skills:
                if skill.matches(cmd) and not isinstance(skill, (OmniBrainSkill, SystemSkill, AppLauncherSkill, MediaSkill)):
                    result = skill.execute(cmd, context)
                    if result and result.get("action") == "SPEAK":
                        self.chat_history.add("JARVIS", result["text"])
                    return result

            # 5. Global Fallback to Brain
            if brain:
                result = brain.execute(cmd, context)
                if result and result.get("action") == "SPEAK":
                    self.chat_history.add("JARVIS", result["text"])
                return result

        return None

        return None
