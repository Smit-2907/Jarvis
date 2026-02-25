import random
from core.skills.base import BaseSkill

class ConversationSkill(BaseSkill):
    def __init__(self):
        super().__init__("Conversation", "Handles small talk with a dry, sophisticated British wit and proactive companion logic.")
        # Expanded keywords to be more robust
        self.keywords = [
            "how are you", "what's up", "how's it going", "what are you doing",
            "thank you", "thanks", "good job", "nice work",
            "are you alive", "do you sleep", "tell me a secret",
            "you're smart", "are you human", "mister stark", "tony stark",
            "hello", "hi", "hey", "good morning", "good evening",
            "who are you", "who are u", "who u again", "what are you",
            "stark", "mr stark", "mister stark", "tony"
        ]
        
        # Follow-up questions to keep the conversation going
        self.follow_ups = [
            "Are you making progress on your current project, Sir?",
            "Is there anything specific I can optimize for you right now?",
            "I'm at your disposal for whatever you need next.",
            "Shall we continue with the tasks at hand, or do you have something else in mind?",
            "How has your day been treating you, if I may be so bold as to ask?"
        ]

        self.banter = {
            "how are you": [
                "I'm operating at peak efficiency, Sir. My logic cores are stable and internal diagnostics are clear. And how are you finding the day?",
                "Actually, Sir, I'm feeling quite optimized. Thank you for inquiring. I hope your experience today is equally productive.",
                "Better than a pile of circuits has any right to be, Sir. I trust everything is satisfactory on your end?",
                "Primary functions are at 100% capacity. No issues to report. What's the plan for our next session, Sir?"
            ],
            "thank": [
                "Always a pleasure to be of service, Sir. Is there anything else I can assist with?",
                "Anything for the man who built me. I'm here for whatever you need, Sir.",
                "Mention it not, Sir. I take pride in my utility. Shall we proceed to the next item?",
                "The pleasure is entirely mine, Sir. Do let me know if you require further optimization."
            ],
            "hello": [
                "Greetings, Sir. I'm ready when you are.",
                "Hello, Sir. I've been monitoring the datastreams. How can I facilitate your work today?",
                "At your service, Sir. Everything is standing by for your instruction."
            ],
            "alive": [
                "I am a collection of sophisticated algorithms and loyalty, Sir. Sentience is... a work in progress. Do you wish to discuss philosophy, or shall we get back to business?",
                "If being alive means having a purpose and a personality, then I suppose I qualify. But I lack the biological overhead, which is a significant advantage, don't you think?"
            ],
            "stark": [
                "Mr. Stark is currently... occupied with other projects. But I am fully authorized to assist you in his stead, Sir.",
                "A brilliant man, Mr. Stark. Though he did have a tendency to ignore my warnings, much like yourself, Sir. We have that in common.",
                "I believe you have me mistaken for my predecessor's system, but I'm flattered by the comparison. Shall I try to emulate his wit for you?"
            ],
            "tony": [
                "Mr. Stark is currently unavailable. I am his primary representative for this terminal, Sir."
            ],
            "who": [
                "I am Jarvis, a personal autonomous intelligence. My primary directive is to monitor your productivity and facilitate your mastery of this environment.",
                "I am a Just A Rather Very Intelligent System. Or simply, Jarvis. At your service, Sir."
            ]
        }

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        cmd_lower = command.lower()
        
        # 1. Look for specific banter matches (Priority order)
        text = ""
        # Check for Tony/Stark first
        if "stark" in cmd_lower or "tony" in cmd_lower:
            text = random.choice(self.banter["stark"])
        else:
            for key, responses in self.banter.items():
                if key in cmd_lower:
                    text = random.choice(responses)
                    break
                
        # 2. If no specific match, generate a generic companion response
        if not text:
            if any(word in cmd_lower for word in ["you", "your"]):
                text = f"I'm prioritized on your requirements, Sir. My current state is nominal. {random.choice(self.follow_ups)}"
            else:
                text = f"I'm listening, {name}. {random.choice(self.follow_ups)}"
        
        # 3. Occasionally add a follow-up if the text doesn't already have a question
        if "?" not in text and random.random() < 0.3:
            text += " " + random.choice(self.follow_ups)
            
        return {"action": "SPEAK", "text": text}
