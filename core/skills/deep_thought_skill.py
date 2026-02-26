import time
import random
import sys
import json
import requests
from colorama import Fore, Style
from core.skills.base import BaseSkill

class DeepThoughtSkill(BaseSkill):
    def __init__(self):
        super().__init__("DeepThought", "Simulates complex neural processing for abstract questions.")
        self.keywords = ["think", "analyze", "explain", "why", "opinion", "strategy"]

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        history = context.get("history", None)
        
        # Fascinating Visuals
        self._simulate_neural_activity()
        
        # 1. Try Ollama (Local LLM)
        try:
            # JARVIS System Prompt to give Mistral the right personality
            system_prompt = (
                "You are JARVIS, a sophisticated, dry-witted, and loyal AI assistant inspired by Tony Stark's assistant. "
                "Keep responses concise, professional, and slightly superior but always polite. "
                "Address the user as 'Sir' or by their name if provided. Don't use emojis."
            )
            
            payload = {
                "model": "mistral",
                "prompt": f"{system_prompt}\nUser: {command}\nJARVIS:",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 100 # Keep it relatively brief for speech
                }
            }
            
            print(f"🧠 [NEURAL LINK] Querying local Mistral core via Ollama...")
            response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
            if response.status_code == 200:
                answer = response.json().get("response", "").strip()
                if answer:
                    # Clean up any AI hallucinations where it might repeat 'Sir' too much
                    return {"action": "SPEAK", "text": answer}
        
        except Exception as e:
            # Silence error and fallback to simulation
            pass

        # 2. Fallback to Simulated Wisdom
        responses = [
            f"Sir, based on a multi-threaded analysis of the current data streams, I believe we should prioritize efficiency.",
            f"Analyzing the variables... it appears we are at a critical junction in development. I'm standing by to compute the next best course of action.",
            f"My opinion, Sir? The data is conclusive. Focus is our strongest asset in this environment."
        ]
        return {"action": "SPEAK", "text": random.choice(responses)}

    def _simulate_neural_activity(self):
        print(f"\n{Fore.MAGENTA}[NEURAL LINK] Initializing synapse simulation...")
        symbols = ["-", "\\", "|", "/"]
        for i in range(15):
            sys.stdout.write(f"\r{Fore.MAGENTA}[NEURAL] {Fore.CYAN}Processing Synapse Layer {i+1}... {symbols[i % 4]} ")
            sys.stdout.flush()
            time.sleep(0.1)
        
        print(f"\n{Fore.GREEN}[ANALYSIS] Computation Complete. Weights normalized.{Style.RESET_ALL}\n")
