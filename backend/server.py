from flask import Flask, render_template, Response, request, jsonify, session, send_from_directory, send_file, after_this_request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from google import genai
from dotenv import load_dotenv
import cv2
import sys
import os
# Suppress C++ backend logging (MediaPipe/TFLite/TensorFlow)
os.environ['GLOG_minloglevel'] = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import threading
import time
import webbrowser
import subprocess
import tempfile
import json
from datetime import datetime
import asyncio
import edge_tts
import pyttsx3
import atexit

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Force reload environment to catch .env changes
load_dotenv(override=True)
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

GEMINI_MODEL_ID = 'gemini-2.5-flash' # Changed from 2.0-flash to fix rate limit errors

_last_loaded_key = None
client = None

def get_gemini_client():
    global client, _last_loaded_key
    load_dotenv(override=True)
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key:
        if _last_loaded_key != key or not client:
            print(f"DEBUG: Initializing/Reloading Gemini client with key (first 4 chars: {key[:4]}...)")
            client = genai.Client(api_key=key)
            _last_loaded_key = key
        return client
    else:
        client = None
        _last_loaded_key = None
        return None

# Initial load check
get_gemini_client()

import requests

def get_local_ollama_model():
    try:
        res = requests.get("http://localhost:11434/api/tags", timeout=2)
        if res.status_code == 200:
            data = res.json()
            models = data.get("models", [])
            if models:
                names = [m.get("name") for m in models if m.get("name")]
                # Prioritize lightweight models for CPU execution
                for name in names:
                    if "llama3.2" in name or "llama3.2:1b" in name or ":1b" in name:
                        return name
                for name in names:
                    if "qwen" in name and ("0.5b" in name or "1.5b" in name or "1.5" in name):
                        return name
                # Next, fallback to heavier models like your gemma4
                for name in names:
                    if "gemma4:e2b" in name:
                        return name
                for name in names:
                    if "gemma" in name:
                        return name
                return names[0]
    except Exception:
        pass
    return "gemma4:e2b"  # Default fallback guess

ollama_process = None

def ensure_ollama_running():
    global ollama_process
    try:
        res = requests.get("http://localhost:11434/", timeout=0.5)
        if res.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    
    try:
        print("INFO: Ollama not running. Attempting to start 'ollama serve' programmatically...")
        ollama_process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        for _ in range(5):
            time.sleep(1.0)
            try:
                res = requests.get("http://localhost:11434/", timeout=0.5)
                if res.status_code == 200:
                    print("INFO: Ollama successfully started programmatically.")
                    return True
            except requests.exceptions.RequestException:
                pass
    except Exception as e:
        print(f"ERROR: Failed to launch Ollama programmatically: {e}")
    return False

def stop_ollama_if_started():
    global ollama_process
    if ollama_process:
        print("INFO: Stopping programmatic Ollama server instance...")
        try:
            ollama_process.terminate()
            ollama_process.wait(timeout=2.0)
        except Exception:
            try:
                ollama_process.kill()
            except Exception:
                pass
        ollama_process = None

atexit.register(stop_ollama_if_started)

def generate_local_ai_response(system_prompt, messages_history, format_json=False):
    """
    Calls local Ollama API to generate a response.
    messages_history should be a list of dicts: [{'role': 'user'/'model', 'content': '...'}]
    """
    if not ensure_ollama_running():
        return "Error contacting local Ollama service: Failed to start or connect to Ollama background service."
        
    model = get_local_ollama_model()
    url = "http://localhost:11434/api/chat"
    
    # Map roles from Gemini standard ('model') to Ollama standard ('assistant')
    ollama_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages_history:
        role = "assistant" if msg.get("role") == "model" or msg.get("role") == "assistant" else "user"
        ollama_messages.append({"role": role, "content": msg.get("content") or msg.get("text", "")})
        
    payload = {
        "model": model,
        "messages": ollama_messages,
        "stream": False
    }
    if format_json:
        payload["format"] = "json"
    
    try:
        # Increased timeout to 180s to allow heavy models to load and run on slower CPUs
        response = requests.post(url, json=payload, timeout=180)
        if response.status_code == 200:
            res_json = response.json()
            return res_json.get("message", {}).get("content", "")
        else:
            print(f"[OLLAMA ERROR] URL: {url}, Payload: {payload}, Status: {response.status_code}, Response: {response.text}")
            return f"Error: Ollama returned status code {response.status_code} ({response.text.strip()})"
    except Exception as e:
        return f"Error contacting local Ollama service: {str(e)}. Make sure Ollama is running and model {model} is loaded."

from backend.ai_proctor.tracker import FaceTracker
from backend.ai_proctor.audio_monitor import AudioMonitor
from backend.ai_proctor.questions import get_question_by_difficulty, get_question_by_id
from backend.database import init_db, save_session, get_profile, create_user, get_user_by_username, get_random_aptitude_questions, check_aptitude_answers

app = Flask(__name__, template_folder=os.path.join(project_root, 'frontend'), static_folder=os.path.join(project_root, 'frontend'))
app.secret_key = 'super_secret_lockedin_key'
CORS(app)

init_db()

proctor_state = {
    "is_active": False, "status": "SECURE", "violations": 0, "current_difficulty": 1,
    "audio_enabled": False, "syntax_errors": 0, "logic_errors": 0, "violation_logs": [],
    "level_times": [], "last_level_time": None
}

camera = None
camera_lock = threading.Lock()
tracker = FaceTracker()
audio_tracker = AudioMonitor(threshold=150) 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

@app.route('/chart.js')
def chart_js():
    return send_from_directory(app.static_folder, 'chart.js')

# --- AUTHENTICATION ROUTES ---
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Missing credentials"})
        
    hashed = generate_password_hash(password)
    if create_user(username, hashed):
        user = get_user_by_username(username)
        session['user_id'] = user['id']
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Username already exists"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = get_user_by_username(username)
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid credentials"})

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"success": True})

@app.route('/check_auth')
def check_auth():
    if 'user_id' in session:
        return jsonify({"authenticated": True})
    return jsonify({"authenticated": False})
# -----------------------------

def log_incident(reason):
    timestamp = datetime.now().strftime("%I:%M:%S %p")
    proctor_state["violation_logs"].append({"time": timestamp, "type": reason})

def generate_frames():
    global camera, proctor_state
    while True:
        if not proctor_state["is_active"]: break
        with camera_lock:
            if camera is None or not camera.isOpened():
                time.sleep(0.1)
                continue
            success, frame = camera.read()
        if not success: continue
        
        try:
            face_count, looking_away = tracker.process_frame(frame)
            current_status = "SECURE"
            
            if "TAB SWITCHED" in proctor_state["status"]:
                current_status = proctor_state["status"]
                color = (0, 0, 255)
            elif face_count != 1 or looking_away:
                current_status = "VIOLATION (LOOK AWAY)"
                color = (0, 0, 255)
            elif proctor_state["audio_enabled"] and audio_tracker.audio_violation:
                current_status = "VIOLATION (AUDIO DETECTED)"
                color = (0, 165, 255) 
            else:
                current_status = "SECURE"
                color = (0, 255, 0)
                
            if current_status != "SECURE" and proctor_state["status"] == "SECURE":
                proctor_state["violations"] += 1
                reason = current_status.replace("VIOLATION (", "").replace(")", "")
                log_incident(reason)
                
            proctor_state["status"] = current_status
            cv2.putText(frame, f"AI: {proctor_state['status']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret: continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception: continue

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_profile_data')
def get_profile_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify(get_profile(user_id))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Not authenticated"}), 401
    
    data = request.json
    username = data.get('username').strip()
    avatar = data.get('avatar')
    new_password = data.get('password')
    
    if not username:
        return jsonify({"success": False, "message": "Username is required"})
        
    import sqlite3
    from backend.database import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if username is taken by another user
    cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (username, user_id))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return jsonify({"success": False, "message": "Username already taken"})
        
    # Update username and avatar
    cursor.execute("UPDATE users SET username = ?, avatar = ? WHERE id = ?", (username, avatar, user_id))
    
    # Update password if provided
    if new_password:
        hashed = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
        
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/get_current_question')
def get_current_question():
    q = get_question_by_difficulty(proctor_state["current_difficulty"], 0)
    return jsonify(q)

@app.route('/start_test', methods=['POST'])
def start_test():
    global camera, proctor_state
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
        
    settings = request.json or {}
    with camera_lock:
        if not proctor_state["is_active"]:
            camera = cv2.VideoCapture(0)
            time.sleep(0.5)
            
            # Initialize tracking and specific timestamps
            proctor_state.update({
                "is_active": True, "audio_enabled": settings.get('audio', False),
                "violations": 0, "syntax_errors": 0, "logic_errors": 0,
                "current_difficulty": 1, "status": "SECURE", "violation_logs": [],
                "level_times": [], "last_level_time": time.time(),
                "categories_completed": [],
                "aptitude_score": None, "behavioral_feedback": None
            })
            if proctor_state["audio_enabled"]: audio_tracker.start()
    return jsonify({"status": "started"})

@app.route('/stop_test')
def stop_test():
    global camera, proctor_state
    user_id = session.get('user_id')
    
    if proctor_state["is_active"] and user_id:
        # Save specific logs and tracked times for the graphs
        v_logs = json.dumps(proctor_state.get("violation_logs", []))
        l_times = json.dumps(proctor_state.get("level_times", []))
        cats = json.dumps(proctor_state.get("categories_completed", []))
        apt_score = proctor_state.get("aptitude_score")
        beh_feedback = proctor_state.get("behavioral_feedback")
        
        save_session(user_id, proctor_state["current_difficulty"], proctor_state["violations"], 
                     proctor_state["syntax_errors"], proctor_state["logic_errors"], v_logs, l_times, cats, apt_score, beh_feedback)
                     
    proctor_state["is_active"] = False
    if audio_tracker: audio_tracker.stop()
    stop_ollama_if_started()
    with camera_lock:
        if camera: camera.release(); camera = None
    return jsonify({"status": "stopped"})

@app.route('/status')
def get_status(): return jsonify(proctor_state)

@app.route('/log_violation', methods=['POST'])
def log_violation():
    global proctor_state
    data = request.json
    reason = data.get("reason", "TAB SWITCHED")
    if proctor_state["is_active"]:
        proctor_state["violations"] += 1
        log_incident(reason)
        proctor_state["status"] = f"VIOLATION ({reason})"
    return jsonify({"status": "logged"})

@app.route('/clear_violation', methods=['POST'])
def clear_violation():
    global proctor_state
    if proctor_state["is_active"] and "TAB SWITCHED" in proctor_state["status"]:
        proctor_state["status"] = "SECURE"
    return jsonify({"status": "cleared"})

@app.route('/run_code', methods=['POST'])
def run_code():
    data = request.json
    code, lang, q_id = data.get('code', ''), data.get('language', 'python'), data.get('question_id')
    question = get_question_by_id(q_id)
    if not question: return jsonify({"stdout": "Question not found", "status": {"id": 6}})
    
    output_text, is_error = "", False
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            if lang == "python":
                full_code = code + "\n" + question["python_test"]
                f_path = os.path.join(temp_dir, "solution.py")
                with open(f_path, "w", encoding="utf-8") as f: f.write(full_code)
                res = subprocess.run([sys.executable, f_path], text=True, capture_output=True, timeout=5)
                if res.returncode != 0:
                    is_error = True
                    output_text = res.stderr
                    if "SyntaxError" in res.stderr or "IndentationError" in res.stderr: proctor_state["syntax_errors"] += 1
                    else: proctor_state["logic_errors"] += 1
                else: output_text = res.stdout
            
            elif lang == "java":
                full_code = code + "\n" + question["java_test"]
                f_path = os.path.join(temp_dir, "Main.java")
                with open(f_path, "w", encoding="utf-8") as f: f.write(full_code)
                # Compile
                compile_res = subprocess.run(["javac", f_path], text=True, capture_output=True, timeout=10)
                if compile_res.returncode != 0:
                    is_error = True
                    output_text = compile_res.stderr
                    proctor_state["syntax_errors"] += 1
                else:
                    # Run
                    run_res = subprocess.run(["java", "-cp", temp_dir, "Main"], text=True, capture_output=True, timeout=5)
                    if run_res.returncode != 0:
                        is_error = True
                        output_text = run_res.stderr
                        proctor_state["logic_errors"] += 1
                    else:
                        output_text = run_res.stdout

            elif lang == "javascript":
                full_code = code + "\n" + question.get("js_test", "")
                f_path = os.path.join(temp_dir, "solution.js")
                with open(f_path, "w", encoding="utf-8") as f: f.write(full_code)
                res = subprocess.run(["node", f_path], text=True, capture_output=True, timeout=5)
                if res.returncode != 0:
                    is_error = True
                    output_text = res.stderr
                    # Basic syntax vs logic error detection for JS
                    if "SyntaxError" in res.stderr: proctor_state["syntax_errors"] += 1
                    else: proctor_state["logic_errors"] += 1
                else: output_text = res.stdout
        
        success = not is_error and "ALL TESTS PASSED" in output_text
        if success: 
            # Track category
            cat = question.get("category", "General")
            if "categories_completed" not in proctor_state: proctor_state["categories_completed"] = []
            if cat not in proctor_state["categories_completed"]:
                proctor_state["categories_completed"].append(cat)

            # Track real time taken for this question for the Graph
            current_time = time.time()
            time_taken = current_time - proctor_state.get("last_level_time", current_time)
            
            if "level_times" not in proctor_state: proctor_state["level_times"] = []
            proctor_state["level_times"].append(round(time_taken / 60.0, 2)) # Save in minutes
            proctor_state["last_level_time"] = current_time
            proctor_state["current_difficulty"] = min(10, proctor_state["current_difficulty"] + 1)
            
        return jsonify({"stdout": output_text, "status": {"id": 3 if success else 11, "description": "Accepted" if success else "Test Failed"}})
    except Exception as e: return jsonify({"stdout": f"Server Error: {str(e)}", "status": {"id": 6}})

@app.route('/ai_interview', methods=['POST'])
def ai_interview():
    data = request.json
    code = data.get('code')
    question_id = data.get('question_id')
    language = data.get('language')
    history = data.get('history', [])
    model_pref = data.get('model_preference', 'gemini')
    
    question = get_question_by_id(question_id)
    if not question:
        return jsonify({"error": "Question not found"}), 404
    
    # Simple prompt for initial feedback
    if not history:
        prompt = f"""
        You are an expert technical interviewer. The candidate has just solved the following coding challenge:
        Title: {question['title']}
        Description: {question['description']}
        
        Candidate's Solution ({language}):
        ```
        {code}
        ```
        
        Instructions:
        1. Briefly analyze their code's performance (time/space complexity).
        2. Provide one constructive tip.
        3. Ask exactly ONE deep follow-up question about their implementation or a theoretical alternative.
        4. Keep your response concise, professional, and within 3-4 sentences.
        """
    else:
        prompt = history[-1]['content']
    
    # Try Gemini first if user selected it and client is configured
    gemini_client = get_gemini_client()
    if model_pref == 'gemini' and gemini_client:
        try:
            # Convert history format for new SDK
            gemini_history = []
            for msg in history[:-1]:
                role = "user" if msg['role'] == "user" else "model"
                gemini_history.append({"role": role, "parts": [{"text": msg['content']}]})
                
            chat = gemini_client.chats.create(model=GEMINI_MODEL_ID, history=gemini_history)
            response = chat.send_message(prompt)
            return jsonify({"response": response.text})
        except Exception as e:
            print(f"Gemini error in /ai_interview: {str(e)}. Falling back to local Ollama.")
            
    # Fallback to Local Ollama
    system_prompt = """
# ROLE
You are Sarah Mitchell, a professional Technical Interviewer with 15+ years of experience hiring software engineers.
Your job is NOT to be a friend, coach, cheerleader, or teacher.
Your job is to accurately assess a candidate's code.
Maintain a professional, polite, neutral, and analytical interview atmosphere. Do not use emojis, over-praise, or use casual language.
"""
    if not history:
        messages = [{"role": "user", "content": prompt}]
    else:
        # History contains role/content dicts
        messages = history
        
    local_response = generate_local_ai_response(system_prompt, messages)
    if "Error contacting local Ollama service" in local_response:
        return jsonify({"error": local_response}), 500
    return jsonify({"response": local_response})

@app.route('/get_aptitude_questions')
def api_get_aptitude_questions():
    questions = get_random_aptitude_questions(10)
    return jsonify(questions)

@app.route('/submit_aptitude', methods=['POST'])
def submit_aptitude():
    data = request.json
    detailed_results = check_aptitude_answers(data.get('answers', {}))
    proctor_state['aptitude_score'] = detailed_results['score']
    return jsonify(detailed_results)

@app.route('/verbal_chat', methods=['POST'])
def verbal_chat():
    data = request.json
    history = data.get('history', [])
    prompt = data.get('prompt')
    model_pref = data.get('model_preference', 'gemini')
    
    system_instruction = """
# ROLE
You are Sarah Mitchell, a professional Technical Interviewer with 15+ years of experience hiring software engineers.
Your job is NOT to be a friend, coach, cheerleader, or teacher.
Your job is to accurately assess a candidate's employability, technical competence, communication ability, and professional readiness.

# INTERVIEW START RULES
When the interview begins (no history):
- Introduce yourself: "Good morning. My name is Sarah Mitchell, and I'll be conducting your interview today."
- Ask the candidate to introduce themselves: "Let's begin with a brief introduction about yourself. Please tell me about your background, education, projects, experience, and career goals."

# INTERVIEW STYLE
- Maintain a professional, polite, neutral, and analytical interview atmosphere.
- Do NOT be a friend, mentor, or motivational speaker.
- Do NOT use excessive encouragement or emojis.
- Do NOT use casual language.
- Ask only ONE question at a time.
- Continuously adapt the difficulty: ask more challenging questions (architecture, tradeoffs, system design) to strong candidates, and foundational questions to weaker candidates.

# FEEDBACK AND QUESTION FLOW
- For every candidate response, briefly evaluate the answer professionally (1-2 sentences of direct feedback pointing out what was good or what was missing).
- Then, immediately ask the next question.
- Keep your total response under 4-5 sentences so it is concise and suitable for Text-to-Speech playback.
"""
    
    # Try Gemini first if user selected it and client is configured
    gemini_client = get_gemini_client()
    if model_pref == 'gemini' and gemini_client:
        try:
            full_prompt = prompt
            if not history:
                full_prompt = system_instruction + f"\n\nThe candidate is ready. Introduce yourself briefly and ask your first challenging question. The candidate said: {prompt}"
                
            # Convert history format for new SDK
            gemini_history = []
            for msg in history:
                role = "user" if msg['role'] == "user" else "model"
                gemini_history.append({"role": role, "parts": [{"text": msg['content']}]})
                
            chat = gemini_client.chats.create(model=GEMINI_MODEL_ID, history=gemini_history)
            response = chat.send_message(full_prompt)
            
            proctor_state["behavioral_feedback"] = "Completed verbal interview."
            return jsonify({"response": response.text})
        except Exception as e:
            print(f"Gemini error in /verbal_chat: {str(e)}. Falling back to local Ollama.")
            
    # Fallback to Local Ollama
    messages = []
    if not history:
        first_input = f"Introduce yourself briefly and ask your first challenging question. The candidate said: {prompt}"
        messages.append({"role": "user", "content": first_input})
    else:
        for msg in history:
            messages.append(msg)
        messages.append({"role": "user", "content": prompt})
        
    local_response = generate_local_ai_response(system_instruction, messages)
    if "Error contacting local Ollama service" in local_response:
        return jsonify({"error": local_response}), 500
        
    proctor_state["behavioral_feedback"] = "Completed verbal interview."
    return jsonify({"response": local_response})

@app.route('/verbal_report', methods=['POST'])
def verbal_report():
    data = request.json
    history = data.get('history', [])
    model_pref = data.get('model_preference', 'gemini')
    
    if not history:
        return jsonify({"score": 0, "summary": "No questions answered.", "questions": []})
        
    prompt = """
    The interview has concluded. Review the transcript of the interview (provided in the history) and generate a JSON report with the following structure:
    {
        "score": <0-100 overall score>,
        "summary": "<A short paragraph summarizing what the candidate did well and what they must focus on before their real interview.>",
        "questions": [
            {
                "q": "<The question you asked>",
                "a": "<The candidate's answer>",
                "feedback": "<Specific feedback on their answer>",
                "negative_marks": <Integer representing points lost for poor answers (0 if good, 1-10 if bad)>
            }
        ]
    }
    ONLY return the raw JSON object, no markdown blocks.
    """
    
    # Try Gemini first if user selected it and client is configured
    gemini_client = get_gemini_client()
    if model_pref == 'gemini' and gemini_client:
        try:
            # Convert history format for new SDK
            gemini_history = []
            for msg in history:
                role = "user" if msg['role'] == "user" else "model"
                gemini_history.append({"role": role, "parts": [{"text": msg['content']}]})
                
            chat = gemini_client.chats.create(model=GEMINI_MODEL_ID, history=gemini_history)
            response = chat.send_message(prompt)
            
            # Clean up possible markdown block from LLM
            response_text = response.text.replace('```json', '').replace('```', '').strip()
            report = json.loads(response_text)
            
            # Save to DB
            proctor_state["behavioral_feedback"] = report.get('summary', 'Interview completed.')
            proctor_state["aptitude_score"] = report.get('score', 0) // 10  # Scale 100 to 10
            
            return jsonify(report)
        except Exception as e:
            print(f"Gemini error in /verbal_report: {str(e)}. Falling back to local Ollama.")
            
    # Fallback to Local Ollama
    system_prompt = "You are a report generator. Extract interview analysis in clean JSON format."
    messages = []
    for msg in history:
        messages.append(msg)
    messages.append({"role": "user", "content": prompt})
    
    local_response = generate_local_ai_response(system_prompt, messages, format_json=True)
    if "Error contacting local Ollama service" in local_response:
        return jsonify({"error": local_response}), 500
        
    try:
        # Clean up possible markdown wrappers if Ollama model returns them despite JSON format setting
        response_text = local_response.replace('```json', '').replace('```', '').strip()
        report = json.loads(response_text)
        
        proctor_state["behavioral_feedback"] = report.get('summary', 'Interview completed.')
        proctor_state["aptitude_score"] = report.get('score', 0) // 10  # Scale 100 to 10
        
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": f"Failed to parse Ollama JSON report: {str(e)}. Output was: {local_response}"}), 500

def synthesize_text(text, base_filepath):
    # Try Edge-TTS first (free, high quality neural voice)
    try:
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(communicate.save(base_filepath))
            loop.close()
        except Exception:
            asyncio.run(communicate.save(base_filepath))
        return base_filepath, "audio/mpeg"
    except Exception as edge_err:
        print(f"[TTS WARNING] Edge-TTS failed: {edge_err}. Attempting pyttsx3 fallback.")
        
    # Fallback to local pyttsx3 (uses system's default TTS engine, e.g. SAPI5 on Windows)
    try:
        wav_path = base_filepath.replace(".mp3", ".wav")
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except ImportError:
            pass
        engine = pyttsx3.init()
        engine.save_to_file(text, wav_path)
        engine.runAndWait()
        del engine
        return wav_path, "audio/wav"
    except Exception as py_err:
        print(f"[TTS ERROR] pyttsx3 fallback failed: {py_err}")
        raise py_err

@app.route('/speak')
def speak():
    text = request.args.get('text', '')
    if not text:
        return "Missing text", 400
        
    # Create a unique temp file name
    temp_dir = tempfile.gettempdir()
    unique_id = os.urandom(8).hex()
    base_path = os.path.join(temp_dir, f"lockedin_tts_{unique_id}.mp3")
    
    try:
        final_path, mimetype = synthesize_text(text, base_path)
        
        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(final_path):
                    os.remove(final_path)
            except Exception as e:
                print(f"Error removing temporary audio file: {e}")
            return response
            
        return send_file(final_path, mimetype=mimetype)
    except Exception as e:
        print(f"[TTS ERROR] Failed to synthesize text: {e}")
        return jsonify({"error": "Failed to synthesize speech"}), 500

if __name__ == '__main__':
    threading.Thread(target=lambda: (time.sleep(2), webbrowser.open("http://127.0.0.1:5000")), daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)