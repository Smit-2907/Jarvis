try:
    from mediapipe.python.solutions import hands as mp_hands
    from mediapipe.python.solutions import face_mesh as mp_face_mesh
    print("✅ Solutions imported via mediapipe.python.solutions")
    hands = mp_hands.Hands()
    print("✅ Hands initialized.")
except Exception as e:
    print(f"❌ Version 2 Error: {e}")
