import re
from core.skills.base import BaseSkill

class VisionLearningSkill(BaseSkill):
    def __init__(self):
        super().__init__("VisionLearning", "Allows manually correcting JARVIS's vision detections.")
        self.keywords = ["no that's a", "actually that is", "that isn't a", "it's a", "it is a"]

    def execute(self, command: str, context: dict) -> dict:
        vision = context.get("vision")
        if not vision:
            return {}

        # Last objects seen (for context)
        last_objs = vision.get_detected_objects()
        obj_in_hand = vision.get_object_in_hand()
        
        # We need a target to correct. If user says "no that's a pen", we need to know what we called it before.
        # For simplicity, we'll assume the most recent 'sensitive' or 'wrong' detection.
        # In a real Stark AI, we'd use the chat history.
        
        match = re.search(r"(?:no that's a|actually it's a|it's a) (.*)", command)
        if match:
            new_label = match.group(1).strip().replace(".", "")
            
            # Logic: If JARVIS recently said 'knife' and user says 'pen', map knife -> pen.
            # We'll check the last 3 detections for a 'common' misidentification.
            candidates = ["knife", "scissors", "toothbrush", "cell phone"]
            target = None
            
            # Use obj_in_hand as primary target if available
            if obj_in_hand and obj_in_hand in candidates:
                target = obj_in_hand
            elif last_objs:
                for o in last_objs:
                    if o in candidates:
                        target = o
                        break
            
            if target:
                vision.learn_object(target, new_label)
                return {"action": "SPEAK", "text": f"Understood, Sir. I've updated my neural mapping. I'll henceforth recognize that geometry as a {new_label}."}
            else:
                return {"action": "SPEAK", "text": "I'm listening, Sir, but I'm not sure which detection you are referring to. Could you be more specific?"}

        return {}
