# LockedIn AI - Viva Preparation Cheat Sheet

**Graduation Project Viva Q&A Guide**  
**Institution:** Lakshmi Narain College of Technology Excellence  
**Presenters:** Shivanshu Yadav & Uday Singh Prajapati  
**Subject:** Major Project Viva-Voce Examination  

---

## Part 1: Basic Concept Questions

### Q1: What is the primary purpose of the LockedIn AI project?
*   **Answer:** LockedIn AI is an automated, AI-powered educational testing and interview preparation platform. It combines real-time webcam and microphone proctoring with coding challenges, multiple-choice aptitude tests, and interactive AI-driven verbal mock interviews to help users prepare for software engineering recruitment processes.

### Q2: What is the tech stack used to build the platform?
*   **Answer:**
    *   **Frontend:** Vanilla HTML5, CSS3, TailwindCSS, Monaco Code Editor, and Chart.js.
    *   **Backend:** Python 3.10+, Flask, SQLite.
    *   **AI/ML/CV:** OpenCV, MediaPipe Face Mesh, PyAudio, NumPy, and Google Gemini API (with local Ollama integration for fallback).

### Q3: What is the Monaco Editor, and why did you choose it?
*   **Answer:** Monaco Editor is the web-based code editor that powers VS Code. We chose it because it provides an industry-standard, professional IDE experience out-of-the-box, featuring syntax highlighting, automatic indentation, code auto-completion, and multi-cursor support.

### Q4: Which database engine is used in this project?
*   **Answer:** We use SQLite (`lockedin.db`), a serverless, zero-configuration relational database. It is highly portable and fast for local single-user preparation setups.

### Q5: How is user registration and authentication handled?
*   **Answer:** Users register via the `/register` endpoint and log in via the `/login` endpoint. Passwords are hashed using the PBKDF2 algorithm with SHA-256 via Flask's `werkzeug.security` before being saved to the database.

### Q6: What does the browser's JavaScript Visibility API do?
*   **Answer:** It monitors whether the browser tab is active. We use the `visibilitychange` event listener. If the user switches tabs or minimizes the window, the frontend immediately posts a "TAB SWITCHED" violation to the Flask backend.

### Q7: What is the role of `pyaudio` in your project?
*   **Answer:** It captures real-time microphone audio from the user's system so the backend can analyze ambient noise levels and flag speaking violations during assessments.

### Q8: What library is utilized for facial landmark detection, and how many points does it track?
*   **Answer:** We use Google's MediaPipe Face Mesh library, which tracks 468 (or 478 refined) 3D coordinate points on the human face in real-time.

### Q9: How is the skill dashboard radar chart rendered?
*   **Answer:** It is rendered on an HTML5 canvas element using Chart.js. It pulls completed category data from the SQLite database to display the user's proficiency across various algorithmic topics.

### Q10: How are points and user ranks calculated?
*   **Answer:** When a session is saved, points are calculated using the following formula:
    $$\text{Points} = (\text{Max Level} \times 100) - (\text{Violations} \times 10) + (\text{Aptitude Score} \times 10)$$
    These points are added to the user's profile, and their rank is updated based on defined thresholds (e.g. reaching $>500$ points upgrades the user to "Syntax Soldier").

---

## Part 2: Intermediate Technical Questions

### Q11: Explain the mathematical calculation used for iris-gaze tracking.
*   **Answer:** We capture the horizontal coordinates of the iris center, inner eye corner, and outer eye corner. We normalize the iris position between 0 and 1:
    $$\text{Ratio} = \frac{\text{Iris.x} - \min(\text{Inner.x}, \text{Outer.x})}{|\text{Outer.x} - \text{Inner.x}|}$$
    A ratio between `0.35` and `0.65` indicates a centered gaze; values outside this range flag a "LOOK AWAY" violation.

### Q12: How does the code execution sandbox work on the backend?
*   **Answer:** The backend creates a directory via `tempfile.TemporaryDirectory()`, writes the user code and assertions into it, and runs the script using `subprocess.run()`. This isolates the execution from the rest of the workspace.

### Q13: How are syntax errors distinguished from logic errors during code execution?
*   **Answer:** If the subprocess execution returns a non-zero exit code, we inspect `stderr`. If terms like "SyntaxError" or compilation errors are found, we increment `syntax_errors`. Otherwise, it is counted as a `logic_error` (failed test cases).

### Q14: What is a Thread Lock, and why is it used on the `/video_feed` endpoint?
*   **Answer:** Since OpenCV camera instances are not inherently thread-safe, concurrent HTTP requests can cause crashes. We use `threading.Lock()` to ensure only one process thread accesses the webcam feed at a time.

### Q15: How does the AI model fallback mechanism function?
*   **Answer:** The application checks for an active Gemini API key in `.env`. If unavailable or rate-limited, it sends requests to a local Ollama instance (`http://localhost:11434`), falling back to models like `llama3.2:1b` or `gemma4:e2b`.

### Q16: What is the RMS of an audio signal, and how is it used here?
*   **Answer:** Root Mean Square (RMS) measures the average energy of the audio signal. In `audio_monitor.py`, we calculate the RMS of 1024-byte sample buffers. If the RMS exceeds $150$, we log a voice violation.

### Q17: How does the adaptive difficulty system work?
*   **Answer:** The database contains coding questions ranked by difficulty (Levels 1 to 5). When a user successfully compiles a solution and passes the tests, the session's difficulty level increments and the next level question is loaded.

### Q18: What security measures prevent infinite loops in user submissions?
*   **Answer:** The subprocess execution is wrapped in `subprocess.run(..., timeout=5.0)`. If the code runs longer than 5 seconds, a `TimeoutExpired` exception is caught, terminating the process and returning a timeout error to the client.

### Q19: Explain how the voice-to-voice interview is structured in the browser.
*   **Answer:** The browser's Web Speech API converts user speech to text, which is sent to Flask. The backend prompts Gemini/Ollama, returns the text response, and the browser's speech synthesis engine reads the response back to the user.

### Q20: How is the overall Integrity Score calculated?
*   **Answer:** The system converts violations into a cheat score:
    $$\text{Cheat Score} = (1 \times \text{eyes\_away\_sec}) + (2 \times \text{audio\_spikes}) + (5 \times \text{multiple\_faces\_sec})$$
    The integrity score is computed as $100 - \text{Cheat Score}$, capped at a minimum of 0.

---

## Part 3: Advanced Architecture Questions

### Q21: Why does the system use a generator function with the `multipart/x-mixed-replace` MIME type?
*   **Answer:** This MIME type allows the server to push a continuous stream of individual JPEG images over a single HTTP connection. The browser renders each incoming image sequentially, displaying a live webcam stream without requiring WebSocket setup.

### Q22: What is the risk of utilizing `shell=True` in `subprocess.run()`, and how does this application prevent it?
*   **Answer:** Setting `shell=True` runs the command through the shell interpreter, making it vulnerable to shell injection (e.g., executing system commands via operators like `;` or `&&`). The application sets `shell=False` and passes command arguments as an isolated list.

### Q23: How are database updates handled when a user registers with an existing username?
*   **Answer:** The `users` table defines `username` as `UNIQUE`. If a registration request uses an existing name, SQLite raises an `IntegrityError`. The code catches this error and returns `success=False` with an appropriate message to the client.

### Q24: Describe the database schema migrations implemented in `database.py`.
*   **Answer:** Rather than dropping and recreation, schema upgrades (like adding `violation_logs` or `aptitude_score`) use `ALTER TABLE` commands wrapped in `try/except` blocks. This prevents data loss when updating existing schemas.

### Q25: Why was a lightweight 1B model (like Llama-3.2-1b) selected as the preferred local AI fallback model?
*   **Answer:** Larger LLMs (e.g., 7B models) require dedicated GPU memory and run slowly on standard CPUs. A 1B model runs efficiently on CPU-only machines with low RAM, keeping response latency reasonable during offline preparation.

### Q26: Explain how keystroke dynamics help detect cheating.
*   **Answer:** Real human typing has natural intervals between keystrokes. If a large block of text ($>50$ characters) is pasted, or keyup/keydown events fire with delays $<10\text{ms}$, it indicates external pasting or script injection, which is caught and flagged as a violation.

### Q27: How does the system handle database session connections in a multi-threaded Flask environment?
*   **Answer:** To avoid thread conflicts, the application opens a new database connection for each function call and closes it immediately after the operation is complete.

### Q28: If MediaPipe detects multiple faces in a frame, how is this penalized, and why?
*   **Answer:** Multiple faces in the frame indicate a potential collaborator helper. This is considered a high-risk violation and is penalized heavily ($5$ points per second) compared to look-away events ($1$ point per second).

### Q29: How are user experience points (XP) and rank progression managed?
*   **Answer:** When a session is saved, points are calculated as:
    $$\text{Points} = (\text{Max Level} \times 100) - (\text{Violations} \times 10) + (\text{Aptitude Score} \times 10)$$
    The user's total points are updated, and their rank is adjusted based on defined thresholds (e.g., reaching $>10,000$ points upgrades the user to '7-Star Architect').

### Q30: What is the difference between Google Gemini 2.0 Flash and 2.5 Flash in our backend design?
*   **Answer:** Gemini 2.5 Flash offers improved context handling, lower latency, and higher rate limits, which helps prevent rate-limit errors during long interactive mock interview sessions.

---

## Part 4: Trick Questions & Project Edge Cases

### Q31: Does our proctoring engine prevent cheating if a user connects a secondary physical monitor to their laptop?
*   **Answer:** No, local browser APIs cannot detect external display connections. However, if the user turns their head or redirects their gaze to look at the secondary monitor, the MediaPipe gaze tracking module will flag the eye deviation as a violation.

### Q32: What happens if a user submits a Python script containing a syntax error? Does the backend crash?
*   **Answer:** No. The code runs inside a try-except block, and the subprocess captures the compilation failure in `stderr`. The backend returns the traceback output to the frontend and increments the syntax error count without crashing the server.

### Q33: Since the webcam uses OpenCV's `cv2.VideoCapture(0)`, what happens if two users log into the application simultaneously from different computers?
*   **Answer:** The application is configured to run on `localhost` (single-user preparation). In a multi-user deployment, OpenCV would attempt to open camera index `0` *on the server hosting the Flask application* rather than the client's machine, failing because the browser cannot access client hardware via server-side OpenCV. (Note: Resolving this would require migrating the video stream capture to frontend WebRTC, which is noted in the future roadmap).

---

## Part 5: Version 3.0 Platform Updates (Profile, Advanced Analytics & Local AI Stability)

### Q34: What are the key improvements in the Version 3.0 release of LockedIn AI?
*   **Answer:** Version 3.0 focuses on personalization, advanced analytics, and system stability:
    1. **Profile Customization**: Users can now update usernames, passwords, and upload custom avatars.
    2. **6-Axis Radar Skill Chart**: Re-engineered to map exact mastery on 6 specific dimensions (Coding, Syntax, Speed, Aptitude, Communication, and Integrity).
    3. **Continuous Performance Line Graph**: Generates a cumulative time-series line graph of level completion time compared against average developer benchmarks.
    4. **Local LLM Automation**: Programmatic management of the local Ollama backend process to start/stop the service dynamically on-demand, saving system resources.
    5. **Edge-TTS / Local pyttsx3 Audio Routing**: A high-quality `/speak` endpoint with modern text-to-speech fallback mechanisms.

### Q35: How is user profile persistence and custom avatars handled?
*   **Answer:** Profile updates are processed via the `/update_profile` POST route. If the user uploads a custom avatar, the image is parsed client-side using JavaScript `FileReader` into a Base64-encoded string, which is transmitted to the server and stored in the database's new `avatar` column inside the `users` table. This provides robust file persistence without the complexity of an external file storage system.

### Q36: Explain the difference between the 6-axis Radar chart and the cumulative Performance Line Graph.
*   **Answer:** 
    *   **6-Axis Radar Chart**: Compares the candidate's holistic skills (Coding, Syntax, Speed, Aptitude, Communication, and Integrity) against a standard benchmark target, helping the candidate identify their overall strengths and weaknesses at a glance.
    *   **Cumulative Performance Line Graph**: Tracks a time-series progress of level completion (Level vs. Cumulative Elapsed Time) compared against the benchmark (e.g. 1.8 mins/level) to highlight speed, stamina, and where the most time was spent during the session.

### Q37: How did you resolve the AMD/UMD loader conflict between Monaco Editor and Chart.js?
*   **Answer:** Monaco Editor's loader (`loader.min.js`) uses an AMD module loader (`window.define`), which hijacks standard UMD libraries like Chart.js if loaded afterward, registering Chart.js anonymously rather than globally on `window.Chart`. We resolved this by reordering script tags in `index.html` to load `chart.js` *before* Monaco's loader. Since `window.define` is not yet present, Chart.js registers globally, and Monaco loads successfully without conflicts.

### Q38: How does the platform start/stop Ollama programmatically on demand?
*   **Answer:** When the user switches to a local model and launches a session (e.g. `/start_test`, `/ai_interview`), the backend queries `http://localhost:11434/`. If the local service is unresponsive, it spawns `ollama serve` in the background as a subprocess (`subprocess.Popen`). On session completion (`/stop_test` or server exit via `atexit`), the backend sends a terminate signal to stop the background Ollama server process, freeing up CPU and memory resource bounds.

### Q39: What is the speech synthesis architecture in the interview mock, and how is offline/online handled?
*   **Answer:** Speech synthesis is managed by the `/speak` endpoint. When online, the backend streams high-quality natural voice audio from Microsoft's Edge-TTS service. If the server is offline or Edge-TTS fails, it falls back to the native system text-to-speech engine (`pyttsx3`) to synthesize speech locally, ensuring high-fidelity voice-guided interviews under all conditions.

