import sys
import io

# Force UTF-8 output encoding for Windows command line
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import cv2
import numpy as np
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_endpoints():
    print("Testing /api/health...")
    res = client.get("/api/health")
    print("Health response:", res.status_code, res.json())
    assert res.status_code == 200

    print("\nTesting /api/supported...")
    res = client.get("/api/supported")
    print("Supported response:", res.status_code, "Signs count:", len(res.json()["signs"]))
    assert res.status_code == 200

    print("\nTesting /process_sentence...")
    res = client.post("/process_sentence", json={
        "tokens": ["Hello", "Yes"],
        "target_language": "Kannada"
    })
    print("Process sentence response status:", res.status_code)
    data = res.json()
    print("Original:", data["original"])
    print("Translated:", data["translated"])
    assert res.status_code == 200
    assert "ನಮಸ್ಕಾರ" in data["translated"]

    print("\nTesting /process_frame (3 frames to satisfy temporal stability buffer)...")
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".jpg", img)
    files = {"image": ("test.jpg", encoded.tobytes(), "image/jpeg")}
    data = {"target_language": "English"}

    # Send 3 frames to stabilize buffer
    for i in range(3):
        files = {"image": ("test.jpg", encoded.tobytes(), "image/jpeg")}
        res = client.post("/process_frame", files=files, data=data)
        print(f"Frame {i+1} detected:", res.json()["sign_text"])

    assert res.status_code == 200
    assert res.json()["sign_text"] == "No Hand Detected"

    print("\n>>> ALL SYSTEM TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_endpoints()
