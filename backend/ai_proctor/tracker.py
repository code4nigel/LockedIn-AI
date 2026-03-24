import cv2
import mediapipe as mp
import numpy as np

class FaceTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

    def process_frame(self, frame):
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        face_count = 0
        looking_away = False

        # Visualizing the "Safe Zone" for the head (Widened to 40% - 60%)
        cv2.line(frame, (int(w * 0.40), 0), (int(w * 0.40), h), (255, 255, 255), 1)
        cv2.line(frame, (int(w * 0.60), 0), (int(w * 0.60), h), (255, 255, 255), 1)

        if results.multi_face_landmarks:
            face_count = len(results.multi_face_landmarks)
            mesh = results.multi_face_landmarks[0].landmark
            
            # 1. Head Pose Visualization
            nose = mesh[1]
            nose_x, nose_y = int(nose.x * w), int(nose.y * h)
            cv2.circle(frame, (nose_x, nose_y), 5, (0, 255, 255), -1)

            # Widened Head Pose Threshold
            if nose.x < 0.40 or nose.x > 0.60:
                looking_away = True

            # 2. Iris Visualization Logic
            def get_eye_ratio(iris_idx, inner_idx, outer_idx, draw=False):
                iris = mesh[iris_idx]
                inner = mesh[inner_idx]
                outer = mesh[outer_idx]
                
                if draw:
                    ix, iy = int(iris.x * w), int(iris.y * h)
                    inx, iny = int(inner.x * w), int(inner.y * h)
                    ox, oy = int(outer.x * w), int(outer.y * h)
                    cv2.circle(frame, (ix, iy), 3, (255, 0, 0), -1)
                    cv2.circle(frame, (inx, iny), 2, (0, 255, 0), -1)
                    cv2.circle(frame, (ox, oy), 2, (0, 255, 0), -1)

                total_w = abs(outer.x - inner.x)
                if total_w == 0: return 0.5
                # Using absolute distance to normalize ratio correctly
                return (iris.x - min(inner.x, outer.x)) / total_w

            l_ratio = get_eye_ratio(468, 133, 33, draw=True)
            r_ratio = get_eye_ratio(473, 362, 263, draw=True)

            # Widened Iris Threshold (Normal range is 0.35 to 0.65)
            if not (0.35 < l_ratio < 0.65) or not (0.35 < r_ratio < 0.65):
                looking_away = True
        
        return face_count, looking_away