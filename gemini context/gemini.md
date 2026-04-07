# LockedIn Project Overview
LockedIn is an AI-powered proctoring and interview preparation system. It combines a coding environment with computer vision (MediaPipe/OpenCV) and audio monitoring to simulate secure, locked-in exam environments and track cheating behaviors (looking away, talking, multiple faces, switching tabs).

## Current Understanding
- **Purpose:** LockedIn is a web-based, AI-proctored coding interview simulator. It watches user behavior (head pose, eyes, audio, tab switches) while they solve algorithm problems in a browser-based Monaco editor.
- **Backend:** Flask powers the backend. It handles authentication, database connections (SQLite), video streaming via OpenCV, code execution (using `subprocess` in temp dirs), and proctoring logic.
- **AI Modules:** Uses MediaPipe for face/iris tracking (`tracker.py`), PyAudio for noise detection (`audio_monitor.py`), and Google Gemini 2.0 API for technical code evaluation and verbal behavioral mock interviews.
- **Frontend:** Single-page application (`frontend/index.html`) using Vanilla JS, TailwindCSS, Monaco Editor, and Chart.js for post-session analytics (Skill Radar Charts and progression tracking).
- **Key Mechanics:**
  - Timer-based session limits across Technical Coding, CS Aptitude, and Behavioral interview modules.
  - Video feed overlays violation alerts (e.g., "VIOLATION (LOOK AWAY)").
  - Executing code tracks both syntax and logic errors, contributing to an overall profile score/EXP.
  - Voice-to-voice AI behavioral interviews with transcript generation and AI summary reports.
  - Generates detailed session reports (level reached, violations, time per level, behavioral feedback, aptitude scores).

## Tech Stack
- **Backend:** Python 3.10+, Flask, SQLite (`lockedin.db`)
- **AI/Proctoring/Interviewer:** OpenCV, MediaPipe (Face Mesh), PyAudio, NumPy, Google Gemini API
- **Frontend:** Vanilla HTML/CSS/JS, TailwindCSS, Monaco Editor, Chart.js

## Key Directories
- `backend/`: Core server logic (`server.py`, `main.py`) and database interactions (`database.py`).
- `backend/ai_proctor/`: Specialized AI tracking modules (`tracker.py`, `audio_monitor.py`, `scorer.py`).
- `frontend/`: Web interface (`index.html`) and assets.   
- `gemini context/report/`: Presentation and report outlines with mermaid diagrams (`presentation.md`, `report.md`).

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