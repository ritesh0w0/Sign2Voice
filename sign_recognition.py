import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from collections import Counter
import cv2
import mediapipe as mp
import numpy as np


class SignRecognizer:
    """
    Robust MediaPipe-powered real-time gesture recognizer.
    Utilizes palm-scale invariant Euclidean joint distances, thumb posture analysis,
    and temporal motion tracking.
    """

    def __init__(self):
        try:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.55,
                min_tracking_confidence=0.55
            )
        except Exception as e:
            print(f"[CRITICAL] MediaPipe Initialization Error: {e}")
            self.hands = None

        # Stability history buffer (temporal smoothing)
        self.history = []
        self.history_size = 3

        # Motion tracking
        self.last_wrist_y = None
        self.motion_score = 1.0

    def detect_sign(self, image_bytes: bytes):
        """
        Processes an encoded image buffer, predicts gesture sign, and returns
        (predicted_sign, debug_metadata).
        """
        raw_sign, debug_info = self._process_frame(image_bytes)

        # Add to rolling history
        self.history.append(raw_sign)
        if len(self.history) > self.history_size:
            self.history.pop(0)

        # Require minimum history to stabilize
        if len(self.history) < self.history_size:
            return "Unknown Sign", debug_info

        # Majority vote
        counts = Counter(self.history)
        most_common, count = counts.most_common(1)[0]

        # 2 out of 3 frames must agree
        if count >= 2 and most_common not in ["Unknown Sign", "No Hand Detected"]:
            return most_common, debug_info

        if most_common == "No Hand Detected":
            return "No Hand Detected", debug_info

        return "Unknown Sign", debug_info

    def _calculate_motion(self, current_wrist_y: float) -> float:
        """Computes instantaneous vertical wrist displacement."""
        if self.last_wrist_y is None:
            self.last_wrist_y = current_wrist_y
            return 1.0

        diff = abs(current_wrist_y - self.last_wrist_y)
        self.last_wrist_y = current_wrist_y
        return diff

    def _process_frame(self, image_bytes: bytes):
        empty_debug = {"text": "No Input", "fingers": [], "motion": 0.0, "landmarks": []}
        if self.hands is None:
            return "Error: Model Init Failed", empty_debug

        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return "Error: Bad Image", empty_debug

        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        try:
            results = self.hands.process(img_rgb)
        except Exception as e:
            print(f"[Vision Processing Error] {e}")
            return "Error: Processing Failed", empty_debug

        if not results.multi_hand_landmarks:
            return "No Hand Detected", {"text": "No Hand", "fingers": [], "motion": 0.0, "landmarks": []}

        hand_lms = results.multi_hand_landmarks[0]
        lm = hand_lms.landmark

        # Extract normalized 2D landmarks for frontend overlay
        landmarks_data = [{"x": round(p.x, 3), "y": round(p.y, 3)} for p in lm]

        wrist = lm[0]
        self.motion_score = self._calculate_motion(wrist.y)

        def get_dist(p1, p2):
            return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5

        # --- Distance-Based Finger State ---
        # A finger is OPEN if the fingertip is further from the wrist than the PIP joint
        fingers_4 = []
        tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky tips
        pips = [6, 10, 14, 18]  # Corresponding PIP knuckles

        for i in range(4):
            dist_tip = get_dist(lm[tips[i]], wrist)
            dist_pip = get_dist(lm[pips[i]], wrist)
            if dist_tip > dist_pip * 1.15:
                fingers_4.append(1)
            else:
                fingers_4.append(0)

        # Thumb analysis (palm-scale invariant)
        thumb_tip = lm[4]
        thumb_ip = lm[3]
        index_mcp = lm[5]

        # Palm scale reference (wrist to index MCP)
        palm_scale = get_dist(wrist, index_mcp)

        # 1. Thumb extended away from palm
        dist_thumb_index = get_dist(thumb_tip, index_mcp)
        is_thumb_extended = dist_thumb_index > (palm_scale * 0.35)

        # 2. Thumb tucked into palm (for '4')
        dist_thumb_ring = get_dist(thumb_tip, lm[13])
        is_thumb_tucked = dist_thumb_ring < (palm_scale * 0.45)

        # 3. Vertical alignment
        thumb_is_up = is_thumb_extended and (thumb_tip.y < thumb_ip.y)
        thumb_is_down = is_thumb_extended and (thumb_tip.y > thumb_ip.y)

        thumb_state_str = "Up" if thumb_is_up else ("Dn" if thumb_is_down else "-")
        debug_str = f"F:{fingers_4} T:{thumb_state_str}"
        debug_info = {
            "text": debug_str,
            "fingers": fingers_4,
            "thumb": thumb_state_str,
            "motion": round(self.motion_score, 4),
            "landmarks": landmarks_data
        }

        # --- Comprehensive Pattern Matching Matrix ---

        # 1. OK Sign: Thumb tip near Index tip, other 3 fingers open
        dist_thumb_index_tips = get_dist(thumb_tip, lm[8])
        if dist_thumb_index_tips < (palm_scale * 0.30) and fingers_4[1:] == [1, 1, 1]:
            return "OK", debug_info

        # 2. Hello / 4 / 5: 4 fingers extended
        if fingers_4 == [1, 1, 1, 1]:
            # Priority: '4' (Thumb Tucked)
            if is_thumb_tucked or not is_thumb_extended:
                return "4", debug_info

            # Motion check: Hello = dynamic wave motion; 5 = static held hand
            if self.motion_score < 0.015:
                debug_info["text"] += " (Still)"
                return "5", debug_info
            else:
                debug_info["text"] += " (Wave)"
                return "Hello", debug_info

        # 3. Yes: Fist + Thumbs Up
        if fingers_4 == [0, 0, 0, 0] and thumb_is_up:
            return "Yes", debug_info

        # 4. No: Fist + Thumbs Down
        if fingers_4 == [0, 0, 0, 0] and thumb_is_down:
            return "No", debug_info

        # 5. 2 / Victory: Index & Middle Extended
        if fingers_4 == [1, 1, 0, 0]:
            return "2", debug_info

        # 6. I Love You: Thumb + Index + Pinky Open (ASL ILY)
        if fingers_4 == [1, 0, 0, 1] and thumb_is_up:
            return "I Love You", debug_info

        # 7. Help / Call Me: Thumb + Pinky Open
        if fingers_4 == [0, 0, 0, 1] and thumb_is_up:
            return "Help", debug_info

        # 8. Rock / Horns: Index and Pinky Open, Middle and Ring Folded
        if fingers_4 == [1, 0, 0, 1] and not thumb_is_up:
            return "Rock", debug_info

        # 9. Numbers
        if fingers_4 == [1, 0, 0, 0] and not thumb_is_up:
            return "1", debug_info
        if fingers_4 == [1, 1, 1, 0]:
            return "3", debug_info

        # 10. ASL Letters
        if fingers_4 == [1, 0, 0, 0] and thumb_is_up:
            return "L", debug_info
        if fingers_4 == [0, 0, 0, 1] and thumb_is_up:
            return "Y", debug_info

        # 11. Fist / Stop / 0
        if fingers_4 == [0, 0, 0, 0] and not thumb_is_up and not thumb_is_down:
            return "Fist", debug_info

        return "Unknown Sign", debug_info
