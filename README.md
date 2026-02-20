#  Jarvis Autonomous Agent v2.0

> "At your service, Sir."

Jarvis is a local-first, autonomous personal intelligence system designed to monitor productivity, assist with automation, and provide a sophisticated conversational interface. Inspired by the legendary Stark Industries AI, this system combines computer vision, offline speech recognition, and an event-driven decision engine to create a seamless interactive experience.

---

## 🌟 Key Features

### 🧠 Advanced Cognition
- **Fuzzy Intent Matching:** Understands commands even through noisy microphone transcriptions (e.g., "Kenya switch" → "Can you switch").
- **Continuous Listening:** A smart 8-second conversational window allows for natural back-and-forth without repeating the wake word.
- **Dynamic Learning:** Teach Jarvis new rules on the fly. *"Jarvis, learn that 'coffee time' means 'open Spotify'."*
- **Iron Man Persona:** Authentic JARVIS personality, including "Sir" addressing and a sophisticated British tone.

### 👁️ Perception Layer
- **Persistent Vision:** Real-time face detection and presence monitoring using OpenCV.
- **Activity Tracking:** Monitors active applications to detect distractions and calculate productivity scores.

---

## 🚀 Getting Started (Setup Guide)

Follow these steps to get Jarvis running on your local machine.

### 1. Prerequisites
- **OS:** Windows 10 or 11 (Highly recommended)
- **Python:** 3.10 or higher installed.
- **Microphone & Webcam:** Required for audio/vision features.

### 2. Download the AI Model (CRITICAL)
Jarvis uses **Vosk** for offline speech recognition. You MUST download the model manually:
1. Download the English model: [vosk-model-small-en-us-0.15.zip](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip)
2. Create a folder named `models` in the project root.
3. Extract the zip file into that folder. Your folder structure should look like this:
   ```text
   jarvis/
   ├── models/
   │   └── vosk-model-small-en-us-0.15/  <-- Model files go here
   ├── main.py
   └── ...
   ```

### 3. Installation

#### Option A: Using `uv` (Recommended)
If you have `uv` installed:
```powershell
uv sync
uv run main.py
```

#### Option B: Using `pip`
If you prefer standard pip:
```powershell
# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Jarvis
python main.py
```

---

## 🏗️ Folder Structure
```text
jarvis/
├── action/             # TTS and Automation logic
├── config/             # YAML settings and learned rules
├── core/               # Engine, Event Bus, and State Machine
├── memory/             # SQLite database and short-term RAM
├── perception/         # Camera and Microphone drivers
└── main.py             # Entry point
```

---

## 💬 Common Commands
Once the microphone is active (look for the 🎙 icon), try saying:

- **Greet:** *"Hello Jarvis"*
- **Identity:** *"Who are you?"*
- **Math:** *"What is 150 times 2 plus 5?"*
- **Status:** *"Jarvis, status report"*
- **Personality:** *"Tell me a joke"*
- **Shutdown:** *"Jarvis, go offline"* or *"Shutdown"*

---

## ⚙️ Configuration
You can tweak Jarvis's behavior in `config/config.yaml`:
- Change `personality` to `Jarvis`, `Professional`, or `Friendly`.
- Adjust `voice_rate` to change how fast he speaks.
- Toggle `vision` or `audio` modules on/off.

---

## 🔒 Privacy & Security
- **100% Offline:** No audio or video data is ever sent to the cloud.
- **Local Database:** Your productivity logs are stored in a local SQLite file (`memory/jarvis_v2.db`).
- **No API Keys:** No OpenAI or Google Cloud keys required.

---

*“I’ve already compiled a list of your favorites, Sir.”*
