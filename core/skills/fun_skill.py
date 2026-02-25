import random
from core.skills.base import BaseSkill

class FunSkill(BaseSkill):
    def __init__(self):
        super().__init__("Fun", "Provides humor and small talk.")
        self.keywords = ["joke", "funny", "laugh", "humour"]
        self.jokes = [
            "Why did the developer go broke? Because he used up all his cache.",
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "How many programmers does it take to change a light bulb? None, it's a hardware problem.",
            "There are only 10 kinds of people: those who understand binary, and those who don't.",
            "Why do Java programmers have to wear glasses? Because they don't C#."
        ]

    def matches(self, command: str) -> bool:
        return any(word in command for word in self.keywords)

    def execute(self, command: str, context: dict) -> dict:
        return {"action": "SPEAK", "text": "A little levity? Very well. " + random.choice(self.jokes)}
