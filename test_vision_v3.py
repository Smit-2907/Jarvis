try:
    import mediapipe.solutions.hands as mp_hands
    print("✅ Direct import successful.")
    hands = mp_hands.Hands()
    print("✅ Hands initialized.")
except Exception as e:
    print(f"❌ Direct Import Error: {e}")
