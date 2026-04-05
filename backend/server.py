from flask import Flask, render_template, Response, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import sys
import os
import threading
import time
import webbrowser
import subprocess
import tempfile
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from backend.ai_proctor.tracker import FaceTracker
from backend.ai_proctor.audio_monitor import AudioMonitor
from backend.ai_proctor.questions import get_question_by_difficulty, get_question_by_id
from backend.database import init_db, save_session, get_profile, create_user, get_user_by_username

app = Flask(__name__, template_folder=os.path.join(project_root, 'frontend'), static_folder=os.path.join(project_root, 'frontend'))
app.secret_key = 'super_secret_lockedin_key'
CORS(app)

init_db()

proctor_state = {
    "is_active": False, "status": "SECURE", "violations": 0, "current_difficulty": 1,
    "audio_enabled": False, "syntax_errors": 0, "logic_errors": 0, "violation_logs": []
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
            proctor_state.update({
                "is_active": True, "audio_enabled": settings.get('audio', False),
                "violations": 0, "syntax_errors": 0, "logic_errors": 0,
                "current_difficulty": 1, "status": "SECURE", "violation_logs": []
            })
            if proctor_state["audio_enabled"]: audio_tracker.start()
    return jsonify({"status": "started"})

@app.route('/stop_test')
def stop_test():
    global camera, proctor_state
    user_id = session.get('user_id')
    
    if proctor_state["is_active"] and user_id:
        save_session(user_id, proctor_state["current_difficulty"], proctor_state["violations"], 
                     proctor_state["syntax_errors"], proctor_state["logic_errors"])
                     
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
    if proctor_state["is_active"]:
        proctor_state["violations"] += 1
        log_incident("TAB SWITCHED")
        proctor_state["status"] = "VIOLATION (TAB SWITCHED)"
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
        success = not is_error and "ALL TESTS PASSED" in output_text
        if success: proctor_state["current_difficulty"] = min(10, proctor_state["current_difficulty"] + 1)
        return jsonify({"stdout": output_text, "status": {"id": 3 if success else 11, "description": "Accepted" if success else "Test Failed"}})
    except Exception as e: return jsonify({"stdout": f"Server Error: {str(e)}", "status": {"id": 6}})

if __name__ == '__main__':
    threading.Thread(target=lambda: (time.sleep(2), webbrowser.open("http://127.0.0.1:5000")), daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)