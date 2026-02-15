import sys
import os

print("Python executable:", sys.executable)

try:
    import mediapipe as mp
    print("MediaPipe imported. File:", mp.__file__)
    print("Dir mp:", dir(mp))
    
    try:
        import mediapipe.solutions
        print("Imported mediapipe.solutions successfully")
        print("Dir mp.solutions:", dir(mp.solutions))
    except ImportError as e:
        print("Failed to import mediapipe.solutions:", e)

    try:
        from mediapipe import solutions
        print("From mediapipe import solutions success")
    except ImportError as e:
        print("Failed 'from mediapipe import solutions':", e)

except ImportError as e:
    print("CRITICAL: Could not import mediapipe:", e)
