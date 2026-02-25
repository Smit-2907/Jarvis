import re
import os
import json
from core.skills.base import BaseSkill

class LearningSkill(BaseSkill):
    def __init__(self, rules_path: str, user_memory_path: str):
        super().__init__("Learning", "Allows the user to teach Jarvis new rules and memories.")
        self.rules_path = rules_path
        self.user_memory_path = user_memory_path
        self.trigger_words = ["learn", "remember", "means", "my name is"]

    def matches(self, command: str) -> bool:
        return any(word in command for word in self.trigger_words)

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        
        # 1. Identity
        if "my name is" in command:
            new_name = command.split("my name is")[-1].strip().replace(".", "").capitalize()
            if self._set_user_name(new_name):
                return {"action": "SPEAK", "text": f"Very well. I shall address you as {new_name} from now on."}
            else:
                return {"action": "SPEAK", "text": f"I'm sorry, that name sounds a bit too complex for my current database."}

        # 2. Dynamic Rule Learning
        if "means" in command:
            match = re.search(r"(?:learn that|remember that)? (.*) means (.*)", command)
            if match:
                t, r = match.groups()
                self._save_rule(t.strip(), r.strip())
                return {"action": "SPEAK", "text": f"Acknowledged. I have logged that '{t.strip()}' corresponds to '{r.strip()}'."}

        return {}

    def _save_rule(self, trigger, response):
        rules = self._load_rules()
        rules[trigger.lower()] = response
        os.makedirs(os.path.dirname(self.rules_path), exist_ok=True)
        with open(self.rules_path, 'w') as f:
            json.dump(rules, f)

    def _load_rules(self):
        if os.path.exists(self.rules_path):
            try:
                with open(self.rules_path, 'r') as f:
                    return json.load(f)
            except: pass
        return {}

    def _set_user_name(self, name: str):
        if len(name.split()) > 2:
            return False
        os.makedirs(os.path.dirname(self.user_memory_path), exist_ok=True)
        with open(self.user_memory_path, 'w') as f:
            json.dump({"name": name}, f)
        return True
