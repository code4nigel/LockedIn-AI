from flask import Flask, render_template, Response, request, jsonify
from flask_cors import CORS
import cv2
import sys
import os
import threading
import time
import webbrowser
import requests

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from backend.ai_proctor.tracker import FaceTracker
from backend.ai_proctor.audio_monitor import AudioMonitor
from backend.ai_proctor.questions import get_question_by_difficulty

app = Flask(__name__, 
            template_folder=os.path.join(project_root, 'frontend'),
            static_folder=os.path.join(project_root, 'frontend'))
CORS(app)

# Global states
proctor_state = {
    "is_active": False,
    "status": "SECURE",
    "violations": 0,
    "current_difficulty": 1
}

PISTON_URL = "https://emkc.org/api/v2/piston/execute"
camera = None
camera_lock = threading.Lock()
tracker = FaceTracker()

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    global camera, proctor_state
    while True:
        if not proctor_state["is_active"]:
            break
            
        with camera_lock:
            if camera is None or not camera.isOpened():
                time.sleep(0.1)
                continue
            success, frame = camera.read()
            
        if not success:
            continue
        
        try:
            # Match the return values of your tracker.py (faces, away)
            faces, away = tracker.process_frame(frame)
            
            proctor_state["status"] = "SECURE" if (faces == 1 and not away) else "VIOLATION"
            color = (0, 255, 0) if proctor_state["status"] == "SECURE" else (0, 0, 255)
                
            cv2.putText(frame, f"AI: {proctor_state['status']}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret: continue
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception as e:
            print(f"Frame Error: {e}")
            continue

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_current_question')
def get_current_question():
    q = get_question_by_difficulty(proctor_state["current_difficulty"], 0)
    return jsonify(q)

@app.route('/start_test')
def start_test():
    global camera
    if not proctor_state["is_active"]:
        camera = cv2.VideoCapture(0)
        proctor_state["is_active"] = True
    return jsonify({"status": "started"})

@app.route('/stop_test')
def stop_test():
    global camera
    proctor_state["is_active"] = False
    time.sleep(0.3)
    with camera_lock:
        if camera:
            camera.release()
            camera = None
    return jsonify({"status": "stopped"})

@app.route('/status')
def get_status():
    return jsonify(proctor_state)

@app.route('/run_code', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    lang = data.get('language', 'python')
    stdin = data.get('stdin', '')

    lang_map = {
        "python": {"n": "python", "v": "3.10.0"},
        "java8": {"n": "java", "v": "1.8.0"},
        "java15": {"n": "java", "v": "15.0.2"}
    }
    target = lang_map.get(lang, lang_map["python"])

    try:
        res = requests.post(PISTON_URL, json={
            "language": target["n"],
            "version": target["v"],
            "files": [{"content": code}],
            "stdin": stdin
        }, timeout=10).json()
        
        run = res.get('run', {})
        output = run.get('stdout', '') + run.get('stderr', '')
        success = (run.get('code') == 0 and not run.get('stderr'))
        
        if success:
            proctor_state["current_difficulty"] += 1
            
        return jsonify({
            "stdout": output if output else "> No output.",
            "status": {"id": 3 if success else 11, "description": "Accepted" if success else "Error"}
        })
    except Exception as e:
        return jsonify({"stdout": f"Server Error: {str(e)}", "status": {"id": 6}})

if __name__ == '__main__':
    threading.Thread(target=lambda: (time.sleep(2), webbrowser.open("http://127.0.0.1:5000"))).start()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)