import cv2
import sys
import os

# Path setup to ensure module discovery
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path: sys.path.append(project_root)
if current_dir not in sys.path: sys.path.append(current_dir)

try:
    from ai_proctor.tracker import FaceTracker
    from ai_proctor.audio_monitor import AudioMonitor
    from ai_proctor.scorer import calculate_cheat_score, calculate_integrity
except ImportError:
    from backend.ai_proctor.tracker import FaceTracker
    from backend.ai_proctor.audio_monitor import AudioMonitor
    from backend.ai_proctor.scorer import calculate_cheat_score, calculate_integrity

def run():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    tracker = FaceTracker()
    audio = AudioMonitor()
    
    window_name = 'LockedIn - Debug Mode'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    
    stats = {"eyes": 0, "audio": 0, "faces": 0}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        # tracker.process_frame now draws debug info directly on the frame
        faces, away = tracker.process_frame(frame)
        
        if faces > 1: stats["faces"] += 1
        if away or faces == 0: stats["eyes"] += 1
        if audio.is_noisy(): stats["audio"] += 1

        # Status Labeling
        label = "SECURE" if (faces == 1 and not away) else "VIOLATION"
        color = (0, 255, 0) if (faces == 1 and not away) else (0, 0, 255)
        
        cv2.putText(frame, f"STATUS: {label}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
        cv2.putText(frame, f"STATUS: {label}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27: break

    cheat = calculate_cheat_score(stats["eyes"]/30, stats["audio"], stats["faces"]/30)
    print(f"\nIntegrity Score: {calculate_integrity(cheat)}%")
    
    cap.release()
    cv2.destroyAllWindows()
    audio.stop()

if __name__ == "__main__":
    run()