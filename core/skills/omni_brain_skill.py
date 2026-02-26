import requests
import json
import random
import time
from duckduckgo_search import DDGS
from core.skills.base import BaseSkill

class OmniBrainSkill(BaseSkill):
    def __init__(self):
        super().__init__("OmniBrain", "The central intelligence core. Combines LLM reasoning, internet search, and visual context.")
        # Catch-all keywords for deep intelligence
        self.keywords = [
            "why", "how", "what", "who", "tell me", "explain", "analyze", "search", 
            "find", "is it", "opinion", "strategy", "help", "think", "suggest",
            "weather", "news", "price", "stock", "identify", "see"
        ]
        self.last_search_result = ""

    def execute(self, command: str, context: dict) -> dict:
        try:
            return self._brain_process(command, context)
        except Exception as e:
            print(f"❌ [CRITICAL] Brain Core Failure: {e}")
            import traceback
            traceback.print_exc()
            return {"action": "SPEAK", "text": "Sir, I'm experiencing a minor sync error in my logic cores. One moment."}

    def _brain_process(self, command: str, context: dict) -> dict:
        vision = context.get("vision")
        history = context.get("history")
        user_name = context.get("user_name", "Sir")
        st_memory = context.get("memory")
        
        # 1. Vision Context
        vision_report = "Eyes: Scanning..."
        if vision:
            objs = vision.get_detected_objects()
            emotion = vision.get_emotion()
            hand_obj = vision.get_object_in_hand()
            
            vision_details = []
            if objs: vision_details.append(f"Detected Objects: {', '.join(objs)}")
            if hand_obj: vision_details.append(f"Active Manipulation: User is holding a {hand_obj}")
            if emotion and emotion != "None": vision_details.append(f"User Facial Emotion: {emotion}")
            
            if vision_details:
                vision_report = "Optic Status: " + " | ".join(vision_details)

        # 1b. Activity/System Context
        activity_report = "System: Status nominal."
        if st_memory:
            current_app = st_memory.get("current_app")
            window_title = st_memory.get("window_title")
            if current_app:
                activity_report = f"User Activity: Currently using {current_app} ({window_title})."

        # 2. History context
        chat_log = ""
        if history:
            try:
                recent = history.get_recent(5)
                for role, text in recent:
                    chat_log += f"{role}: {text}\n"
            except: pass

        # 3. Decision: Do we need internet?
        trigger_words = ["news", "weather", "latest", "who is", "what happened", "stock", "price", "current", "update", "today", "tomorrow"]
        needs_search = any(word in command.lower() for word in trigger_words)
        search_context = ""
        
        if needs_search:
            try:
                # Better query cleaning: Remove 'Jarvis' and common trigger verbs
                search_query = command.lower()
                for phrase in ["jarvis", "tell me about", "what is", "do a search for", "google", "search for", "find out"]:
                    search_query = search_query.replace(phrase, "").strip()
                
                # If news is mentioned, make the query more relevant to headlines
                if "news" in search_query:
                    search_query = f"latest news {search_query.replace('news', '').strip()}"
                
                print(f"🌍 [INTERNET] Scanning global datastreams for: {search_query}...")
                with DDGS() as ddgs:
                    # New syntax for DDGS text search in v6+
                    results = [r for r in ddgs.text(search_query, max_results=3)]
                    if results:
                        search_context = "\nRecent Real-world Data:\n" + "\n".join([f"- {r['body']}" for r in results])
                        print(f"✅ [INTERNET] Satellite uplink successful. Data synced.")
                    else:
                        print(f"⚠️ [INTERNET] No significant data found for '{search_query}'.")
            except Exception as e:
                print(f"❌ [INTERNET ERROR] Uplink failure: {e}")

        # 4. Neural Processing
        try:
            print(f"🧠 [NEURAL] Synthesizing response via Mistral 7B core...")
            
            system_prompt = (
                f"You are JARVIS, the highly advanced AI from Stark Industries. "
                f"You are witty, sophisticated, British-accented, and proactive. "
                "You have access to real-time vision and internet data. "
                "\n[CURRENT ENVIRONMENT]:\n"
                f"{vision_report}\n"
                f"{activity_report}\n"
                f"{search_context if search_context else '[Internet Data: Not required for this request]'}\n"
                "\nINSTRUCTIONS:\n"
                "1. Address the user as 'Sir'.\n"
                "2. Be concise (max 2 sentences).\n"
                "3. Use the environmental data naturally (e.g., 'I see you are holding a pen, Sir').\n"
                "4. If searching the web, summarize the answer don't just say you checked.\n"
                "5. No emojis."
            )

            payload = {
                "model": "mistral",
                "prompt": f"{system_prompt}\n\n[CONVERSATION HISTORY]:\n{chat_log}\n\nSir: {command}\nJARVIS:",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 100
                }
            }

            response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=45)
            
            if response.status_code == 200:
                answer = response.json().get("response", "").strip()
                if answer:
                    return {"action": "SPEAK", "text": answer}
                    
        except Exception as e:
            print(f"❌ [NEURAL ERROR] Logic core timeout: {e}")

        # Ultra-Stable Fallback
        return {"action": "SPEAK", "text": "My apologies, Sir. My connection to the primary reasoning core is intermittent. I am however monitoring your environment and stand ready."}
