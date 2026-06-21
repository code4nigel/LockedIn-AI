# LockedIn AI: AI-Powered Adaptive Proctoring & Technical Interview Preparation Platform

**LockedIn AI** is a state-of-the-art educational and assessment platform designed to prepare candidates for high-stakes technical coding assessments and professional developer interviews. By combining a Monaco-based coding sandbox, real-time client-side computer vision (MediaPipe Face Mesh), and audio monitoring with interactive voice-enabled behavioral mock interviewers (Google Gemini API / local Ollama models), LockedIn AI delivers immediate, analytical, and security-centric feedback.

---

## 🚀 Key Capabilities

### 1. Monaco Code Workspace & Isolated Sandbox
*   **Professional IDE**: Implements Microsoft’s Monaco Editor with syntax highlighting, automatic indentation, and code autocompletion.
*   **Local Compilation Sandbox**: Executes Python, Java, and JavaScript code locally in temporary directories (`tempfile.TemporaryDirectory`) using subprocesses.
*   **Safety Constraints**: Enforces a strict $5.0$-second timeout to kill infinite loops and runs processes with `shell=False` to prevent command injection.
*   **Adaptive Difficulty**: Dynamically upgrades exam challenges (Levels 1 to 5) as the user successfully passes test cases.

### 2. Multi-Layered AI Proctoring System
*   **Computer Vision Eye/Gaze Tracker**: Utilizes MediaPipe Face Mesh locally to identify head rotation and eye deviation. Triggers violations if the nose shifts outside the center frame or if the normalized iris-to-eye-corner ratio moves beyond the $[0.35, 0.65]$ threshold.
*   **Audio Monitor**: Runs a background thread capturing real-time microphone buffers via PyAudio, calculating Root Mean Square (RMS) energy. Flags audio violations when speaking or background coaching exceeds threshold limits.
*   **Keystroke Dynamics**: Tracks typing behavior; instantly flags copying and pasting of large code blocks ($>50$ characters) or unnatural keypress speeds ($<10\text{ms}$ intervals).
*   **Window Tab Switching**: Listens to the browser's Page Visibility API and logs violations the moment a user minimizes the window or opens a secondary browser tab.

### 3. Interactive Voice Mock Interview (LLM)
*   **Professional Persona**: Simulates live interview panels with a strictly professional, non-cheerleader interviewer role prompt.
*   **Dual LLM Integration**: Routes queries to Google Gemini 2.5 Flash for high-quality evaluations, or falls back dynamically to local Ollama endpoints (supporting `llama3.2:1b`, `qwen`, or `gemma4:e2b`).
*   **Speech Synthesis & Recognition**: Translates candidate speech to text using the browser's Web Speech API, sends prompts to the LLM, and streams synthesized responses back. Includes natural Microsoft Edge-TTS streaming with a local native `pyttsx3` offline fallback.

### 4. Advanced Analytics & Profiles (Version 3.0)
*   **Profile Customization**: Users can edit usernames, update passwords, and upload custom profile pictures. Avatars are parsed into Base64 strings and stored directly in the SQLite `users` table.
*   **6-Axis Radar Skill Chart**: Renders visual comparisons of user proficiency (Coding, Syntax, Speed, Aptitude, Communication, Integrity) against a standard Benchmark target.
*   **Performance Line Graph**: Generates a cumulative time-series line chart (Level vs. Time) in the session details modal, showing precisely where candidates spent the most time compared to average benchmarks.
*   **Local LLM Automation**: Programmatically spawns `ollama serve` on session start and terminates the background process on exit, saving system CPU and memory resources.

---

## 🛠️ Tech Stack

*   **Frontend**: Vanilla HTML5, CSS3, Tailwind CSS, Monaco Editor API, Chart.js.
*   **Backend**: Python 3.10+, Flask, SQLite.
*   **AI/CV/Processing**: MediaPipe Face Mesh, OpenCV, NumPy, PyAudio, Edge-TTS, pyttsx3.
*   **APIs**: Google GenAI SDK, local Ollama API (`/api/chat`).

---

## 📊 Database Relational Schema

LockedIn AI uses a local SQLite database (`lockedin.db`) structured with three relational tables:

```mermaid
erDiagram
    users {
        int id PK
        string username UNIQUE
        string password
        int total_points
        string rank
        string avatar
    }
    sessions {
        int id PK
        int user_id FK
        int max_level
        int violations
        int syntax_errors
        int logic_errors
        string timestamp
        string violation_logs
        string level_times
        string categories_completed
        int aptitude_score
        string behavioral_feedback
    }
    aptitude_questions {
        int id PK
        string question
        string option_a
        string option_b
        string option_c
        string option_d
        string correct_answer
        string category
    }

    users ||--o{ sessions : "attempts"
```

### Table Definitions
1.  **`users`**: Manages accounts, credentials, cumulative experience points (XP), ranks, and Base64 avatar images.
2.  **`sessions`**: Logs historical test results, proctor flags, syntax/logic errors, elapsed time distributions, MCQ scores, and behavioral feedback summaries.
3.  **`aptitude_questions`**: Houses multiple-choice CS aptitude questions divided by subjects (e.g. OS, Algorithms).

---

## ⚙️ Setup & Run Instructions

### 1. Prerequisites
Ensure you have Python 3.10+ installed and a webcam/microphone connected to your local machine.

### 2. Environment Configuration
Create a `.env` file in the root folder and add your credentials:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 3. Installation
Activate your virtual environment and install the required dependencies:
```powershell
# Activate Virtual Environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install Pinned Package Dependencies
pip install -r requirements.txt
```

### 4. Running the Web Application
Start the backend server, which automatically initializes the database, validates dependencies, and launches the web interface:
```powershell
python backend/server.py
```
Open your web browser and navigate to `http://127.0.0.1:5000`.

### 5. Running local Proctor Test (CLI Utility)
To test face mesh tracking, eye gaze vectors, and noise detection filters in a standalone OpenCV test frame:
```powershell
python backend/main.py
```
*Press the `Esc` key on the OpenCV camera window to close the utility.*
