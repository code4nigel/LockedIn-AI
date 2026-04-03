import cv2
import sys
import os
import time

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path: sys.path.append(project_root)
if current_dir not in sys.path: sys.path.append(current_dir)

from backend.ai_proctor.tracker import FaceTracker
from backend.ai_proctor.audio_monitor import AudioMonitor
from backend.ai_proctor.scorer import calculate_cheat_score, calculate_integrity
from backend.ai_proctor.questions import get_question_by_difficulty

def run_test_session():
    # Setup Camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    tracker = FaceTracker()
    audio = AudioMonitor()
    
    # State management
    current_difficulty = 1
    session_stats = {"eyes_away_frames": 0, "audio_spikes": 0, "multi_face_frames": 0}
    start_time = time.time()
    
    # Get first question
    active_question = get_question_by_difficulty(current_difficulty, 0)

    window_name = 'LockedIn - Adaptive Interview'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)

    print(f"TEST STARTED: {active_question['title']}")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        # AI Monitoring
        faces, away = tracker.process_frame(frame)
        if faces > 1: session_stats["multi_face_frames"] += 1
        if away or faces == 0: session_stats["eyes_away_frames"] += 1
        if audio.is_noisy(): session_stats["audio_spikes"] += 1

        # UI OVERLAY - Question Info
        cv2.putText(frame, f"Q: {active_question['title']} (Diff: {active_question['difficulty']})", 
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # PROCTOR STATUS
        status = "SECURE" if (faces == 1 and not away) else "WATCHING"
        color = (0, 255, 0) if status == "SECURE" else (0, 0, 255)
        cv2.putText(frame, f"PROCTOR: {status}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # INSTRUCTION
        cv2.putText(frame, "Press 'N' for Next (Simulate Solve) or 'Esc' to End", 
                    (20, 680), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27: # Esc
            break
        elif key == ord('n'): # Simulate solving a question
            print("Question Solved! Adapting difficulty...")
            current_difficulty = active_question['difficulty']
            active_question = get_question_by_difficulty(current_difficulty, 1)
            print(f"Next Question: {active_question['title']}")

    # Final Report
    duration = time.time() - start_time
    # Approx 30 FPS logic for second conversion
    eyes_sec = session_stats["eyes_away_frames"] / 30
    multi_sec = session_stats["multi_face_frames"] / 30
    
    cheat_score = calculate_cheat_score(eyes_sec, session_stats["audio_spikes"], multi_sec)
    integrity = calculate_integrity(cheat_score)

    print("\n" + "="*40)
    print("         LockedIn FINAL REPORT")
    print("="*40)
    print(f"Total Duration: {duration:.1f} seconds")
    print(f"Final Difficulty Reached: {active_question['difficulty']}")
    print(f"Integrity Score: {integrity}%")
    print(f"Cheat Risk: {'HIGH' if cheat_score > 70 else 'MEDIUM' if cheat_score > 30 else 'LOW'}")
    print("="*40)

    cap.release()
    cv2.destroyAllWindows()
    audio.stop()

if __name__ == "__main__":
    run_test_session()