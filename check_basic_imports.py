import os
import time
import sys

# Force output to handle encoding better
# sys.stdout.reconfigure(encoding='utf-8') # Only in Python 3.7+ 

def test_import(module_name):
    print(f"Testing {module_name}...", end=" ", flush=True)
    start = time.time()
    try:
        __import__(module_name)
        end = time.time()
        print(f"SUCCESS ({end - start:.2f}s)")
    except Exception as e:
        print(f"FAIL: {e}")

# Basic deps
test_import("numpy")
test_import("cv2")
test_import("yaml")
test_import("psutil")
test_import("win32gui")
test_import("pyttsx3")

# Heavy AI deps
test_import("mediapipe")
test_import("vosk")
test_import("ultralytics")
test_import("deepface")
