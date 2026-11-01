import os
import math
from PIL import Image, ImageDraw, ImageFont

# Ensure assets directory exists
os.makedirs("assets", exist_ok=True)

# System fonts
FONT_REGULAR = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# -------------------------------------------------------------
# 1. BANNER (assets/banner.png - 1280x420)
# -------------------------------------------------------------
def create_banner():
    width, height = 1280, 420
    img = Image.new("RGBA", (width, height), (8, 12, 22, 255))
    draw = ImageDraw.Draw(img)

    # Ambient gradient glow
    for y in range(height):
        ratio = y / height
        r = int(8 + (18 - 8) * ratio)
        g = int(12 + (24 - 12) * ratio)
        b = int(22 + (45 - 22) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Glowing subtle grid / geometric accent lines
    for x in range(0, width, 60):
        draw.line([(x, 0), (x, height)], fill=(255, 255, 255, 6))
    for y in range(0, height, 60):
        draw.line([(0, y), (width, y)], fill=(255, 255, 255, 6))

    # Neon circles / orbs blur simulation
    for radius, alpha in [(240, 20), (180, 30), (120, 45), (60, 70)]:
        cx, cy = 1100, 180
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                     outline=(99, 102, 241, alpha), width=3)
        cx2, cy2 = 180, 320
        draw.ellipse([cx2 - radius, cy2 - radius, cx2 + radius, cy2 + radius],
                     outline=(6, 182, 212, alpha), width=2)

    # Top Tagline / Category Pill
    pill_font = get_font(FONT_BOLD, 14)
    pill_text = "AI-POWERED ACCESSIBILITY & MULTILINGUAL COMMUNICATION"
    draw.rounded_rectangle([70, 55, 590, 88], radius=16, fill=(99, 102, 241, 35), outline=(99, 102, 241, 140), width=1)
    draw.text((90, 63), pill_text, fill=(199, 210, 254), font=pill_font)

    # Main Project Title
    title_font = get_font(FONT_BOLD, 68)
    draw.text((70, 105), "Sign2Voice", fill=(255, 255, 255), font=title_font)
    version_font = get_font(FONT_BOLD, 22)
    draw.rounded_rectangle([440, 125, 560, 160], radius=10, fill=(6, 182, 212, 40), outline=(6, 182, 212, 160), width=1)
    draw.text((455, 130), "v2.0 Neural", fill=(6, 182, 212), font=version_font)

    # Subtitle / Elevator Pitch
    sub_font = get_font(FONT_REGULAR, 22)
    sub_text = "Real-Time Sign Language Recognition, Heuristic NLP Sentence Formulation,\nand Edge-TTS Multilingual Voice Synthesis."
    draw.text((70, 195), sub_text, fill=(148, 163, 184), font=sub_font, spacing=6)

    # Badges Row
    badges = [
        ("MediaPipe 21 Joints", (6, 182, 212)),
        ("Edge-TTS Neural Voice", (139, 92, 246)),
        ("5 Languages (EN, HI, KN, TA, TE)", (236, 72, 153)),
        ("FastAPI Async Core", (16, 185, 129)),
        ("Sub-50ms Latency", (245, 158, 11))
    ]

    bx = 70
    by = 310
    badge_font = get_font(FONT_BOLD, 14)
    for text, color in badges:
        bbox = draw.textbbox((0, 0), text, font=badge_font)
        bw = bbox[2] - bbox[0] + 32
        draw.rounded_rectangle([bx, by, bx + bw, by + 38], radius=19, fill=(color[0], color[1], color[2], 25), outline=(color[0], color[1], color[2], 120), width=1)
        draw.text((bx + 16, by + 9), text, fill=color, font=badge_font)
        bx += bw + 14

    # Stylized Hand Graphic on Right
    hx, hy = 1040, 200
    # Draw futuristic palm & connected joints
    joint_coords = [
        (hx, hy + 90),       # Wrist 0
        (hx - 50, hy + 50),  # Thumb 1
        (hx - 70, hy + 20),  # Thumb 2
        (hx - 80, hy - 15),  # Thumb 3
        (hx - 85, hy - 50),  # Thumb 4 Tip
        (hx - 30, hy - 20),  # Index 5
        (hx - 35, hy - 65),  # Index 6
        (hx - 38, hy - 105), # Index 7
        (hx - 40, hy - 145), # Index 8 Tip
        (hx, hy - 25),       # Mid 9
        (hx, hy - 75),       # Mid 10
        (hx, hy - 120),      # Mid 11
        (hx, hy - 160),      # Mid 12 Tip
        (hx + 30, hy - 20),  # Ring 13
        (hx + 32, hy - 65),  # Ring 14
        (hx + 33, hy - 105), # Ring 15
        (hx + 35, hy - 145), # Ring 16 Tip
        (hx + 55, hy - 10),  # Pinky 17
        (hx + 60, hy - 45),  # Pinky 18
        (hx + 65, hy - 75),  # Pinky 19
        (hx + 70, hy - 105)  # Pinky 20 Tip
    ]

    connections = [
        (0,1),(1,2),(2,3),(3,4),
        (0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12),
        (0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20),
        (5,9),(9,13),(13,17)
    ]

    for p1, p2 in connections:
        draw.line([joint_coords[p1], joint_coords[p2]], fill=(6, 182, 212, 180), width=2)

    for i, pt in enumerate(joint_coords):
        color = (236, 72, 153, 240) if i in [4, 8, 12, 16, 20] else (139, 92, 246, 240)
        r = 6 if i in [4, 8, 12, 16, 20] else 4
        draw.ellipse([pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r], fill=color)

    img.save("assets/banner.png", "PNG")
    print("[Asset] banner.png created successfully.")

# -------------------------------------------------------------
# 2. ARCHITECTURE DIAGRAM (assets/architecture_diagram.png - 1400x820)
# -------------------------------------------------------------
def create_architecture():
    width, height = 1400, 820
    img = Image.new("RGBA", (width, height), (10, 14, 26, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient fill
    for y in range(height):
        r = int(10 + y * 0.01)
        g = int(14 + y * 0.015)
        b = int(26 + y * 0.02)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Title
    t_font = get_font(FONT_BOLD, 34)
    st_font = get_font(FONT_REGULAR, 17)
    draw.text((60, 45), "Sign2Voice - High-Level System Architecture", fill=(255, 255, 255), font=t_font)
    draw.text((60, 92), "End-to-End Pipeline: From Optical Camera Capture to Real-time Neural Voice Synthesis", fill=(148, 163, 184), font=st_font)

    # 4 Architecture Columns / Stages
    stages = [
        {
            "num": "01",
            "title": "Client & Capture",
            "subtitle": "HTML5 / WebRTC / Canvas",
            "color": (6, 182, 212),
            "items": [
                "Webcam Stream (640x480 RGB)",
                "HTML5 Canvas Overlay",
                "Frame Throttling (3-12 FPS)",
                "Multipart Form Data Dispatch",
                "Local WebAudio Player & Waveform"
            ],
            "x": 60, "w": 280
        },
        {
            "num": "02",
            "title": "Vision & Landmark Core",
            "subtitle": "MediaPipe & OpenCV Engine",
            "color": (99, 102, 241),
            "items": [
                "FastAPI Gateway & CORS",
                "OpenCV Frame Preprocessing",
                "21 3D Joint Landmark Tracking",
                "Palm-Invariant Euclidean Distances",
                "Temporal Rolling Stability Buffer"
            ],
            "x": 380, "w": 290
        },
        {
            "num": "03",
            "title": "NLP Sentence Engine",
            "subtitle": "Token Grammar Synthesis",
            "color": (168, 85, 247),
            "items": [
                "Gesture Token Accumulation",
                "Multi-Sign Sequence Pattern Matching",
                "Natural Sentence Synthesis",
                "Dynamic Context Disambiguation",
                "Emergency / Greeting Priority Logic"
            ],
            "x": 710, "w": 300
        },
        {
            "num": "04",
            "title": "Translation & Voice Core",
            "subtitle": "Deep-Translator & Edge-TTS",
            "color": (236, 72, 153),
            "items": [
                "Pre-warmed Native Dictionary Cache",
                "Deep-Translator Google Fallback",
                "Edge-TTS Microsoft Neural Voices",
                "5 Languages: EN, HI, KN, TA, TE",
                "LRU In-Memory Audio Disk Cache"
            ],
            "x": 1050, "w": 290
        }
    ]

    card_y = 160
    card_h = 440

    stage_num_font = get_font(FONT_BOLD, 18)
    card_title_font = get_font(FONT_BOLD, 19)
    card_sub_font = get_font(FONT_REGULAR, 12)
    item_font = get_font(FONT_REGULAR, 14)

    for stage in stages:
        sx, sw = stage["x"], stage["w"]
        col = stage["color"]

        # Card container
        draw.rounded_rectangle([sx, card_y, sx + sw, card_y + card_h], radius=16,
                               fill=(20, 28, 48, 220), outline=(col[0], col[1], col[2], 90), width=2)

        # Header accent bar
        draw.rounded_rectangle([sx, card_y, sx + sw, card_y + 8], radius=4, fill=col)

        # Stage number pill
        draw.rounded_rectangle([sx + 20, card_y + 24, sx + 68, card_y + 54], radius=8,
                               fill=(col[0], col[1], col[2], 40), outline=(col[0], col[1], col[2], 120), width=1)
        draw.text((sx + 32, card_y + 28), stage["num"], fill=col, font=stage_num_font)

        # Titles
        draw.text((sx + 82, card_y + 24), stage["title"], fill=(255, 255, 255), font=card_title_font)
        draw.text((sx + 82, card_y + 48), stage["subtitle"], fill=(148, 163, 184), font=card_sub_font)

        # Divider
        draw.line([(sx + 20, card_y + 80), (sx + sw - 20, card_y + 80)], fill=(255, 255, 255, 20), width=1)

        # Feature items
        iy = card_y + 105
        for item in stage["items"]:
            # bullet
            draw.ellipse([sx + 24, iy + 6, sx + 32, iy + 14], fill=col)
            draw.text((sx + 44, iy), item, fill=(226, 232, 240), font=item_font)
            iy += 60

    # Draw Connecting Directional Flow Arrows between cards
    arrow_y = card_y + (card_h // 2)
    for i in range(len(stages) - 1):
        s1 = stages[i]
        s2 = stages[i + 1]
        x1 = s1["x"] + s1["w"] + 8
        x2 = s2["x"] - 8
        draw.line([(x1, arrow_y), (x2, arrow_y)], fill=(6, 182, 212, 200), width=3)
        # Arrowhead
        draw.polygon([(x2, arrow_y), (x2 - 10, arrow_y - 6), (x2 - 10, arrow_y + 6)], fill=(6, 182, 212, 240))

    # Bottom Protocol Specs Bar
    draw.rounded_rectangle([60, 640, 1340, 770], radius=14, fill=(16, 22, 38, 240), outline=(255, 255, 255, 25), width=1)
    b_title_font = get_font(FONT_BOLD, 15)
    b_val_font = get_font(FONT_REGULAR, 14)

    specs = [
        ("INFERENCE LATENCY", "< 45ms (CPU Native)"),
        ("VISION BACKEND", "MediaPipe Hands v0.10.14"),
        ("TRANSLATION MATRIX", "Deep-Translator + Native Cache"),
        ("VOICE SYNTHESIS", "Edge-TTS Neural Voices (5 Locales)")
    ]

    bx = 90
    for label, val in specs:
        draw.text((bx, 665), label, fill=(100, 116, 139), font=b_title_font)
        draw.text((bx, 695), val, fill=(6, 182, 212), font=b_val_font)
        bx += 310

    img.save("assets/architecture_diagram.png", "PNG")
    print("[Asset] architecture_diagram.png created successfully.")

# -------------------------------------------------------------
# 3. DASHBOARD MOCKUP SCREENSHOT (assets/dashboard_screenshot.png - 1400x900)
# -------------------------------------------------------------
def create_dashboard_mockup():
    width, height = 1400, 900
    img = Image.new("RGBA", (width, height), (11, 15, 25, 255))
    draw = ImageDraw.Draw(img)

    # Ambient glows
    for y in range(height):
        ratio = y / height
        draw.line([(0, y), (width, y)], fill=(int(11 + 6 * ratio), int(15 + 8 * ratio), int(25 + 18 * ratio), 255))

    # App Header Bar
    draw.rounded_rectangle([0, 0, width, 75], radius=0, fill=(15, 21, 35, 240), outline=(255, 255, 255, 20), width=1)
    draw.rounded_rectangle([35, 16, 75, 56], radius=10, fill=(99, 102, 241, 200))
    # Brand logo icon text
    h_font = get_font(FONT_BOLD, 22)
    draw.text((90, 24), "Sign2Voice", fill=(255, 255, 255), font=h_font)

    badge_font = get_font(FONT_BOLD, 12)
    draw.rounded_rectangle([220, 27, 305, 50], radius=11, fill=(99, 102, 241, 50), outline=(99, 102, 241, 140), width=1)
    draw.text((230, 31), "v2.0 Neural", fill=(199, 210, 254), font=badge_font)

    # Header Right Status
    draw.rounded_rectangle([1060, 22, 1190, 52], radius=15, fill=(16, 185, 129, 30), outline=(16, 185, 129, 120), width=1)
    draw.ellipse([1075, 33, 1085, 43], fill=(16, 185, 129, 255))
    draw.text((1095, 28), "Engine Ready", fill=(16, 185, 129), font=get_font(FONT_BOLD, 13))

    draw.rounded_rectangle([1210, 22, 1360, 52], radius=8, fill=(255, 255, 255, 15), outline=(255, 255, 255, 30), width=1)
    draw.text((1230, 28), "📖 Gesture Guide", fill=(255, 255, 255), font=get_font(FONT_REGULAR, 13))

    # Left Container: Video Feed (w: 720, h: 760)
    vx, vy, vw, vh = 40, 105, 710, 750
    draw.rounded_rectangle([vx, vy, vx + vw, vy + vh], radius=18, fill=(19, 26, 44, 220), outline=(255, 255, 255, 30), width=1)

    # Video viewport inner
    cx, cy, cw, ch = vx + 24, vy + 70, vw - 48, 520
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=14, fill=(5, 8, 14, 255), outline=(6, 182, 212, 100), width=2)

    # Video HUD corners
    def draw_hud_corners(bx, by, bw, bh):
        length = 20
        # TL
        draw.line([(bx, by), (bx + length, by)], fill=(6, 182, 212, 255), width=3)
        draw.line([(bx, by), (bx, by + length)], fill=(6, 182, 212, 255), width=3)
        # TR
        draw.line([(bx + bw, by), (bx + bw - length, by)], fill=(6, 182, 212, 255), width=3)
        draw.line([(bx + bw, by), (bx + bw, by + length)], fill=(6, 182, 212, 255), width=3)
        # BL
        draw.line([(bx, by + bh), (bx + length, by + bh)], fill=(6, 182, 212, 255), width=3)
        draw.line([(bx, by + bh), (bx, by + bh - length)], fill=(6, 182, 212, 255), width=3)
        # BR
        draw.line([(bx + bw, by + bh), (bx + bw - length, by + bh)], fill=(6, 182, 212, 255), width=3)
        draw.line([(bx + bw, by + bh), (bx + bw, by + bh - length)], fill=(6, 182, 212, 255), width=3)

    draw_hud_corners(cx + 12, cy + 12, cw - 24, ch - 24)

    # MediaPipe hand skeleton mock inside video viewport
    hx, hy = cx + (cw // 2) - 20, cy + (ch // 2) + 20
    j_coords = [
        (hx, hy + 120),
        (hx - 60, hy + 70), (hx - 90, hy + 30), (hx - 110, hy - 20), (hx - 120, hy - 70), # Thumb
        (hx - 45, hy - 30), (hx - 50, hy - 90), (hx - 55, hy - 150), (hx - 60, hy - 210), # Index
        (hx, hy - 40), (hx, hy - 110), (hx, hy - 170), (hx, hy - 230),                      # Middle
        (hx + 45, hy - 30), (hx + 48, hy - 90), (hx + 50, hy - 150), (hx + 55, hy - 205), # Ring
        (hx + 80, hy - 15), (hx + 88, hy - 65), (hx + 95, hy - 110), (hx + 105, hy - 150) # Pinky
    ]
    conns = [
        (0,1),(1,2),(2,3),(3,4),
        (0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12),
        (0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20),
        (5,9),(9,13),(13,17)
    ]
    for p1, p2 in conns:
        draw.line([j_coords[p1], j_coords[p2]], fill=(6, 182, 212, 220), width=3)
    for i, pt in enumerate(j_coords):
        color = (236, 72, 153, 255) if i in [4, 8, 12, 16, 20] else (168, 85, 247, 255)
        r = 7 if i in [4, 8, 12, 16, 20] else 4
        draw.ellipse([pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r], fill=color)

    # Floating Detection Pill over video
    draw.rounded_rectangle([cx + 20, cy + ch - 75, cx + cw - 20, cy + ch - 20], radius=12,
                           fill=(15, 23, 42, 235), outline=(99, 102, 241, 140), width=1)
    draw.text((cx + 38, cy + ch - 63), "👋  Hello (Wave Motion)", fill=(255, 255, 255), font=get_font(FONT_BOLD, 18))
    draw.rounded_rectangle([cx + cw - 210, cy + ch - 67, cx + cw - 35, cy + ch - 30], radius=8,
                           fill=(6, 182, 212, 35), outline=(6, 182, 212, 140), width=1)
    draw.text((cx + cw - 195, cy + ch - 58), "F:[1, 1, 1, 1] T:Up", fill=(6, 182, 212), font=get_font(FONT_MONO, 14))

    # Camera buttons bottom
    draw.rounded_rectangle([vx + 24, vy + ch + 90, vx + 180, vy + ch + 135], radius=8, fill=(99, 102, 241, 230))
    draw.text((vx + 50, vy + ch + 102), "▶ Start Camera", fill=(255, 255, 255), font=get_font(FONT_BOLD, 14))

    draw.rounded_rectangle([vx + 200, vy + ch + 90, vx + 380, vy + ch + 135], radius=8, fill=(255, 255, 255, 15), outline=(255, 255, 255, 30), width=1)
    draw.text((vx + 225, vy + ch + 102), "➕ Add to Sentence", fill=(255, 255, 255), font=get_font(FONT_BOLD, 14))

    # Right Container 1: Instant Translation & Voice
    rx, ry, rw = 780, 105, 580
    draw.rounded_rectangle([rx, ry, rx + rw, ry + 230], radius=18, fill=(19, 26, 44, 220), outline=(255, 255, 255, 30), width=1)
    draw.text((rx + 24, ry + 24), "🌐 Instant Translation & Voice", fill=(255, 255, 255), font=get_font(FONT_BOLD, 18))

    # Language Dropdown Pill
    draw.rounded_rectangle([rx + rw - 180, ry + 20, rx + rw - 24, ry + 54], radius=8, fill=(15, 23, 42, 240), outline=(99, 102, 241, 160), width=1)
    draw.text((rx + rw - 165, ry + 28), "ಕನ್ನಡ (Kannada) ▼", fill=(255, 255, 255), font=get_font(FONT_BOLD, 13))

    # Translation display box
    draw.rounded_rectangle([rx + 24, ry + 70, rx + rw - 24, ry + 160], radius=10, fill=(12, 18, 32, 230), outline=(255, 255, 255, 20), width=1)
    draw.text((rx + 40, ry + 82), "TRANSLATED SPEECH OUTPUT", fill=(100, 116, 139), font=get_font(FONT_BOLD, 11))
    draw.text((rx + 40, ry + 108), "ನಮಸ್ಕಾರ (Namaskara)", fill=(6, 182, 212), font=get_font(FONT_BOLD, 26))

    # Audio Replay Bar with Animated Bars
    draw.ellipse([rx + 30, ry + 175, rx + 65, ry + 210], fill=(99, 102, 241, 240))
    draw.text((rx + 42, ry + 184), "🔊", font=get_font(FONT_REGULAR, 14))
    for i, bh in enumerate([8, 18, 24, 14, 28, 16, 10]):
        draw.rounded_rectangle([rx + 80 + i * 8, ry + 205 - bh, rx + 84 + i * 8, ry + 205], radius=2, fill=(6, 182, 212, 240))
    draw.text((rx + 155, ry + 188), "Edge-TTS Neural Voice (kn-IN-GaganNeural)", fill=(148, 163, 184), font=get_font(FONT_REGULAR, 13))

    # Right Container 2: Sentence Construction Studio
    sy = ry + 250
    draw.rounded_rectangle([rx, sy, rx + rw, sy + 280], radius=18, fill=(19, 26, 44, 220), outline=(255, 255, 255, 30), width=1)
    draw.text((rx + 24, sy + 24), "🧩 Sentence Construction Studio", fill=(255, 255, 255), font=get_font(FONT_BOLD, 18))

    # Tokens Chips Box
    draw.rounded_rectangle([rx + 24, sy + 65, rx + rw - 24, sy + 125], radius=10, fill=(12, 18, 32, 230), outline=(99, 102, 241, 80), width=1)
    tokens = ["Hello ✕", "Yes ✕", "Victory ✕"]
    tx = rx + 36
    for tok in tokens:
        draw.rounded_rectangle([tx, sy + 77, tx + 95, sy + 112], radius=17, fill=(99, 102, 241, 45), outline=(99, 102, 241, 140), width=1)
        draw.text((tx + 16, sy + 85), tok, fill=(255, 255, 255), font=get_font(FONT_BOLD, 13))
        tx += 110

    # Synthesize Button
    draw.rounded_rectangle([rx + 24, sy + 140, rx + rw - 24, sy + 185], radius=8, fill=(236, 72, 153, 230))
    draw.text((rx + 165, sy + 152), "✨ Synthesize & Speak Full Sentence", fill=(255, 255, 255), font=get_font(FONT_BOLD, 15))

    # Sentence Result Box
    draw.rounded_rectangle([rx + 24, sy + 200, rx + rw - 24, sy + 265], radius=8, fill=(12, 18, 32, 230), outline=(255, 255, 255, 20), width=1)
    draw.text((rx + 36, sy + 210), '"Hello! Everything looks good."', fill=(148, 163, 184), font=get_font(FONT_REGULAR, 14))
    draw.text((rx + 36, sy + 235), 'ನಮಸ್ಕಾರ! ಎಲ್ಲವೂ ಸರಿಯಾಗಿದೆ.', fill=(236, 72, 153), font=get_font(FONT_BOLD, 17))

    # Right Container 3: Telemetry & Model Diagnostics
    dy = sy + 300
    draw.rounded_rectangle([rx, dy, rx + rw, dy + 185], radius=18, fill=(19, 26, 44, 220), outline=(255, 255, 255, 30), width=1)
    draw.text((rx + 24, dy + 22), "📊 Real-Time Model Telemetry", fill=(255, 255, 255), font=get_font(FONT_BOLD, 18))

    t_metrics = [
        ("FINGER STATE", "[1, 1, 1, 1]", (6, 182, 212)),
        ("WRIST VELOCITY", "0.042 (Wave)", (139, 92, 246)),
        ("PIPELINE LATENCY", "42ms (Total)", (16, 185, 129))
    ]

    tx_start = rx + 24
    card_w = (rw - 68) // 3
    for label, val, color in t_metrics:
        draw.rounded_rectangle([tx_start, dy + 65, tx_start + card_w, dy + 155], radius=10, fill=(12, 18, 32, 230), outline=(255, 255, 255, 20), width=1)
        draw.text((tx_start + 16, dy + 82), label, fill=(100, 116, 139), font=get_font(FONT_BOLD, 11))
        draw.text((tx_start + 16, dy + 112), val, fill=color, font=get_font(FONT_BOLD, 16))
        tx_start += card_w + 10

    img.save("assets/dashboard_screenshot.png", "PNG")
    print("[Asset] dashboard_screenshot.png created successfully.")

# -------------------------------------------------------------
# 4. GESTURE MATRIX (assets/gesture_matrix.png - 1200x700)
# -------------------------------------------------------------
def create_gesture_matrix():
    width, height = 1200, 700
    img = Image.new("RGBA", (width, height), (10, 14, 25, 255))
    draw = ImageDraw.Draw(img)

    # Ambient gradient
    for y in range(height):
        ratio = y / height
        draw.line([(0, y), (width, y)], fill=(int(10 + 8 * ratio), int(14 + 10 * ratio), int(25 + 20 * ratio), 255))

    # Header
    draw.text((50, 40), "Sign2Voice - Gesture Vocabulary Matrix", fill=(255, 255, 255), font=get_font(FONT_BOLD, 30))
    draw.text((50, 85), "Pre-trained geometric decision rules tuned for high-speed CPU recognition", fill=(148, 163, 184), font=get_font(FONT_REGULAR, 15))

    gestures = [
        ("Hello", "👋", "All 4 fingers open + wrist motion velocity > 0.015"),
        ("Yes", "👍", "Fist with thumb vertically extended upwards"),
        ("No", "👎", "Fist with thumb vertically pointing downwards"),
        ("Victory", "✌️", "Index and middle fingers extended (V-shape)"),
        ("I Love You", "🤟", "Thumb, index finger, and pinky extended (ASL ILY)"),
        ("Help", "🤙", "Thumb and pinky extended (Emergency / Shaka sign)"),
        ("1", "☝️", "Only index finger extended vertically"),
        ("2", "✌️", "Index and middle fingers extended"),
        ("3", "🤟", "Thumb, index, and middle fingers open"),
        ("4", "🖖", "Four fingers open with thumb tucked into palm"),
        ("5", "✋", "All 5 fingers open with static zero-motion hand"),
        ("L", "🇱", "Index finger and thumb forming perpendicular 90 deg L"),
    ]

    gx, gy = 50, 135
    cols = 3
    card_w = 345
    card_h = 120

    for idx, (name, icon, rule) in enumerate(gestures):
        col_idx = idx % cols
        row_idx = idx // cols

        x = gx + col_idx * (card_w + 18)
        y = gy + row_idx * (card_h + 16)

        draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=12, fill=(20, 28, 48, 230), outline=(99, 102, 241, 60), width=1)
        draw.text((x + 18, y + 18), icon, font=get_font(FONT_REGULAR, 26))
        draw.text((x + 65, y + 22), name, fill=(255, 255, 255), font=get_font(FONT_BOLD, 17))
        draw.text((x + 18, y + 68), rule, fill=(148, 163, 184), font=get_font(FONT_REGULAR, 12))

    img.save("assets/gesture_matrix.png", "PNG")
    print("[Asset] gesture_matrix.png created successfully.")

if __name__ == "__main__":
    create_banner()
    create_architecture()
    create_dashboard_mockup()
    create_gesture_matrix()
    print(">>> All 4 visual assets generated successfully! <<<")
