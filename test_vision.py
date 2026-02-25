try:
    import mediapipe as mp
    print("✅ MediaPipe loaded successfully.")
    hands = mp.solutions.hands.Hands()
    print("✅ Hands module initialized.")
    face = mp.solutions.face_mesh.FaceMesh()
    print("✅ FaceMesh module initialized.")
except Exception as e:
    print(f"❌ MediaPipe Error: {e}")
