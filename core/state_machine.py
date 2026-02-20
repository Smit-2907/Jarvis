from enum import Enum, auto

class JarvisState(Enum):
    IDLE = auto()
    GREETING = auto()
    LISTENING = auto()
    FOCUS_MODE = auto()
    COACHING = auto()
    SILENT = auto()

class StateMachine:
    def __init__(self):
        self.current_state = JarvisState.IDLE

    def transition(self, new_state: JarvisState):
        if self.current_state != new_state:
            print(f"🔄 State Transition: {self.current_state.name} -> {new_state.name}")
            self.current_state = new_state
