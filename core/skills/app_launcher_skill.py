import os
import subprocess
from core.skills.base import BaseSkill

class AppLauncherSkill(BaseSkill):
    def __init__(self):
        super().__init__("AppLauncher", "Launches applications, web pages, and system folders.")
        self.keywords = ["open", "launch", "start", "run", "browse"]
        
        # Extended App Map
        self.app_map = {
            "browser": "start chrome",
            "chrome": "start chrome",
            "edge": "start msedge",
            "spotify": "start spotify:",
            "code": "code",
            "visual studio code": "code",
            "notepad": "notepad",
            "calculator": "calc",
            "terminal": "wt",
            "powershell": "powershell",
            "discord": "start discord:",
            "whatsapp": "start whatsapp:",
            "vlc": "vlc",
            "settings": "start ms-settings:",
            "command prompt": "cmd"
        }
        
        # Common Folder Map
        self.folder_map = {
            "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
            "documents": os.path.join(os.path.expanduser("~"), "Documents"),
            "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
            "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
            "projects": os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "jarvis") # Local context
        }

    def execute(self, command: str, context: dict) -> dict:
        name = context.get("user_name", "Sir")
        
        # 1. URL Detection
        if ".com" in command or ".org" in command or "website" in command:
            words = command.split()
            for word in words:
                if "." in word and len(word) > 4:
                    url = word if word.startswith("http") else "https://" + word
                    os.system(f"start {url}")
                    return {"action": "SPEAK", "text": f"Opening the requested webpage, {name}."}

        # 2. Folder Detection
        for folder_key, path in self.folder_map.items():
            if folder_key in command:
                if os.path.exists(path):
                    os.startfile(path)
                    return {"action": "SPEAK", "text": f"Opening your {folder_key} folder, Sir."}

        # 3. Application Detection
        for app_key, run_cmd in self.app_map.items():
            if app_key in command:
                try:
                    subprocess.Popen(run_cmd, shell=True)
                    return {"action": "SPEAK", "text": f"Initializing {app_key}, {name}."}
                except Exception:
                    return {"action": "SPEAK", "text": f"I encountered an error trying to initialize {app_key}, Sir."}

        # 4. Fallback search (if "open" is used but no match found)
        if "open" in command or "search for" in command:
            search_query = command.replace("open", "").replace("search for", "").strip()
            if len(search_query) > 2:
                # Try to search on Google as a fallback for "open [unknown thing]"
                import urllib.parse
                url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
                os.system(f"start {url}")
                return {"action": "SPEAK", "text": f"I'm not familiar with that specific application, Sir. Opening a search for '{search_query}' instead."}

        return {}
