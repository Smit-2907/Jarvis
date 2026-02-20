import time
import yaml
import threading
from core.event_bus import bus
from core.state_machine import StateMachine
from core.decision_engine import DecisionEngine
from perception.perception_layer import VisionPresence, ActivityTracker
from perception.audio_listener import AudioListener
from memory.database import DatabaseManager, ShortTermMemory
from personality.response_generator import ResponseGenerator
from action.action_layer import TTSEngine, AutomationEngine

class AgentLoop:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        # Layers
        self.db = DatabaseManager(self.config['memory']['db_path'])
        self.stm = ShortTermMemory()
        self.personality = ResponseGenerator(self.config['system']['personality'])
        self.sm = StateMachine()
        self.automation = AutomationEngine()
        
        self.vision = VisionPresence(self.config['perception']['vision']['interval'])
        self.decision_engine = DecisionEngine(self.sm, self.stm, self.db, self.personality, vision=self.vision)
        
        self.tts = TTSEngine(self.config['action']['voice_rate'], self.config['action']['volume'])
        self.activity = ActivityTracker(self.config['perception']['activity']['interval'])
        self.audio = AudioListener(self.config['perception']['audio']['model_path'], 
                                   self.config['perception']['audio']['wake_word'])
        
        self._running = False
        
        # Connect Bus to Decision Engine
        self._setup_subscriptions()

    def _setup_subscriptions(self):
        # All events go to the decision engine
        events = ["USER_PRESENT", "USER_LEFT", "APP_SWITCHED", "WAKE_WORD_DETECTED", "USER_COMMAND"]
        for e in events:
            bus.subscribe(e, lambda data, et=e: self._handle_event(et, data))

    def _handle_event(self, event_type: str, data: dict):
        result = self.decision_engine.evaluate(event_type, data)
        if result:
            if result.get("terminate"):
                self.tts.speak("Goodbye! Shutting down systems.")
                time.sleep(2)
                self.stop()
                sys.exit(0)
            
            if result.get("action") == "SPEAK":
                self.tts.speak(result["text"])
            elif result.get("action") == "EXECUTE":
                self.automation.execute_command(result["text"])
            elif result.get("action") == "LOG":
                self.db.log_event(event_type, result["text"])

    def _cli_input_thread(self):
        """Allows direct text interaction with Jarvis via terminal."""
        while self._running:
            try:
                # Use input() in a way that doesn't block the whole app too much
                cmd = input("💬 Say something to Jarvis: ").strip().lower()
                if cmd:
                    bus.publish("USER_COMMAND", {"command": cmd})
            except EOFError:
                break
            except Exception:
                continue

    def run(self):
        self._running = True
        print("🤖 Jarvis Agent Loop Starting...")
        print("💡 Hint: Type 'focus' or 'hello' below to interact.")
        
        # Start Audio & CLI threads
        self.audio.start()
        threading.Thread(target=self._cli_input_thread, daemon=True).start()
        
        try:
            while self._running:
                # Perception Polling
                self.vision.poll()
                self.activity.poll()
                
                time.sleep(1.0) # Main loop cadence
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self._running = False
        self.audio.stop()
        self.vision.stop()
        print("🛑 Jarvis Offline.")
