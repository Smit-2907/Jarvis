from core.skills.base import BaseSkill

class VisionSkill(BaseSkill):
    def __init__(self):
        super().__init__("Vision", "Handles object detection, hand tracking, and biometric assessment.")
        self.keywords = [
            "see", "look", "camera", "scanning", "presence", "what is this", 
            "detect objects", "holding", "identify", "vision", "fingers", 
            "how many", "emotion", "feeling"
        ]

    def execute(self, command: str, context: dict) -> dict:
        vision = context.get("vision")
        personality = context.get("personality")
        name = context.get("user_name", "Sir")
        
        if not vision:
            return {"action": "SPEAK", "text": "I'm sorry, Sir, but my optic sensors are currently offline."}

        # 1. Hand Tracking & Finger Counting
        if any(word in command for word in ["fingers", "how many"]):
            count = vision.get_finger_count()
            if count > 0:
                return {"action": "SPEAK", "text": f"I detect {count} fingers extended on your hand, {name}."}
            return {"action": "SPEAK", "text": f"I can see your hands, {name}, but no fingers are currently extended."}

        # 2. Object in Hand / Identification
        if any(word in command for word in ["detect", "holding", "identify", "what is this", "what do you see"]):
            obj_in_hand = vision.get_object_in_hand()
            if obj_in_hand:
                return {"action": "SPEAK", "text": f"It appears you are holding a {obj_in_hand}, Sir. My sensors have cross-referenced the geometry and confirmed its identity."}
                
            objects = vision.get_detected_objects()
            if objects:
                if len(objects) == 1:
                    return {"action": "SPEAK", "text": f"My tactical scan identifies a {objects[0]} within your immediate vicinity, Sir."}
                else:
                    obj_str = ", ".join(objects[:-1]) + " and a " + objects[-1]
                    return {"action": "SPEAK", "text": f"Scanning highlights several distinct items in the perimeter, Sir: a {obj_str}."}
            else:
                return {"action": "SPEAK", "text": f"I'm analyzing the visual feed, {name}, but I cannot distinguish any specific objects with certainty at this moment."}

        # 3. Emotions
        if any(word in command for word in ["emotion", "feeling", "how do i look"]):
            emotion = vision.get_emotion()
            if emotion != "None":
                responses = {
                    "Happy": f"You look quite pleased, Sir. High morale is good for productivity.",
                    "Surprised": f"You seem startled, Sir. Is everything alright with the current task?",
                    "Focused": f"I detect a high level of concentration. I'll maintain silent monitoring.",
                    "Serious": f"You look quite determined, {name}. Focus mode is advised.",
                    "Neutral": f"Your expression is neutral, Sir. Steady as she goes."
                }
                return {"action": "SPEAK", "text": responses.get(emotion, f"Biometric scan suggests a {emotion} state, Sir.")}
            return {"action": "SPEAK", "text": "I'm having trouble analyzing your biometric markers at this angle, Sir."}

        # 4. Presence
        if any(word in command for word in ["see me", "look", "presence", "vision"]):
            count = vision.get_face_count()
            if count > 0:
                return {"action": "SPEAK", "text": f"I see you clearly, {name}. Biometric identity verified."}
            return {"action": "SPEAK", "text": "I can see the room, but I don't see any biological signatures in the frame."}

        return {}
