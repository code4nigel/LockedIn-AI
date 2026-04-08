# Architectural Patterns & Conventions

## 1. Global State Management (Backend)
- The Flask application (`backend/server.py`) uses a global `proctor_state` dictionary to manage real-time session tracking across multiple endpoints (status, violations, syntax/logic errors).
- Thread-safe camera access is implemented using `threading.Lock()` (`camera_lock`) for concurrent video streaming and state updates.

## 2. Video Streaming & Background Processing
- Uses a generator function (`generate_frames`) in Flask to yield MJPEG frames via `Multipart/x-mixed-replace`.
- Audio monitoring runs in a separate background daemon thread using `PyAudio` (`backend/ai_proctor/audio_monitor.py`).

## 3. Database Access Pattern
- SQLite operations in `backend/database.py` follow an open-execute-close pattern per function call rather than maintaining a persistent connection pool. It safely handles schema upgrades with `try/except` blocks handling `sqlite3.OperationalError`.

## 4. Frontend-Backend Communication
- Client polls `/status` periodically instead of using WebSockets.
- Tab-switching is handled via the `visibilitychange` DOM event, reporting violations immediately to the backend via POST requests.
- Code execution isolates user submissions into a `tempfile.TemporaryDirectory` and runs them via `subprocess.run` (`backend/server.py`: `run_code()`).

## 5. Coding & Style Conventions
- **Progressive Enhancement:** UI uses standard HTML/JS with Tailwind for styling; relies heavily on hidden/block class toggling for modal and state management instead of a frontend framework like React.
- **Security:** `werkzeug.security` is used for basic password hashing, but JWTs are not used (relies on Flask sessions).