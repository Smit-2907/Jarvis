import collections

class ConversationHistory:
    def __init__(self, capacity: int = 5):
        self.history = collections.deque(maxlen=capacity)

    def add(self, role: str, message: str):
        self.history.append({"role": role, "message": message})

    def get_last_user_message(self):
        for entry in reversed(self.history):
            if entry["role"] == "USER":
                return entry["message"]
        return None

    def get_context_string(self):
        return "\n".join([f"{e['role']}: {e['message']}" for e in self.history])

    def clear(self):
        self.history.clear()
