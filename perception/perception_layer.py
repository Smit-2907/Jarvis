import cv2
import time
import threading
import os
from core.event_bus import bus

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

class VisionPresence:
    def __init__(self, interval: float = 2.0):
        self.interval = interval
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.is_present = False
        self.last_state_change = 0
        self.face_count = 0
        self.detected_objects = []
        
        # Initialize camera once
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("⚠️ Warning: Could not open camera.")

        self.model_path = os.path.join("models", "object_detector.tflite")
        self.detector = None
        
        if MEDIAPIPE_AVAILABLE and os.path.exists(self.model_path):
            try:
                base_options = python.BaseOptions(model_asset_path=self.model_path)
                options = vision.ObjectDetectorOptions(base_options=base_options,
                                                        score_threshold=0.35,
                                                        max_results=5)
                self.detector = vision.ObjectDetector.create_from_options(options)
                print("👁️ Object Detection model loaded successfully.")
            except Exception as e:
                print(f"⚠️ Could not initialize Object Detector: {e}")

    def poll(self):
        """Polls the camera for face presence and objects."""
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # 1. Face Detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        self.face_count = len(faces)
        
        # 2. Object Detection (Run only if detector is available)
        if self.detector:
            try:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                detection_result = self.detector.detect(mp_image)
                
                new_objects = []
                for detection in detection_result.detections:
                    category = detection.categories[0]
                    new_objects.append(category.category_name)
                
                self.detected_objects = list(set(new_objects)) # Unique objects
            except Exception as e:
                pass

        now_present = self.face_count > 0
        now = time.time()
        
        if now_present != self.is_present:
            if now - self.last_state_change > 5:
                self.is_present = now_present
                self.last_state_change = now
                event = "USER_PRESENT" if now_present else "USER_LEFT"
                bus.publish(event, {"timestamp": now})

    def get_face_count(self):
        return self.face_count

    def get_detected_objects(self):
        return self.detected_objects

    def stop(self):
        if self.cap:
            self.cap.release()
        if self.detector:
            self.detector.close()

class ActivityTracker:
    def __init__(self, interval: float = 5.0):
        self.interval = interval
        self.current_app = None
        self.last_poll = time.time()

    def poll(self):
        import psutil
        import win32gui
        import win32process

        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd: return
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            app_name = process.name()
            
            if app_name != self.current_app:
                self.current_app = app_name
                bus.publish("APP_SWITCHED", {"app_name": app_name, "title": win32gui.GetWindowText(hwnd)})
        except:
            pass
