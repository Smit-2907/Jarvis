import os
import time
import yaml
import threading
import sys
from colorama import Fore, Style, init

from core.event_bus import bus
from core.state_machine import StateMachine, JarvisState
from core.decision_engine import DecisionEngine
from perception.perception_layer import VisionPresence, ActivityTracker
from perception.audio_listener import AudioListener
from memory.database import DatabaseManager, ShortTermMemory
from personality.response_generator import ResponseGenerator
from action.action_layer import TTSEngine, AutomationEngine

init(autoreset=True)

class AgentLoop:
    def __init__(self, config_path: str):
        # 1. Resolve Project Root
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        # 2. Re-resolve config path if it was relative
        if not os.path.isabs(config_path):
            config_abs = os.path.abspath(os.path.join(self.root, config_path))
            if os.path.exists(config_abs): config_path = config_abs

        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                
            print(f"🧠 {Fore.YELLOW}Initializing Intelligence Core...")
            # Make paths absolute relative to project root
            db_abs_path = os.path.abspath(os.path.join(self.root, self.config['memory']['db_path']))
            self.db = DatabaseManager(db_abs_path)
            self.stm = ShortTermMemory()
            self.personality = ResponseGenerator(self.config['system']['personality'])
            self.sm = StateMachine()
            self.automation = AutomationEngine()
            
            if self.config['perception']['vision'].get('enabled', True):
                self.vision = VisionPresence(
                    self.config['perception']['vision']['interval'],
                    show_hud=self.config['perception']['vision'].get('debug_view', False),
                    root_path=self.root
                )
            else:
                self.vision = None
                print(f"👁️ {Fore.RED}Vision Sensors are DISABLED via configuration.")
            
            self.decision_engine = DecisionEngine(self.sm, self.stm, self.db, self.personality, vision=self.vision)
            
            print(f"🔊 {Fore.YELLOW}Connecting Action Subsystems...")
            self.tts = TTSEngine(self.config['action']['voice_rate'], self.config['action']['volume'])
            self.activity = ActivityTracker(self.config['perception']['activity']['interval'])
            
            print(f"👂 {Fore.YELLOW}Calibrating Audio Sensors (Asynchronous)...")
            audio_model_abs = os.path.abspath(os.path.join(self.root, self.config['perception']['audio']['model_path']))
            self.audio = AudioListener(audio_model_abs, 
                                       self.config['perception']['audio']['wake_word'],
                                       self.config['perception']['audio'].get('intensity_threshold', 150))
            
            # We start the audio thread immediately, it handles its own slow model loading
            self.audio.start()
            
            self._running = False
            self._setup_subscriptions()
            self._last_interaction = time.time()
            print(f"✅ {Fore.GREEN}Systems Ready.")
            
        except Exception as e:
            print(f"❌ {Fore.RED}CRITICAL: JARVIS failed to initialize subsystems: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def _setup_subscriptions(self):
        events = ["USER_PRESENT", "USER_LEFT", "APP_SWITCHED", "WAKE_WORD_DETECTED", "USER_COMMAND"]
        for e in events:
            # We wrap the handle in a thread to keep the event source (Audio/Vision) responsive
            bus.subscribe(e, lambda data, et=e: threading.Thread(target=self._handle_event, args=(et, data), daemon=True).start())

    def _handle_event(self, event_type: str, data: dict):
        self._last_interaction = time.time()
        
        # INTERRUPTION LOGIC: If user says "stop" or "listen jarvis", kill active TTS
        raw_cmd = data.get("command", "").lower()
        if "stop" in raw_cmd or "listen jarvis" in raw_cmd or "shut up" in raw_cmd:
            self.tts.stop_speaking()
            # If it was just a stop command, we can return early or proceed to evaluate
            if raw_cmd.strip() in ["stop", "listen jarvis", "shut up"]:
                return

        result = self.decision_engine.evaluate(event_type, data)
        if result:
            if result.get("terminate"):
                self.tts.speak("Systems powering down. It's been a pleasure, Sir.")
                time.sleep(2)
                self.stop()
                sys.exit(0)
            
            if result.get("action") == "SPEAK":
                self.tts.speak(result["text"])
            elif result.get("action") == "EXECUTE":
                self.automation.execute_command(result["text"])
            elif result.get("action") == "LOG":
                self.db.log_event(event_type, result["text"])

    def _proactive_check(self):
        while self._running:
            now = time.time()
            if self.sm.current_state == JarvisState.IDLE and (now - self._last_interaction > 600):
                if self.vision and self.vision.is_present:
                    self._last_interaction = now
                    resp = "Pardon me, Sir. I noticed it's been a while since our last interaction. Shall I put the primary scanners on idle, or are we still making progress?"
                    self.tts.speak(resp)
            time.sleep(60)

    def _cli_input_thread(self):
        while self._running:
            try:
                print(f"{Fore.WHITE}USER > ", end="", flush=True)
                cmd = sys.stdin.readline().strip().lower()
                if cmd:
                    bus.publish("USER_COMMAND", {"command": cmd})
            except Exception:
                continue

    def run(self):
        self._running = True
        
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}       STARK INDUSTRIES - J.A.R.V.I.S. OS v4.0")
        print(f"{Fore.CYAN}       STATUS: {Fore.GREEN}COMPANION")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        print(f"🎤 All core threads dispatched. Jarvis is monitoring...")
        
        threading.Thread(target=self._cli_input_thread, daemon=True).start()
        threading.Thread(target=self._proactive_check, daemon=True).start()
        
        print(f"{Fore.BLUE}💬 Hello, Sir. Jarvis at your service. All systems standing by.")
        
        try:
            while self._running:
                if self.vision:
                    self.vision.poll()
                self.activity.poll()
                time.sleep(1.0) 
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self._running = False
        self.audio.stop()
        if self.vision:
            self.vision.stop()
        print(f"\n{Fore.RED}🛑 Jarvis Systems Offline. Powering down.")
