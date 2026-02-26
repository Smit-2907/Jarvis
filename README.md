#  J.A.R.V.I.S. Autonomous Companion v4.0 (Strategic Optical Upgrade)

> "At your service, Sir. I've upgraded the optical sensors and synchronized the global datastreams."

J.A.R.V.I.S. (Just A Rather Very Intelligent System) is a local-first, autonomous personal intelligence system designed for deep productivity, proactive assistance, and immersive interaction. This system combines **YOLOv8** object detection, **DeepFace** biometrics, **MediaPipe** hand tracking, and a local **Ollama** intelligence core to create a truly sentient-feeling desktop companion.

---

## 🌟 Key Features

### 🧠 OmniBrain Intelligence (v4.0)
- **Ollama Integration:** Powered by a local **Mistral 7B** model for advanced reasoning, witty banter, and complex problem-solving.
- **Global Datastream Uplink:** Integrated **DuckDuckGo Search** for real-time news, weather, and world data.
- **Multimodal Context:** Jarvis combines what he *sees* (camera) with what he *knows* (LLM) and what you *do* (activity tracking) into every response.
- **Contextual Memory:** Persistent conversation history ensures he remembers exactly what you discussed 5 minutes ago.

### 👁️ Strategic Vision v4.0
- **YOLOv8 Neural Core:** High-fidelity object detection capable of identifying 80+ classes (stationary and dynamic) with pinpoint accuracy.
- **DeepFace Biometrics:** Advanced facial analysis for precise emotion classification (Happy, Serious, Surprised, etc.) and future identity verification.
- **MediaPipe Hand Lab:** Low-latency hand tracking for finger counting and spatial interaction.
- **Tactical HUD:** A real-time visual overlay highlighting every detected object and metric in his field of view.

### 🔊 Sonic Presence
- **Indian English Vosk Model:** Optimized for Indian accents with a high-fidelity 1GB acoustic model.
- **Self-Deafness Protocol:** Jarvis automatically ignores his own voice to prevent feedback loops during speech.
- **Fluent TTS:** Custom-tuned Microsoft British synthesis with phonetic smoothing.

---

## 🚀 Getting Started (Setup Guide)

### 1. Prerequisites
- **OS:** Windows 10 or 11
- **Hardware:** 8GB+ RAM (Recommended for local LLM)
- **Software:** [Ollama](https://ollama.com/) (Must be running with `mistral` model installed)

### 2. Download Offline Models
Jarvis requires local models for speech and vision:
1. **Speech:** Download the **Indian English** model and place it in `models/vosk-model-en-in-0.5`.
2. **Vision:** YOLOv8 and DeepFace weights are auto-downloaded on first run (~15MB total).
3. **Hands:** `hand_landmarker.task` belongs in the `models/` folder.

### 3. Installation

**From GitHub (Quick Start)**
1. **Clone the repo:**
   ```powershell
   git clone https://github.com/Smit-2907/Jarvis.git
   cd Jarvis
   ```
2. **Run the One-Click Setup:**
   ```powershell
   ./setup.ps1
   ```

**Option B: Manual Installation**
If you prefer manual control:
```powershell
uv sync
uv run main.py
```

---

## 🏗️ The Skill System
Jarvis is fully modular. His core intelligence is handled by the **OmniBrain**, while specialized actions are siloed:
- `OmniBrainSkill`: The "Primary reasoning core" combining LLM, Search, and Vision.
- `AppLauncherSkill`: Voice-activated app, folder, and website opener.
- `SystemHealthSkill`: Real-time hardware diagnostics (CPU/RAM).
- `VisionSkill`: Dedicated telemetry for hands and biometric markers.
- `MediaSkill`: Volume and playback control.

---

## 💬 Tactical Commands
- **Intelligence:** *"Jarvis, explain the theory of relativity"* or *"What is the latest SpaceX news?"*
- **Vision:** *"Jarvis, scan the environment and identify everything you see"* or *"How am I looking today?"*
- **Utility:** *"Open Google Chrome"*, *"Search for the best productivity hacks"*, or *"What is 45 percent of 1200?"*
- **Control:** *"Jarvis, stop"*, *"Go offline"*, or *"System status check"*

---

## 🔒 Privacy & Security
- **100% Local Logic:** Your voice and face never leave your machine.
- **Transparent Processing:** All neural synthetic steps are logged in real-time in the terminal.
- **No API Keys:** Runs entirely on local hardware (Ollama + TFLite + ONNX).

---

*“Honestly, Sir, I have all of a human's sophistication with none of the biological overhead.”*
