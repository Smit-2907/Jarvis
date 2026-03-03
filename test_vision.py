import sys
import os

print("🔍 J.A.R.V.I.S. Vision Diagnostics")
print("==================================")

try:
    import mediapipe as mp
    print(f"✅ MediaPipe Core: Installed (v{getattr(mp, '__version__', 'unknown')})")
    
    # Check Tasks API (What J.A.R.V.I.S. actually uses)
    print("📋 Checking Tasks API...", end=" ", flush=True)
    try:
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        print("READY")
        
        # Test Task initialization if model exists
        model_path = "models/hand_landmarker.task"
        if os.path.exists(model_path):
            print(f"📋 Testing Hand Landmarker initialization...", end=" ", flush=True)
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
            landmarker = vision.HandLandmarker.create_from_options(options)
            print("SUCCESS")
        else:
            print(f"⚠️ Model missing: {model_path}")
    except Exception as e:
        print(f"FAILED: {e}")

    # Check Legacy Solutions (Optional/Testing)
    print("📋 Checking Legacy Solutions API...", end=" ", flush=True)
    try:
        import mediapipe.solutions.hands as mp_hands
        print("READY")
    except Exception as e:
        print(f"UNAVAILABLE (Common in v0.10+)")

except ImportError:
    print("❌ MediaPipe is NOT installed. Run 'uv sync' or 'pip install mediapipe'.")

print("\n🚀 Ready to start JARVIS? Run: python main.py")


