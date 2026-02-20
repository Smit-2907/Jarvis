from threading import Lock
from collections import defaultdict
from typing import Callable, Any

class EventBus:
    """A simple thread-safe synchronous event bus."""
    def __init__(self):
        self._subscribers = defaultdict(list)
        self._lock = Lock()

    def subscribe(self, event_type: str, callback: Callable[[Any], None]):
        with self._lock:
            self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, data: Any = None):
        with self._lock:
            subscribers = self._subscribers[event_type][:]
        
        for callback in subscribers:
            try:
                callback(data)
            except Exception as e:
                print(f"Error in subscriber for {event_type}: {e}")

# Global instance for ease of use
bus = EventBus()
