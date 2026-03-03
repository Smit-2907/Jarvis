try:
    print("🔍 Testing MediaPipe Version 3 (direct sub-module) logic...")
    import mediapipe.solutions.hands as mp_hands
    print("✅ Direct import successful.")
    hands = mp_hands.Hands()
    print("✅ Hands initialized.")
except Exception as e:
    print(f"❌ Direct Import Error: {e}")
    print("💡 Note: J.A.R.V.I.S. uses mediapipe.tasks which is more robust in newer versions.")

    print("💡 Suggestion: Use the 'Tasks' API as implemented in perception_layer.py")
