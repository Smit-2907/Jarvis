import re
import random
from core.skills.base import BaseSkill

class MathSkill(BaseSkill):
    def __init__(self):
        super().__init__("Math", "Performs mathematical calculations.")
        self.keywords = ["plus", "minus", "times", "divided", "calculate", "what is", "sum"]

    def matches(self, command: str) -> bool:
        return any(word in command for word in self.keywords) or re.search(r'[0-9]', command)

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        try:
            # Basic cleanup for eval (still risky but matching original behavior for now)
            math_input = command.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")
            expr = re.sub(r'[^0-9+\-*/().]', '', math_input)
            if expr:
                # Use a safer eval approach or just simple math parser
                # For now keeping it similar to original but with a bit more safety in mind
                res = eval(expr, {"__builtins__": None}, {})
                math_phrases = [
                    f"According to my calculations, that would be {res}.",
                    f"The result is {res}, Sir.",
                    f"That comes out to {res}.",
                    f"I've computed the value for you: {res}."
                ]
                return {"action": "SPEAK", "text": random.choice(math_phrases)}
        except Exception as e:
            print(f"Math Error: {e}")
            return {"action": "SPEAK", "text": "I'm sorry, Sir, that calculation seems to be causing an overflow in my logic processor."}
        
        return {}
