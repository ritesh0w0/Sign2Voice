import mediapipe as mp
import cv2
import numpy as np

class SignRecognizer:
    def __init__(self):
        try:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=1,
                min_detection_confidence=0.5
            )
        except Exception as e:
            print(f"CRITICAL: MediaPipe Error: {e}")
            self.hands = None
        
        # Stability Filter
        self.history = []
        self.history_size = 3
        
        # Motion Tracking
        self.last_wrist_y = None
        self.motion_score = 1.0

    def detect_sign(self, image_bytes):
        raw_sign, debug_info = self._process_frame(image_bytes)
        
        # Add to history
        self.history.append(raw_sign)
        if len(self.history) > self.history_size:
            self.history.pop(0)
            
        # Check stability (require majority)
        if len(self.history) < self.history_size:
             return "Unknown Sign", debug_info
        
        # Count occurrences
        from collections import Counter
        counts = Counter(self.history)
        most_common, count = counts.most_common(1)[0]
        
        # Threshold: 2 out of 3 frames must match
        if count >= 2 and most_common != "Unknown Sign" and most_common != "No Hand Detected":
            return most_common, debug_info
        
        if most_common == "No Hand Detected":
             return "No Hand Detected", debug_info
             
        return "Unknown Sign", debug_info

    def _calculate_motion(self, current_wrist_y):
        # Simple derivative of Y position
        if self.last_wrist_y is None:
            self.last_wrist_y = current_wrist_y
            return 1.0 # Assume moving initially
            
        diff = abs(current_wrist_y - self.last_wrist_y)
        self.last_wrist_y = current_wrist_y
        return diff

    def _process_frame(self, image_bytes):
        if self.hands is None:
            return "Error: Model Init Failed", ""

        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return "Error: Bad Image", ""

        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        try:
            results = self.hands.process(img_rgb)
        except Exception as e:
            print(f"Processing Error: {e}")
            return "Error: Processing Failed", ""

        if not results.multi_hand_landmarks:
            return "No Hand Detected", "No Hand"

        lm = results.multi_hand_landmarks[0].landmark
        
        # Motion Calculation (Wrist Y variance)
        wrist_y = lm[0].y
        self.motion_score = self._calculate_motion(wrist_y)
        
        # --- Robust Finger State (Distance Based) ---
        # Logic: A finger is OPEN if the Tip is further from the Wrist (0) than the PIP joint (Knuckle) is.
        # This works even if the hand is tilted or upside down.
        
        wrist = lm[0]
        def get_dist(p1, p2):
            return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**0.5
            
        fingers_4 = [] 
        tips = [8, 12, 16, 20] # Index, Middle, Ring, Pinky
        pips = [6, 10, 14, 18] # PIP joints
        
        for i in range(4):
            dist_tip = get_dist(lm[tips[i]], wrist)
            dist_pip = get_dist(lm[pips[i]], wrist)
            
            # If Tip is further than PIP, it's extended (Open)
            # Threshold tuned to 1.15 (Balanced between Fists and Open)
            if dist_tip > dist_pip * 1.15: 
                fingers_4.append(1)
            else:
                fingers_4.append(0)
                
        # Thumb Analysis (Palm-Scale Invariant)
        thumb_tip = lm[4]
        thumb_ip = lm[3]
        thumb_mcp = lm[2]
        index_mcp = lm[5]
        pinky_mcp = lm[17]
        
        # Scale factor: Distance from Wrist to Index MCP (~ Palm Height)
        palm_scale = get_dist(wrist, index_mcp)
        
        # 1. Is thumb extended AWAY from hand?
        # Measure distance from Index MCP Base
        dist_thumb_index = get_dist(thumb_tip, index_mcp)
        
        # Threshold Reduced to 0.35 (Easier to flare/detect Open)
        is_thumb_extended = dist_thumb_index > (palm_scale * 0.35)
        
        # 2. Check for "Tucked" Thumb (Crucial for Sign '4')
        # Check distance to Ring Finger MCP (better than Pinky for '4' usually)
        dist_thumb_ring = get_dist(thumb_tip, lm[13]) 
        is_thumb_tucked = dist_thumb_ring < (palm_scale * 0.45)
        
        # 3. Is thumb vertical?
        is_thumb_vertical = thumb_tip.y < thumb_ip.y 
        
        # Thumb Up: Extended AND Vertical
        thumb_is_up = is_thumb_extended and is_thumb_vertical
        
        # Thumb Down: Extended AND Pointing Down
        thumb_is_down = is_thumb_extended and (thumb_tip.y > thumb_ip.y)
        
        # Debug String
        debug_str = f"F:{fingers_4} T:{'Up' if thumb_is_up else ('Dn' if thumb_is_down else '-')}"

        # --- Pattern Matching ---
        
        # Hello: All fingers open
        if fingers_4 == [1, 1, 1, 1]: 
             # PRIORITY: Check for "4" (Thumb Tucked)
             # If thumb is explicitly tucked OR not extended -> 4
             if is_thumb_tucked or not is_thumb_extended:
                  return "4", debug_str

             # Motion Check
             # Hello = Moving. 5 = Static.
             # User reported Hello -> 5 (Too aggressive on 5).
             # We set threshold very low on static. 
             # Only if DEAD STILL (< 0.01), call it 5.
             # Any slight wobble (> 0.01) -> Hello.
             if self.motion_score < 0.015: 
                  return "5", debug_str + " (Sta)"
             else:
                  return "Hello", debug_str + " (Mov)"
            
        # Yes: Fist + Thumb Up
        if fingers_4 == [0, 0, 0, 0] and thumb_is_up:
            return "Yes", debug_str
            
        # No: Fist + Thumb Down
        if fingers_4 == [0, 0, 0, 0] and thumb_is_down:
            return "No", debug_str
            
        # 2 (Victory): Index/Middle Open
        if fingers_4 == [1, 1, 0, 0]:
            return "2", debug_str
            
        # I Love You: Thumb Up + Index Open + Pinky Open
        if fingers_4 == [1, 0, 0, 1] and thumb_is_up:
            return "I Love You", debug_str
            
        # Help: Pinky + Thumb Up
        if fingers_4 == [0, 0, 0, 1] and thumb_is_up:
            return "Help", debug_str
            
        # Numbers
        # Note: With stricter open check (1.3), we ensure 1, 2, 3 don't leak extra fingers.
        if fingers_4 == [1, 0, 0, 0] and not thumb_is_up: return "1", debug_str 
        if fingers_4 == [1, 1, 1, 0]: return "3", debug_str 
        
        # Alphabets
        if fingers_4 == [1, 0, 0, 0] and thumb_is_up: return "L", debug_str
        if fingers_4 == [0, 0, 0, 1] and thumb_is_up: return "Y", debug_str 
        
        return "Unknown Sign", debug_str
