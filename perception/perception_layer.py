import cv2
import time
import threading
import os
import numpy as np
from core.event_bus import bus

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

class VisionPresence:
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.is_present = False
        self.last_state_change = 0
        self.face_count = 0
        self.finger_count = 0
        self.current_emotion = "Neutral"
        self.detected_objects = []
        self.object_in_hand = None
        
        # Initialize Tasks
        self.hand_landmarker = None
        self.face_landmarker = None
        self.object_detector = None
        
        if MEDIAPIPE_AVAILABLE:
            self._init_tasks()

        # Camera
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def _init_tasks(self):
        try:
            # 1. Hands
            hand_model = os.path.join("models", "hand_landmarker.task")
            if os.path.exists(hand_model):
                base_options = python.BaseOptions(model_asset_path=hand_model)
                options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
                self.hand_landmarker = vision.HandLandmarker.create_from_options(options)
                print("👁️ Tactical Hand Tracking active.")

            # 2. Face
            face_model = os.path.join("models", "face_landmarker.task")
            if os.path.exists(face_model):
                base_options = python.BaseOptions(model_asset_path=face_model)
                options = vision.FaceLandmarkerOptions(
                    base_options=base_options,
                    output_face_blendshapes=True,
                    output_facial_transformation_matrixes=True,
                    num_faces=1)
                self.face_landmarker = vision.FaceLandmarker.create_from_options(options)
                print("👁️ Biometric Face Analysis active.")

            # 3. Objects
            obj_model = os.path.join("models", "object_detector.tflite")
            if os.path.exists(obj_model):
                base_options = python.BaseOptions(model_asset_path=obj_model)
                options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.3)
                self.object_detector = vision.ObjectDetector.create_from_options(options)
                print("👁️ Object Recognition system active.")
        except Exception as e:
            print(f"⚠️ Vision Task Init Error: {e}")

    def _analyze_emotion(self, blendshapes):
        """Map blendshapes to emotions."""
        # MediaPipe blendshapes provide categories like 'eyeBlinkLeft', 'jawOpen', etc.
        shapes = {s.category_name: s.score for s in blendshapes[0]}
        
        if shapes.get('jawOpen', 0) > 0.4: return "Surprised"
        if (shapes.get('mouthSmileLeft', 0) + shapes.get('mouthSmileRight', 0)) > 0.6: return "Happy"
        if (shapes.get('browDownLeft', 0) + shapes.get('browDownRight', 0)) > 0.4: return "Serious/Focused"
        if (shapes.get('mouthPucker', 0)) > 0.3: return "Thinking"
        return "Neutral"

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
            res = self.hand_landmarker.detect(mp_image)
            if res.hand_landmarks:
                hand_landmarks = res.hand_landmarks
                for hand in res.hand_landmarks:
                    # Tips: 8, 12, 16, 20. Thumb: 4.
                    for tip in [8, 12, 16, 20]:
                        if hand[tip].y < hand[tip-2].y: self.finger_count += 1
                    # Thumb
                    if hand[4].x < hand[3].x: self.finger_count += 1

        # 2. Face & Emotion
        self.face_count = 0
        if self.face_landmarker:
            res = self.face_landmarker.detect(mp_image)
            if res.face_landmarks:
                self.face_count = 1
                if res.face_blendshapes:
                    self.current_emotion = self._analyze_emotion(res.face_blendshapes)
            else:
                self.current_emotion = "None"

        # 3. Objects & In-Hand detection
        self.object_in_hand = None
        if self.object_detector:
            res = self.object_detector.detect(mp_image)
            new_objs = []
            for det in res.detections:
                label = det.categories[0].category_name
                new_objs.append(label)
                
                # Hand proximity
                bbox = det.bounding_box
                if hand_landmarks:
                    bx, by, bw, bh = bbox.origin_x/640, bbox.origin_y/480, bbox.width/640, bbox.height/480
                    for hand in hand_landmarks:
                        hx, hy = hand[9].x, hand[9].y
                        if bx < hx < bx + bw and by < hy < by + bh:
                            self.object_in_hand = label
            self.detected_objects = list(set(new_objs))

        # 4. Presence
        now = time.time()
        now_present = self.face_count > 0
        if now_present != self.is_present:
            if now - self.last_state_change > 3:
                self.is_present = now_present
                self.last_state_change = now
                bus.publish("USER_PRESENT" if now_present else "USER_LEFT", {"emotion": self.current_emotion})

    def get_face_count(self): return self.face_count
    def get_detected_objects(self): return self.detected_objects
    def get_finger_count(self): return self.finger_count
    def get_emotion(self): return self.current_emotion
    def get_object_in_hand(self): return self.object_in_hand

    def stop(self):
        self.cap.release()
        if self.hand_landmarker: self.hand_landmarker.close()
        if self.face_landmarker: self.face_landmarker.close()
        if self.object_detector: self.object_detector.close()
