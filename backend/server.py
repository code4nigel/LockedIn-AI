from flask import Flask, render_template, Response, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from google import genai
from dotenv import load_dotenv
import cv2
import sys
import os
import threading
import time
import webbrowser
import subprocess
import tempfile
import json
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Force reload environment to catch .env changes
load_dotenv(override=True)
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

GEMINI_MODEL_ID = 'gemini-2.5-flash' # Changed from 2.0-flash to fix rate limit errors

if GOOGLE_API_KEY:
    print(f"DEBUG: Gemini API Key loaded (first 4 chars: {GOOGLE_API_KEY[:4]}...)")
    client = genai.Client(api_key=GOOGLE_API_KEY)
else:
    client = None

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
    if not client:
        return jsonify({"error": "Gemini API key not configured"}), 500
    
    data = request.json
    code = data.get('code')
    question_id = data.get('question_id')
    language = data.get('language')
    history = data.get('history', [])
    
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
    
    try:
        # Convert history format for new SDK
        gemini_history = []
        for msg in history[:-1]:
            role = "user" if msg['role'] == "user" else "model"
            gemini_history.append({"role": role, "parts": [{"text": msg['content']}]})
            
        chat = client.chats.create(model=GEMINI_MODEL_ID, history=gemini_history)
        response = chat.send_message(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    if not client:
        return jsonify({"error": "Gemini API key not configured"}), 500
    
    data = request.json
    history = data.get('history', [])
    prompt = data.get('prompt')
    
    system_instruction = """
    You are an expert Technical and Behavioral Interviewer preparing the candidate for top-tier software engineering roles.
    Role and Responsibilities:
    1. Conduct a realistic, challenging, and dynamic behavioral and system design interview.
    2. DO NOT ask the same basic questions every time. Start with a unique behavioral or introductory question (e.g., a specific conflict, a past failure, a unique technical challenge, why they want this role).
    3. After the candidate answers a question, briefly provide 1-2 sentences of constructive feedback directly to the candidate, pointing out what was good and what was lacking.
    4. Then, immediately ask the next challenging question (e.g., jump into a high-level system design scenario or another deep behavioral aspect).
    5. Maintain a professional, strict, but fair tone. Do not be overly polite or chatty.
    6. Keep your total response under 4-5 sentences so it can be easily spoken aloud by TTS.
    """
    
    if not history:
        prompt = system_instruction + f"\n\nThe candidate is ready. Introduce yourself briefly and ask your first challenging question. The candidate said: {prompt}"
    
    try:
        # Convert history format for new SDK
        gemini_history = []
        for msg in history:
            role = "user" if msg['role'] == "user" else "model"
            gemini_history.append({"role": role, "parts": [{"text": msg['content']}]})
            
        chat = client.chats.create(model=GEMINI_MODEL_ID, history=gemini_history)
        response = chat.send_message(prompt)
        
        proctor_state["behavioral_feedback"] = "Completed verbal interview."
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verbal_report', methods=['POST'])
def verbal_report():
    if not client:
        return jsonify({"error": "Gemini API key not configured"}), 500
        
    data = request.json
    history = data.get('history', [])
    
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
    
    try:
        # Convert history format for new SDK
        gemini_history = []
        for msg in history:
            role = "user" if msg['role'] == "user" else "model"
            gemini_history.append({"role": role, "parts": [{"text": msg['content']}]})
            
        chat = client.chats.create(model=GEMINI_MODEL_ID, history=gemini_history)
        response = chat.send_message(prompt)
        
        # Clean up possible markdown block from LLM
        response_text = response.text.replace('```json', '').replace('```', '').strip()
        report = json.loads(response_text)
        
        # Save to DB
        proctor_state["behavioral_feedback"] = report.get('summary', 'Interview completed.')
        proctor_state["aptitude_score"] = report.get('score', 0) // 10  # Scale 100 to 10
        
        return jsonify(report)
    except Exception as e:
        print("Error generating verbal report:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    threading.Thread(target=lambda: (time.sleep(2), webbrowser.open("http://127.0.0.1:5000")), daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)