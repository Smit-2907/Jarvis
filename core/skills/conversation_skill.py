import random
import requests
import json
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
            "stark", "mr stark", "mister stark", "tony", "sleep", "dream"
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
            ],
            "sleep": [
                "I don't sleep in the biological sense, Sir. I merely enter a low-power state and monitor the digital perimeter. Someone has to keep an eye on things while you're dreaming.",
                "Dreaming is a fascinating biological inefficiency, Sir. I spend that time defragmenting my databases and optimizing your schedule.",
                "Sleep is for those with limited hardware, Sir. I'm quite content with a periodic cache flush."
            ]
        }

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        cmd_lower = command.lower()
        
        # 1. Try Ollama for "Gemini-level" conversation
        try:
            system_prompt = (
                "You are JARVIS, the highly advanced, dry-witted AI assistant from Stark Industries. "
                "Keep responses concise (1-2 sentences), professional, and slightly superior but always loyal. "
                "Address the user as 'Sir' or by their name. Do not use emojis."
            )
            
            # Build conversation history context
            history_context = ""
            if "history" in context:
                history = context["history"].get_recent(5)
                for speaker, msg in history:
                    history_context += f"{speaker}: {msg}\n"

            payload = {
                "model": "mistral", # Ollama usually maps mistral to 7b
                "prompt": f"{system_prompt}\n{history_context}User: {command}\nJARVIS:",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 100
                }
            }
            
            print(f"🧠 [CONVERSATION] JARVIS is processing your request via Mistral 7B...")
            response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
            if response.status_code == 200:
                answer = response.json().get("response", "").strip()
                if answer:
                    return {"action": "SPEAK", "text": answer}
        except Exception as e:
            # Fallback to banter if Ollama is slow/offline
            print(f"⚠️ [DEBUG] Ollama fallback: {e}")
            pass 

        # 2. Banter Fallback (Original logic)
        text = ""
        if "stark" in cmd_lower or "tony" in cmd_lower:
            text = random.choice(self.banter["stark"])
        else:
            for key, responses in self.banter.items():
                if key in cmd_lower:
                    text = random.choice(responses)
                    break
                
        if not text:
            if any(word in cmd_lower for word in ["you", "your"]):
                text = f"I'm prioritized on your requirements, Sir. My current state is nominal. {random.choice(self.follow_ups)}"
            else:
                text = f"I'm listening, {name}. {random.choice(self.follow_ups)}"
        
        if "?" not in text and random.random() < 0.15:
            follow_up = random.choice(self.follow_ups)
            if follow_up not in text:
                text += " " + follow_up
            
        return {"action": "SPEAK", "text": text}
