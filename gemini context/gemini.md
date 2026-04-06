# LockedIn Project Overview
LockedIn is an AI-powered proctoring and interview preparation system. It combines a coding environment with computer vision (MediaPipe/OpenCV) and audio monitoring to simulate secure, locked-in exam environments and track cheating behaviors (looking away, talking, multiple faces, switching tabs).

## Current Understanding
- **Purpose:** LockedIn is a web-based, AI-proctored coding interview simulator. It watches user behavior (head pose, eyes, audio, tab switches) while they solve algorithm problems in a browser-based Monaco editor.
- **Backend:** Flask powers the backend. It handles authentication, database connections (SQLite), video streaming via OpenCV, code execution (using `subprocess` in temp dirs), and proctoring logic.
- **AI Modules:** Uses MediaPipe for face/iris tracking (`tracker.py`) and PyAudio for noise detection (`audio_monitor.py`).
- **Frontend:** Single-page application (`frontend/index.html`) using Vanilla JS, TailwindCSS, Monaco Editor, and Chart.js for post-session analytics.
- **Key Mechanics:**
  - Timer-based session limits.
  - Video feed overlays violation alerts (e.g., "VIOLATION (LOOK AWAY)").
  - Executing code tracks both syntax and logic errors, contributing to an overall profile score/EXP.
  - Generates detailed session reports (level reached, violations, time per level).

## Tech Stack
- **Backend:** Python 3.10+, Flask, SQLite (`lockedin.db`)
- **AI/Proctoring:** OpenCV, MediaPipe (Face Mesh), PyAudio, NumPy
- **Frontend:** Vanilla HTML/CSS/JS, TailwindCSS, Monaco Editor, Chart.js

## Key Directories
- `backend/`: Core server logic (`server.py`, `main.py`) and database interactions (`database.py`).
- `backend/ai_proctor/`: Specialized AI tracking modules (`tracker.py`, `audio_monitor.py`, `scorer.py`).
- `frontend/`: Web interface (`index.html`) and assets.

## Build and Test Commands
- **Setup:** `python -m venv venv` and `pip install -r requirements.txt`
- **Run Server:** `python backend/server.py`
- **Run Local Proctor Test:** `python backend/main.py`
- **Access DB:** The app uses a local SQLite DB (`lockedin.db`) managed via `backend/database.py`.

## Checkpointing Strategy
- Active Branch: `Gemini-CLI-1` (Created as a separate branch from `main`).
- Commits will be proposed clearly with the "why" before staging.

## Additional Documentation
For deeper architectural context and conventions, please check:
- [Architectural Patterns](architectural_patterns.md)
