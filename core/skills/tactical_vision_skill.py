import random
from core.skills.base import BaseSkill

class TacticalVisionSkill(BaseSkill):
    def __init__(self):
        super().__init__("TacticalVision", "Provides advanced environmental assessments.")
        self.keywords = ["tactical", "assessment", "scan the room", "environment report", "threat level", "full scan"]

    def execute(self, command: str, context: dict) -> dict:
        vision = context.get("vision")
        name = context.get("user_name", "Sir")
        
        if not vision:
            return {"action": "SPEAK", "text": "Tactical sensors are currently offline, Sir."}

        objects = vision.get_detected_objects()
        faces = vision.get_face_count()
        emotion = vision.get_emotion()
        obj_in_hand = vision.get_object_in_hand()
        
        report = f"Initiating high-fidelity tactical scan, {name}. Stand by... "
        
        # 1. Biometrics
        if faces > 0:
            report += f"Bio-signature detected. Identity confirmed as {name}. "
            if emotion != "None":
                report += f"Current cognitive state evaluated as {emotion}. "
        
        # 2. Objects & Manipulations
        if objects:
            report += f"Optical sensors identify {len(objects)} kinetic objects in the perimeter. "
            if obj_in_hand:
                report += f"Primary manipulation detected: you are currently utilizing a {obj_in_hand}. "
            
            # Specific object alerts
            if "cell phone" in objects:
                report += "External communication device present. "
            if "laptop" in objects or "keyboard" in objects:
                report += "Workstation interface is active and nominal. "
        else:
            report += "No significant anomalies detected in the immediate environment. "
            
        # 3. Threat Level
        threat = "nominal" if emotion != "Surprised" else "slightly elevated due to a detected startle response"
        report += f"Ambient threat level is currently {threat}. All local systems are stable and the environment is secured, Sir."
        
        return {"action": "SPEAK", "text": report}
