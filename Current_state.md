# Project Current State: LockedIn

**LockedIn** is an AI-powered proctoring and interview preparation platform. It combines a Monaco-based coding environment with real-time computer vision (MediaPipe Face Mesh) and audio monitoring to simulate a secure exam environment, flag cheating behaviors (such as looking away, talking, multiple faces in frame, or switching browser tabs), and offer immediate technical/behavioral feedback powered by Google's Gemini API.

---

## 1. Project Folder & File Structure

Here is the exact layout of the repository as it stands:

```
LockedIn/
├── .env                          # Local credentials (Gemini API Key, ElevenLabs API Key)
├── .gitignore                    # Git ignore file (excludes venv, pycache, lockedin.db)
├── lockedin.db                   # SQLite database file storing users, sessions, and questions
├── README.md                     # Project README (currently empty)
├── requirements.txt              # Python library dependencies
├── venv/                         # Python virtual environment folder
│
├── backend/                      # Python Flask Backend
│   ├── main.py                   # Standalone OpenCV webcam testing script
│   ├── server.py                 # Main Flask server (APIs, auth, routing, Gemini integration)
│   ├── database.py               # SQLite schema initialization, query utils, profile summaries
│   │
│   └── ai_proctor/               # Special AI Proctoring & Logic modules
│       ├── __init__.py           # Package init
│       ├── audio_monitor.py      # RMS-based sound levels and voice detection (PyAudio)
│       ├── questions.py          # Adaptive coding challenges (Levels 1-5) and test cases
│       ├── scorer.py             # Calculations for Cheat Score and Integrity Percentage
│       └── tracker.py            # MediaPipe Face Mesh head-pose and iris-gaze tracking
│
├── frontend/                     # Vanilla HTML/JS UI Assets
│   ├── index.html                # Single-page app (TailwindCSS, Monaco Editor, Chart.js, JS logic)
│   └── fonts/                    # Custom styling fonts
│       └── NatureBeautyPersonalUse-9Y2DK.ttf
│
├── gemini context/               # Project documentation & reference notes
│   ├── architectural_patterns.md # Summary of global state, background workers, and isolation
│   ├── gemini.md                 # Brief project summary, tech stack, and active branch info
│   ├── planning.md               # Future features roadmap and design constraints
│   │
│   └── report/                   # Detailed academic-style documents
│       ├── presentation.md       # 10-slide presentation outline with Mermaid Diagrams
│       └── report.md             # In-depth technical project report with ER/DFD/Sequence diagrams
│
└── img/                          # Screenshots, mockups, and exported diagrams
    ├── diagrams/                 # DFD, ER, Sequence, and System flow images and text files
    └── [various UI images].png   # UI elements and page layout references
```

---

## 2. Component Analysis & Standings

### A. Backend (`backend/`)
- **`server.py`**: Serves as the central API gateway. It:
  - Manages a thread-safe webcam instance using `threading.Lock()` to process and stream frames.
  - Implements API endpoints for user registration, login, profile stats, question retrieval, verbal chat sessions, and behavioral evaluations.
  - Hosts the `/run_code` execution endpoint, which compiles and runs student code locally (Python, Java, and JavaScript supported) inside a `tempfile.TemporaryDirectory` via Python's `subprocess.run` to securely check assertions.
  - Integrates the `google-genai` SDK using `gemini-2.5-flash` for code evaluations and conversational behavioral interviews.
- **`database.py`**: Initializes and updates the SQLite database. Configures default CS aptitude questions on startup and tracks points, ranks, and logs.
- **`main.py`**: A CLI script designed for testing. It spins up the webcam, tracks eyes, checks noise levels, runs the adaptive difficulty loop, and exits with a command-line printout of the final integrity score.

### B. AI Proctoring Module (`backend/ai_proctor/`)
- **`tracker.py`**: Uses MediaPipe Face Mesh to identify head movements and eye direction. If the nose coordinate goes beyond `0.40 - 0.60` of the screen width, or the eye iris-to-eye-corner ratio moves outside the `0.35 - 0.65` normal boundary, the user is flagged as "Looking Away".
- **`audio_monitor.py`**: Leverages PyAudio to capture microphone feeds. If the root-mean-square (RMS) level of the buffer spikes above `150` (configurable), a noise violation is recorded.
- **`scorer.py`**: Translates violations (1 point per second eyes away, 2 points per audio spike, 5 points per second multiple faces) into a `cheat_score` (out of 100). The integrity score is calculated as `100 - cheat_score`.

### C. Frontend UI (`frontend/`)
- **`index.html`**: A comprehensive single-page web app built on TailwindCSS. Key interfaces include:
  - **Workspace (Editor)**: Displays active coding questions, a camera feed showing proctoring states, a Monaco code editor, and console outputs. 
  - **Career Hub (Dashboard)**: Provides user profiles, progression levels, a list of past attempts, and a custom Chart.js Radar Chart mapping mastery levels across topics like Arrays, DP, and Strings.
  - **Core CS Aptitude**: Runs a timed 10-question multiple-choice exam, displaying immediate grade feedback upon completion.
  - **Behavioral Mock**: An interactive vocal prep screen using the browser's Web Speech API (for input) and Text-to-Speech (for AI speech outputs) to simulate interviews with Gemini.
- **Keystroke Dynamics**: Embedded JS inside Monaco detects unnatural keypress rates (< 10ms delay between keys) or large text block pastes (> 50 characters) and posts violations to the server.
- **Tab Switching**: Monitors the document `visibilitychange` event to detect tab/window leaving.

---

## 3. Database Schema

The database `lockedin.db` contains three main tables:

### 1. `users`
Tracks individual accounts, accumulated experience points, and progression titles.
- `id` (INTEGER, Primary Key)
- `username` (TEXT, Unique)
- `password` (TEXT, Hashed)
- `total_points` (INTEGER, Default: 0)
- `rank` (TEXT, e.g., 'Code Initiate', 'Syntax Soldier', 'Senior Scripter', 'Logic Master', '7-Star Architect')

### 2. `sessions`
Records performance stats and AI proctor flags for every test taken.
- `id` (INTEGER, Primary Key)
- `user_id` (INTEGER, Foreign Key referencing `users(id)`)
- `max_level` (INTEGER)
- `violations` (INTEGER)
- `syntax_errors` (INTEGER)
- `logic_errors` (INTEGER)
- `violation_logs` (TEXT, JSON string)
- `level_times` (TEXT, JSON string)
- `categories_completed` (TEXT, JSON string)
- `aptitude_score` (INTEGER, Nullable)
- `behavioral_feedback` (TEXT, Nullable)
- `timestamp` (DATETIME, Default: CURRENT_TIMESTAMP)

### 3. `aptitude_questions`
Maintains a pool of multiple-choice questions for CS quizzes.
- `id` (INTEGER, Primary Key)
- `question` (TEXT)
- `option_a` (TEXT)
- `option_b` (TEXT)
- `option_c` (TEXT)
- `option_d` (TEXT)
- `correct_answer` (TEXT)
- `category` (TEXT)

---

## 4. Run & Stop Commands

### Setup & Activation
Before running either component, ensure you have the virtual environment activated and dependencies installed:
```powershell
# 1. Activate Virtual Environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 2. Verify / Install Dependencies
pip install -r requirements.txt
```

### Option A: The Full Web Application (Frontend + Backend)
*Runs the Flask server which serves the web application, handles authentication, runs the code compiler, and coordinates Gemini AI features.*

- **Starting Command:**
  ```powershell
  python backend/server.py
  ```
  *Note: Upon starting, the script will wait 2 seconds and then automatically launch the interface in your default browser at `http://127.0.0.1:5000`.*
  
- **Ending/Stopping Command:**
  To stop the web application, focus on the terminal running the server and press:
  ```
  Ctrl + C
  ```

### Option B: Local Proctor Test (CLI Utility)
*Launches a standalone window containing the OpenCV webcam feed, testing face/eye/audio tracking algorithms, and printing output directly to the terminal console.*

- **Starting Command:**
  ```powershell
  python backend/main.py
  ```
  
- **Ending/Stopping Command:**
  To close the CV2 camera feed and exit the monitoring loop, focus on the open camera window and press:
  ```
  Esc (Escape key)
  ```
