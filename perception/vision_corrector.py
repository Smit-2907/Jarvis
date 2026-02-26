import json
import os

class VisionCorrector:
    def __init__(self, mapping_path: str):
        self.mapping_path = mapping_path
        self.mappings = self._load()

    def _load(self):
        if os.path.exists(self.mapping_path):
            try:
                with open(self.mapping_path, 'r') as f:
                    return json.load(f)
            except: pass
        return {
            "knife": "pen", # Default bias based on user feedback
            "scissors": "pen",
            "toothbrush": "pen"
        }

    def save(self, original: str, corrected: str):
        self.mappings[original.lower()] = corrected.lower()
        os.makedirs(os.path.dirname(self.mapping_path), exist_ok=True)
        with open(self.mapping_path, 'w') as f:
            json.dump(self.mappings, f)

    def correct(self, label: str) -> str:
        return self.mappings.get(label.lower(), label)
