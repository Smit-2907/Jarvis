from core.skills.base import BaseSkill
from core.state_machine import JarvisState

class ProductivitySkill(BaseSkill):
    def __init__(self, state_machine):
        super().__init__("Productivity", "Manages focus sessions and activity tracking.")
        self.sm = state_machine
        self.keywords = ["focus", "lock in", "deep work", "work", "stop mode", "break", "idle", "status report", "how is my day", "productivity"]

    def matches(self, command: str) -> bool:
        return any(word in command for word in self.keywords)

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        db = context.get("db")
        
        if any(word in command for word in ["status report", "how is my day", "productivity"]):
            if db:
                summary = db.get_activity_summary()
                if not summary:
                    return {"action": "SPEAK", "text": f"I don't have enough data yet to compile a full report, {name}. We should begin monitoring your focus sessions."}
                
                top_app = summary[0]['app_name']
                total_seconds = sum(item['total_duration'] for item in summary)
                report = f"Report for today, {name}. Your primary activity has been {top_app}. "
                report += f"I have logged a total of {int(total_seconds // 60)} minutes of active usage across all applications."
                return {"action": "SPEAK", "text": report}

        if any(word in command for word in ["focus", "lock in", "deep work", "work"]):
            self.sm.transition(JarvisState.FOCUS_MODE)
            return {"action": "SPEAK", "text": f"Focus mode initiated, {name}. I will now log any potential distractions."}
            
        if any(word in command for word in ["stop", "break", "idle"]):
            self.sm.transition(JarvisState.IDLE)
            return {"action": "SPEAK", "text": f"I have deactivated focus mode. You are now in idle state, {name}."}

        return {}
