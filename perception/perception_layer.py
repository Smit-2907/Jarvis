import cv2
import time
import threading
from core.event_bus import bus

class VisionPresence:
    def __init__(self, interval: float = 2.0):
        self.interval = interval
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.is_present = False
        self.last_state_change = 0
        self.face_count = 0
        
        # Initialize camera once
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("⚠️ Warning: Could not open camera.")

    def poll(self):
        """Polls the camera for face presence."""
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # Simple Face Detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        self.face_count = len(faces)
        
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

    def stop(self):
        if self.cap:
            self.cap.release()

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
