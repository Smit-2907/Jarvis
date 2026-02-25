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
            AutomationSkill(),
            WebSearchSkill(),
            DeepThoughtSkill(),
            ConversationSkill(),
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
            "years": "sir", "for years": "sir", "active and ready for years": "active and ready for sir"
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
            self.db.log_activity(app_name, data.get("title", ""), 5.0)

        # 2. Command Handling
        elif event_type in ["USER_COMMAND", "WAKE_WORD_DETECTED"]:
            raw_cmd = data.get("command", "").strip().lower()
            if not raw_cmd:
                resp = self.personality.get_response("SMALL_TALK")
                self.chat_history.add("JARVIS", resp)
                self.sm.transition(JarvisState.CHATTING)
                return {"action": "SPEAK", "text": resp}

            cmd = self._clean_command(raw_cmd)
            self.chat_history.add("USER", cmd)
            
            # Contextual Bias: If we're chatting, favor ConversationSkill
            if self.sm.current_state == JarvisState.CHATTING:
                # Move ConversationSkill to front of list for this check
                chat_skill = next((s for s in self.skills if isinstance(s, ConversationSkill)), None)
                if chat_skill and chat_skill.matches(cmd):
                    result = chat_skill.execute(cmd, {"user_name": user_name, "history": self.chat_history})
                    if result:
                        self.chat_history.add("JARVIS", result["text"])
                        return result

            # Check Skills
            context = {
                "user_name": user_name,
                "vision": self.vision,
                "personality": self.personality,
                "db": self.db,
                "memory": self.memory,
                "history": self.chat_history
            }

            for skill in self.skills:
                if skill.matches(cmd):
                    # For companion feel, transition to CHATTING if it's a social/info skill
                    if isinstance(skill, (ConversationSkill, DeepThoughtSkill, FunSkill)):
                        self.sm.transition(JarvisState.CHATTING)
                        
                    result = skill.execute(cmd, context)
                    if result and result.get("action") == "SPEAK":
                        self.chat_history.add("JARVIS", result["text"])
                    return result

            # 3. Fallback to Conversation (Instead of erroring)
            self.sm.transition(JarvisState.CHATTING)
            chat_skill = next((s for s in self.skills if isinstance(s, ConversationSkill)), None)
            if chat_skill:
                result = chat_skill.execute(cmd, context)
                self.chat_history.add("JARVIS", result["text"])
                return result

        return None
