import mediapipe as mp
try:
    print("MediaPipe Attributes:", dir(mp))
    print("Checking solutions...")
    print(mp.solutions)
    print("SOLUTIONS FOUND")
except Exception as e:
    print("ERROR:", e)
