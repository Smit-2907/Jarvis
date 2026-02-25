import os
import urllib.parse
import re
import random
from core.skills.base import BaseSkill

class WebSearchSkill(BaseSkill):
    def __init__(self):
        super().__init__("WebSearch", "Searches the internet for information.")
        self.keywords = ["search", "google", "find out", "lookup", "research", "tell me about", "what is"]
        self.ignore = ["who are you", "what is the time", "what is 2", "status", "who are u"]

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        
        # 1. Strip WAKE word and Jarvis name
        query = command.lower()
        query = query.replace("jarvis", "").strip()
        
        # 2. Extract subject by stripping known search verbs/phrases
        # We use a broader list of search phrases to clean the subject
        verbs = [
            "search for", "search", "google", "find out", "lookup", 
            "research", "tell me about", "what is", "do a search for",
            "perform a search on", "who is", "who are", "information on"
        ]
        
        # Sort by length descending to catch longer phrases first
        for verb in sorted(verbs, key=len, reverse=True):
            if query.startswith(verb):
                query = query[len(verb):].strip()
                break
            elif verb in query:
                # If verb is in the middle, take everything AFTER it
                query = query.split(verb)[-1].strip()
                break
        
        # Clean up common filler words at the start of the remaining subject
        query = re.sub(r'^(the|a|an|some|details on|about)\s+', '', query)
        
        if not query or len(query) < 2:
            return {"action": "SPEAK", "text": f"Sir, I'm ready to search, but I need a clearer subject. What would you like me to look up?"}

        # Format URL
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        
        # Proactively open browser
        os.system(f"start {url}")
        
        responses = [
            f"I've initiated a search for '{query}', Sir.",
            f"Actually, I've located some data on '{query}'. Browsing the results now.",
            f"Searching the global networks for '{query}' as requested.",
            f"Researching '{query}' now. Results should be visible on your primary display, Sir."
        ]
        return {"action": "SPEAK", "text": random.choice(responses)}
