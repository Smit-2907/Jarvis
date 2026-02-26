import cv2
import time
import threading
import os
import numpy as np
import collections
from core.event_bus import bus
from perception.vision_corrector import VisionCorrector

try:
    import psutil
    import win32gui
    import win32process
    ACTIVITY_AVAILABLE = True
except ImportError:
    ACTIVITY_AVAILABLE = False


try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

# Heavy AI imports moved to background init to prevent startup hang
ADVANCED_MODELS_AVAILABLE = True

class VisionPresence:
    def __init__(self, interval: float = 1.0, show_hud: bool = False):
        self.interval = interval
        self.show_hud = show_hud
        self.corrector = VisionCorrector(os.path.join("config", "vision_mappings.json"))
        self.is_present = False
        self.last_state_change = 0
        self.face_count = 0
        self.finger_count = 0
        self.current_emotion = "Neutral"
        self.detected_objects = []
        self.detection_history = collections.deque(maxlen=6) # Faster response: 6 frames
        self.object_in_hand = None
        
        # Initialize Tasks
        self.hand_landmarker = None
        self.yolo_model = None
        self.deepface_locked = False # To prevent overlapping analysis
        
        # Camera starts as None, will be opened in background
        self.cap = None
        
        # Initialize EVERYTHING in background to stop main thread hang
        threading.Thread(target=self._initialize_all_models, daemon=True).start()

    def _initialize_all_models(self):
        """Wrapper for background thread loading."""
        # 1. Open Camera first (Critical for HUD)
        print(f"👁️ {time.strftime('%H:%M:%S')} [VISION] Initializing Tactical Camera...")
        try:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            print(f"✅ {time.strftime('%H:%M:%S')} [VISION] Camera uplink established.")
        except Exception as e:
            print(f"⚠️ [VISION] Camera Fail: {e}")

        if MEDIAPIPE_AVAILABLE:
            self._init_tasks()
        if ADVANCED_MODELS_AVAILABLE:
            self._init_advanced_models()

    def _init_tasks(self):
        try:
            # 1. Hands (Keeping MediaPipe for best hand perf)
            hand_model = os.path.join("models", "hand_landmarker.task")
            if os.path.exists(hand_model):
                base_options = python.BaseOptions(model_asset_path=hand_model)
                options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
                self.hand_landmarker = vision.HandLandmarker.create_from_options(options)
                print("👁️ Tactical Hand Tracking active (MediaPipe).")
        except Exception as e:
            print(f"⚠️ Hand Task Init Error: {e}")

    def _init_advanced_models(self):
        try:
            # Move heavy imports here so main thread doesn't hang
            print(f"👁️ {time.strftime('%H:%M:%S')} [VISION] Loading high-fidelity Neural Modules...")
            from ultralytics import YOLO
            from deepface import DeepFace
            
            # YOLOv8n for Object Detection
            print(f"👁️ {time.strftime('%H:%M:%S')} [VISION] Initializing YOLOv8 Neural Core...")
            print(f"💡 [INFO] This might take a moment to synchronize weights (~6MB).")
            self.yolo_model = YOLO("yolov8n.pt") 
            print(f"✅ {time.strftime('%H:%M:%S')} [VISION] YOLOv8 Object Recognition active.")
            
            # DeepFace pre-warm 
            print(f"👁️ {time.strftime('%H:%M:%S')} [VISION] Loading DeepFace Biometric Suite...")
            print(f"✅ {time.strftime('%H:%M:%S')} [VISION] Biometric Intelligence active.")
            self.deepface_module = DeepFace # Store for run_deepface
        except Exception as e:
            print(f"⚠️ {time.strftime('%H:%M:%S')} [VISION] Advanced Model Init Error: {e}")
            # Ensure it doesn't try to run if it failed
            self.yolo_model = None

    def _analyze_emotion(self, blendshapes):
        """Map blendshapes to emotions."""
        # MediaPipe blendshapes provide categories like 'eyeBlinkLeft', 'jawOpen', etc.
        shapes = {s.category_name: s.score for s in blendshapes[0]}
        
        if shapes.get('jawOpen', 0) > 0.4: return "Surprised"
        if (shapes.get('mouthSmileLeft', 0) + shapes.get('mouthSmileRight', 0)) > 0.6: return "Happy"
        if (shapes.get('browDownLeft', 0) + shapes.get('browDownRight', 0)) > 0.4: return "Serious/Focused"
        if (shapes.get('mouthPucker', 0)) > 0.3: return "Thinking"
        return "Neutral"


    def learn_object(self, original: str, corrected: str):
        self.corrector.save(original, corrected)
        print(f"👁️ JARVIS: Re-trained optic recognition. '{original}' is now seen as '{corrected}'.")

    def _analyze_presence(self):
        # 4. Presence
        now = time.time()
        now_present = self.face_count > 0
        if now_present != self.is_present:
            if now - self.last_state_change > 3:
                self.is_present = now_present
                self.last_state_change = now
                bus.publish("USER_PRESENT" if now_present else "USER_LEFT", {"emotion": self.current_emotion})

    def poll(self):
        if not self.cap or not self.cap.isOpened(): return
        ret, frame = self.cap.read()
        if not ret: return
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # 1. Hands & Fingers
        self.finger_count = 0
        hand_landmarks = []
        if self.hand_landmarker:
            try:
                res = self.hand_landmarker.detect(mp_image)
                if res.hand_landmarks:
                    hand_landmarks = res.hand_landmarks
                    for hand in res.hand_landmarks:
                        # Tips: 8, 12, 16, 20. Thumb: 4.
                        for tip in [8, 12, 16, 20]:
                            if hand[tip].y < hand[tip-2].y: self.finger_count += 1
                        # Thumb
                        if hand[4].x < hand[3].x: self.finger_count += 1
            except: pass

        # 2. Face, Identity & Emotion (DeepFace)
        self.face_count = 0
        if ADVANCED_MODELS_AVAILABLE and self.yolo_model and not self.deepface_locked:
            # We run DeepFace every 5 frames to save CPU
            if int(time.time() * 10) % 5 == 0:
                threading.Thread(target=self._run_deepface, args=(frame.copy(),), daemon=True).start()

        # 3. Objects & In-Hand (YOLOv8)
        self.object_in_hand = None
        self.current_detections = [] 
        new_objs = []
        
        if self.yolo_model:
            results = self.yolo_model(frame, verbose=False)[0]
            for box in results.boxes:
                label = results.names[int(box.cls[0])]
                conf = float(box.conf[0])
                
                if conf > 0.4:
                    label = self.corrector.correct(label)
                    new_objs.append(label)
                    
                    # Store for HUD
                    xyxy = box.xyxy[0].tolist()
                    self.current_detections.append({
                        "label": label,
                        "conf": conf,
                        "bbox": xyxy
                    })
                    
                    # Hand proximity check
                    if hand_landmarks:
                        x1, y1, x2, y2 = xyxy
                        for hand in hand_landmarks:
                            hx, hy = hand[9].x * 640, hand[9].y * 480
                            if x1 < hx < x2 and y1 < hy < y2:
                                self.object_in_hand = label

            # Temporal Smoothing Logic
            self.detection_history.append(set(new_objs))
            
            # Aggregate counts
            all_counts = collections.Counter()
            for frame_objs in self.detection_history:
                for obj in frame_objs:
                    all_counts[obj] += 1
            
            # Threshold: Must appear in 50% of recent frames (3/6)
            smoothed_objs = [obj for obj, count in all_counts.items() if count >= 3]
            self.detected_objects = list(set(smoothed_objs))

        # 4. Presence
        self._analyze_presence()

        # 5. Visual HUD (Optional)
        if self.show_hud:
            self._draw_hud(frame, hand_landmarks, new_objs)

    def _run_deepface(self, frame):
        if not hasattr(self, 'deepface_module'): return
        self.deepface_locked = True
        try:
            # Face analysis
            objs = self.deepface_module.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
            if objs:
                self.face_count = len(objs)
                self.current_emotion = objs[0]['dominant_emotion'].capitalize()
        except Exception:
            pass
        finally:
            self.deepface_locked = False

    def _draw_hud(self, frame, hand_landmarks, objects):
        # 1. Overlay detected objects (YOLO Format)
        for det in self.current_detections:
            x1, y1, x2, y2 = det['bbox']
            label = det['label']
            conf = det['conf']
            
            # Draw cyan box with JARVIS aesthetic
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 2)
            cv2.putText(frame, f"{label} {int(conf*100)}%", (int(x1), int(y1) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
        # 2. Draw Hand Landmarks
        for hand in hand_landmarks:
            for landmark in hand:
                px, py = int(landmark.x * 640), int(landmark.y * 480)
                cv2.circle(frame, (px, py), 2, (0, 255, 255), -1)

        # 3. Status Text
        status_color = (0, 255, 0) if self.is_present else (0, 0, 255)
        cv2.putText(frame, f"STATUS: {'CONNECTED' if self.is_present else 'SCANNING'}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(frame, f"EMOTION: {self.current_emotion}", (20, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, f"FINGERS: {self.finger_count}", (20, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
        
        if self.object_in_hand:
            cv2.putText(frame, f"MANIPULATING: {self.object_in_hand}", (20, 130), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

        cv2.imshow("JARVIS TACTICAL HUD", frame)
        cv2.waitKey(1)

    def get_face_count(self): return self.face_count
    def get_detected_objects(self): return self.detected_objects
    def get_finger_count(self): return self.finger_count
    def get_emotion(self): return self.current_emotion
    def get_object_in_hand(self): return self.object_in_hand

    def stop(self):
        self.cap.release()
        if self.hand_landmarker: self.hand_landmarker.close()
        cv2.destroyAllWindows()

class ActivityTracker:
    def __init__(self, interval: float = 5.0):
        self.interval = interval
        self.last_app = None
        self.last_title = None
        self.start_time = time.time()

    def poll(self):
        if not ACTIVITY_AVAILABLE: return
        
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd: return
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            app_name = process.name()
            window_title = win32gui.GetWindowText(hwnd)
            
            if app_name != self.last_app or window_title != self.last_title:
                now = time.time()
                duration = now - self.start_time
                if self.last_app:
                    bus.publish("APP_SWITCHED", {
                        "app_name": app_name,
                        "window_title": window_title,
                        "old_app": self.last_app,
                        "duration": duration
                    })
                
                self.last_app = app_name
                self.last_title = window_title
                self.start_time = now
        except Exception:
            pass
