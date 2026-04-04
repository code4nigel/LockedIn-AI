from flask import Flask, render_template, Response, request, jsonify
from flask_cors import CORS
import cv2
import sys
import os
import threading
import time
import webbrowser
import subprocess
import tempfile

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from backend.ai_proctor.tracker import FaceTracker
from backend.ai_proctor.questions import get_question_by_difficulty, get_question_by_id

app = Flask(__name__, template_folder=os.path.join(project_root, 'frontend'), static_folder=os.path.join(project_root, 'frontend'))
CORS(app)

proctor_state = {"is_active": False, "status": "SECURE", "violations": 0, "current_difficulty": 1}
camera = None
camera_lock = threading.Lock()
tracker = FaceTracker()

@app.route('/')
def index():
    return render_template('index.html')

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
            if face_count != 1 or looking_away:
                proctor_state["status"] = "VIOLATION"
                color = (0, 0, 255)
            else:
                proctor_state["status"] = "SECURE"
                color = (0, 255, 0)
            cv2.putText(frame, f"AI: {proctor_state['status']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret: continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception:
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
    global camera, proctor_state
    with camera_lock:
        if not proctor_state["is_active"]:
            camera = cv2.VideoCapture(0)
            time.sleep(0.5)
            proctor_state["is_active"] = True
    return jsonify({"status": "started"})

@app.route('/stop_test')
def stop_test():
    global camera, proctor_state
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
    q_id = data.get('question_id')
    
    question = get_question_by_id(q_id)
    if not question:
        return jsonify({"stdout": "Question not found.", "status": {"id": 6, "description": "Error"}})

    output_text = ""
    is_error = False
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            if lang == "python":
                # Inject Python tests
                full_code = code + "\n" + question["python_test"]
                file_path = os.path.join(temp_dir, "solution.py")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(full_code)
                
                res = subprocess.run([sys.executable, file_path], text=True, capture_output=True, timeout=5)
                if res.returncode != 0:
                    is_error = True
                    output_text += "--- TEST FAILED ---\n" + res.stderr
                else:
                    output_text += res.stdout

            elif lang == "java":
                # Save user code as Solution.java
                sol_path = os.path.join(temp_dir, "Solution.java")
                with open(sol_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                # Save test code as Main.java
                main_path = os.path.join(temp_dir, "Main.java")
                with open(main_path, "w", encoding="utf-8") as f:
                    f.write(question["java_test"])
                
                comp = subprocess.run(["javac", sol_path, main_path], text=True, capture_output=True, timeout=5)
                if comp.returncode != 0:
                    is_error = True
                    output_text += "--- COMPILATION ERROR ---\n" + comp.stderr
                else:
                    run_res = subprocess.run(["java", "-cp", temp_dir, "Main"], text=True, capture_output=True, timeout=5)
                    if run_res.returncode != 0:
                        is_error = True
                        output_text += "--- TEST FAILED ---\n" + run_res.stderr
                    else:
                        output_text += run_res.stdout

        if not output_text.strip() and not is_error:
            output_text = "> Execution complete."

        success = not is_error
        if success and "ALL TESTS PASSED" in output_text:
            proctor_state["current_difficulty"] = min(10, proctor_state["current_difficulty"] + 1)
            
        return jsonify({
            "stdout": output_text,
            "status": {
                "id": 3 if success else 11,
                "description": "Accepted" if success else "Test Failed"
            }
        })

    except subprocess.TimeoutExpired:
        return jsonify({"stdout": "Execution timed out.", "status": {"id": 5, "description": "Time Limit Exceeded"}})
    except Exception as e:
        return jsonify({"stdout": f"Server Error: {str(e)}", "status": {"id": 6, "description": "Failed"}})

if __name__ == '__main__':
    threading.Thread(target=lambda: (time.sleep(2), webbrowser.open("http://127.0.0.1:5000")), daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)