import re
from abc import ABC, abstractmethod

class BaseSkill(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def matches(self, command: str) -> bool:
        """
        Default match logic using word boundaries for keywords.
        """
        if not hasattr(self, 'keywords'):
            return False
            
        for kw in self.keywords:
            # Use regex for whole-word matching to avoid partial matches
            pattern = rf"\b{re.escape(kw)}\b"
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

    @abstractmethod
    def execute(self, command: str, context: dict) -> dict:
        """Execute the skill logic and return an action dict."""
        pass
