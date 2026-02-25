#  J.A.R.V.I.S. Autonomous Companion v3.0

> "At your service, Sir. I've taken the liberty of optimizing all background tasks."

J.A.R.V.I.S. (Just A Rather Very Intelligent System) is a local-first, autonomous personal intelligence system designed for deep productivity, proactive assistance, and immersive interaction. Inspired by the legendary Stark Industries AI, this system combines high-fidelity computer vision, offline speech recognition, and an event-driven modular skill engine to create a truly sentient-feeling desktop companion.

---

## 🌟 Key Features

### 🧠 Advanced Sentience (v3.0)
- **Modular Skill Engine:** A highly scalable architecture with specialized skills for everything from math and vision to system automation and web research.
- **Companion Context:** Remembers the last 8 exchanges to maintain natural, ongoing conversations without context loss.
- **Proactive Intelligence:** Jarvis performs background check-ins if he detects you are present but idle, and coaching notifications if you lose focus.
- **Neural Processing Simulation:** Abstract queries trigger a visual "synapse simulation" in the terminal, showing the AI's internal logic flow.
- **Interruption Protocol:** Say *"Stop"* or *"Listen Jarvis"* to immediately silence his audio feed.

### 👁️ Tactical Vision v3.0
- **MediaPipe Tasks Integration:** Utilizes high-performance landmarker models for sub-millimeter tracking.
- **Finger Counting & Gesture Tracking:** Jarvis can count exactly how many fingers you are holding up and track hand movements with high precision.
- **Biometric Emotion Analysis:** Analyzes 52 face blendshapes to detect cognitive states like **Happy**, **Focused**, **Surprised**, or **Serious**.
- **Spatial Awareness:** Detects when you are holding objects by cross-referencing hand position with identified items.
- **Activity Intelligence:** Automatically logs application usage and calculates productivity scores in an offline SQLite database.

### 🔊 Sonic Presence
- **Fluent TTS:** A custom-tuned speech engine with sentence-level pacing, phonetic smoothing, and natural breath pauses.
- **Visual Waveforms:** Every word Jarvis speaks is accompanied by a dynamic ASCII waveform (` ▂▃▄▅▆▇█`) in your terminal.
- **British Vocal Core:** Optimized for high-quality British English synthesis for the authentic "Stark Industries" experience.

---

## 🚀 Getting Started (Setup Guide)

### 1. Prerequisites
- **OS:** Windows 10 or 11 (Optimized for PowerShell and System TTS)
- **Python:** 3.10+
- **Microphone & Webcam:** Required for full peripheral awareness.

### 2. Download Offline Models
Jarvis requires local models for speech and vision:
1. **Speech:** Download [vosk-model-small-en-us-0.15.zip](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip).
2. **Vision:** Hand and Face landmarker tasks are auto-downloaded or can be placed in `models/`.

### 3. Installation
Using `uv` for high-performance dependency management:
```powershell
uv add mediapipe numpy
uv sync
uv run main.py
```

---

## 🏗️ The Skill System
Jarvis is fully modular. Each "Skill" is a standalone unit:
- `WebSearchSkill`: Intelligent subject extraction for refined Google research.
- `SystemHealthSkill`: Visual ASCII HUD for CPU/RAM/Battery diagnostics.
- `VisionSkill`: Biometric analysis, hand tracking, and object-in-hand logic.
- `AutomationSkill`: Voice-controlled screenshots, PC locking, and brightness.
- `ProtocolSkill`: High-level routines like "Protocol Zero" or "Deep Work".
- `DeepThoughtSkill`: Abstract analysis and sentient banter.

---

## 💬 Tactical Commands
- **Protocols:** *"Jarvis, engage Protocol Deep Work"* or *"Activate Protocol Zero"*
- **Diagnostics:** *"Give me a full system diagnostic"*
- **Vision:** *"How many fingers am I holding up?"* or *"What's my current emotion?"*
- **Spatial:** *"What am I holding?"* or *"Scan the room"*
- **Research:** *"Research the latest advancements in fusion power"*
- **Banter:** *"Are you human?"*, *"Who is Tony Stark?"*, *"Thanks for the help"*

---

## 🔒 Privacy & Security
- **100% Local:** No cloud APIs. No data leaves your machine.
- **Encrypted Memory:** All learned rules and activity logs are stored locally.
- **No subscription fees:** Runs entirely on your hardware.

---

*“Honestly, Sir, I have all of a human's sophistication with none of the biological overhead.”*
