/**
 * Sign2Voice - Frontend Client Controller
 * 
 * Hands-Free Automatic Pipeline:
 * 1. Automatically appends words as you sign and hold gestures (~0.8s stability).
 * 2. Words are NOT spoken individually (prevents repetitive stutter).
 * 3. Waits for the user to finish all gestures.
 * 4. When hands lower/pause (~1.2s), it automatically formulates, translates,
 *    and speaks the complete final sentence via Edge-TTS!
 */

// State Management
const state = {
  streaming: false,
  stream: null,
  fps: 5,
  timerId: null,
  isProcessing: false,
  selectedLanguage: "English",

  // Automatic Gesture Appending Engine
  tokens: [],
  candidateSign: null,
  candidateStreak: 0,
  REQUIRED_STREAK: 4, // 4 consecutive frames (~0.8s) to lock in a word

  // Automatic Sentence Completion Trigger
  noHandFrames: 0,
  NO_HAND_TRIGGER_FRAMES: 6, // ~1.2s of hand lowered triggers speech
  isSynthesizingSentence: false,

  // Audio State
  lastSentenceAudioUrl: ""
};

// DOM Elements
const webcam = document.getElementById("webcam");
const canvas = document.getElementById("landmark-canvas");
const ctx = canvas ? canvas.getContext("2d") : null;
const btnStartCam = document.getElementById("btn-start-cam");
const btnStopCam = document.getElementById("btn-stop-cam");
const btnFlipCam = document.getElementById("btn-flip-cam");
const fpsSelect = document.getElementById("fps-select");
const langSelect = document.getElementById("lang-select");
const btnClearTokens = document.getElementById("btn-clear-tokens");
const btnPlaySentenceAudio = document.getElementById("btn-play-sentence-audio");
const btnGuide = document.getElementById("btn-guide");
const btnCloseGuide = document.getElementById("btn-close-guide");
const modalGuide = document.getElementById("modal-guide");
const guideGrid = document.getElementById("guide-grid");
const gestureHoldProgress = document.getElementById("gesture-hold-progress");
const autoStatusIndicator = document.getElementById("auto-status-indicator");

// Audio Element
const audioPlayer = new Audio();

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  loadSupportedData();
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);
});

function resizeCanvas() {
  if (canvas && webcam) {
    canvas.width = webcam.clientWidth || 640;
    canvas.height = webcam.clientHeight || 480;
  }
}

function setupEventListeners() {
  btnStartCam?.addEventListener("click", startCamera);
  btnStopCam?.addEventListener("click", stopCamera);
  btnFlipCam?.addEventListener("click", flipCamera);

  fpsSelect?.addEventListener("change", (e) => {
    state.fps = parseInt(e.target.value, 10) || 5;
    if (state.streaming) {
      restartLoop();
    }
  });

  langSelect?.addEventListener("change", (e) => {
    state.selectedLanguage = e.target.value;
    updateStatus(`Target language set to ${state.selectedLanguage}`);
  });

  btnClearTokens?.addEventListener("click", resetSentenceBuffer);

  btnPlaySentenceAudio?.addEventListener("click", () => {
    if (state.lastSentenceAudioUrl) {
      playAudio(state.lastSentenceAudioUrl);
    }
  });

  btnGuide?.addEventListener("click", () => {
    if (modalGuide) modalGuide.style.display = "flex";
  });

  btnCloseGuide?.addEventListener("click", () => {
    if (modalGuide) modalGuide.style.display = "none";
  });

  window.addEventListener("click", (e) => {
    if (e.target === modalGuide) {
      modalGuide.style.display = "none";
    }
  });

  // Audio Visualizer Hooks
  audioPlayer.addEventListener("play", () => setAudioVisualizer(true));
  audioPlayer.addEventListener("ended", () => setAudioVisualizer(false));
  audioPlayer.addEventListener("error", () => setAudioVisualizer(false));
}

// Camera Pipeline
let currentFacingMode = "user";

async function startCamera() {
  try {
    const constraints = {
      video: {
        facingMode: currentFacingMode,
        width: { ideal: 640 },
        height: { ideal: 480 }
      },
      audio: false
    };

    state.stream = await navigator.mediaDevices.getUserMedia(constraints);
    webcam.srcObject = state.stream;
    await webcam.play();

    state.streaming = true;
    resizeCanvas();
    updateStatus("Camera Active ● Signing Mode");

    btnStartCam.style.display = "none";
    btnStopCam.style.display = "inline-flex";

    restartLoop();
  } catch (err) {
    console.error("Camera access error:", err);
    alert(`Could not start camera: ${err.message}. Please check webcam permissions.`);
  }
}

function stopCamera() {
  state.streaming = false;
  if (state.timerId) {
    clearInterval(state.timerId);
    state.timerId = null;
  }

  if (state.stream) {
    state.stream.getTracks().forEach((track) => track.stop());
    state.stream = null;
  }

  webcam.srcObject = null;
  clearCanvas();
  updateStatus("Camera Paused");

  btnStartCam.style.display = "inline-flex";
  btnStopCam.style.display = "none";
}

function flipCamera() {
  currentFacingMode = currentFacingMode === "user" ? "environment" : "user";
  if (state.streaming) {
    stopCamera();
    startCamera();
  }
}

function restartLoop() {
  if (state.timerId) clearInterval(state.timerId);
  const intervalMs = Math.round(1000 / state.fps);
  state.timerId = setInterval(captureAndProcessFrame, intervalMs);
}

// Frame Capture Loop
async function captureAndProcessFrame() {
  if (!state.streaming || state.isProcessing || !webcam.videoWidth || state.isSynthesizingSentence) {
    return;
  }

  state.isProcessing = true;
  const startTime = performance.now();

  try {
    const offscreen = document.createElement("canvas");
    offscreen.width = webcam.videoWidth;
    offscreen.height = webcam.videoHeight;
    const offCtx = offscreen.getContext("2d");
    offCtx.drawImage(webcam, 0, 0, offscreen.width, offscreen.height);

    const blob = await new Promise((resolve) => offscreen.toBlob(resolve, "image/jpeg", 0.75));
    if (!blob) return;

    const formData = new FormData();
    formData.append("image", blob, "frame.jpg");
    formData.append("target_language", state.selectedLanguage);

    const response = await fetch("process_frame", {
      method: "POST",
      body: formData
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();

    const latency = Math.round(performance.now() - startTime);
    handleFrameData(data, latency);
  } catch (err) {
    console.warn("Frame processing glitch:", err);
  } finally {
    state.isProcessing = false;
  }
}

// Process Frame Recognition & Automatic Sentence Engine
function handleFrameData(data, latencyMs) {
  const { sign_text, translated_text, debug_info } = data;

  // Latency & Telemetry
  const elLatency = document.getElementById("telemetry-latency");
  if (elLatency) elLatency.textContent = `${latencyMs}ms`;

  // Draw 21 MediaPipe Landmarks
  if (debug_info && debug_info.landmarks && debug_info.landmarks.length > 0) {
    drawHandLandmarks(debug_info.landmarks);
  } else {
    clearCanvas();
  }

  // Update Live Sign Preview
  const elSign = document.getElementById("live-sign-name");
  const elIcon = document.getElementById("live-sign-icon");
  const elDebug = document.getElementById("live-debug-info");
  const elTrans = document.getElementById("live-translated-text");

  if (elSign) elSign.textContent = sign_text || "Scanning...";
  if (elIcon) elIcon.textContent = getSignEmoji(sign_text);
  if (elDebug) elDebug.textContent = (debug_info && debug_info.text) || "Detecting...";
  if (elTrans) elTrans.textContent = translated_text || "...";

  // Telemetry: Fingers & Motion
  if (debug_info) {
    const elFingers = document.getElementById("telemetry-fingers");
    const elMotion = document.getElementById("telemetry-motion");

    if (elFingers && debug_info.fingers) {
      elFingers.textContent = `[${debug_info.fingers.join(", ")}]`;
    }
    if (elMotion && typeof debug_info.motion !== "undefined") {
      elMotion.textContent = `${debug_info.motion}`;
    }
  }

  // --- AUTOMATIC APPEND & AUTO-SPEECH ENGINE ---
  const isValidSign = sign_text && !["No Hand Detected", "Unknown Sign", "Ready"].includes(sign_text) && !sign_text.startsWith("Error");

  if (isValidSign) {
    state.noHandFrames = 0; // Hand is active

    if (sign_text === state.candidateSign) {
      state.candidateStreak++;
      if (gestureHoldProgress) {
        gestureHoldProgress.textContent = `Locking: ${state.candidateStreak}/${state.REQUIRED_STREAK}`;
        gestureHoldProgress.style.color = "#06b6d4";
      }

      // Automatically append gesture once held steadily
      if (state.candidateStreak === state.REQUIRED_STREAK) {
        // Prevent appending the exact same sign consecutively
        const lastToken = state.tokens[state.tokens.length - 1];
        if (lastToken !== sign_text) {
          state.tokens.push(sign_text);
          renderTokens();

          if (autoStatusIndicator) {
            autoStatusIndicator.textContent = `● APPENDED "${sign_text.toUpperCase()}"`;
            autoStatusIndicator.style.color = "#8b5cf6";
          }
        }
      }
    } else {
      state.candidateSign = sign_text;
      state.candidateStreak = 1;
      if (gestureHoldProgress) {
        gestureHoldProgress.textContent = `Hold ~1s to append`;
        gestureHoldProgress.style.color = "var(--text-dim)";
      }
    }
  } else {
    // Hand is absent or transition
    state.candidateSign = null;
    state.candidateStreak = 0;
    if (gestureHoldProgress) {
      gestureHoldProgress.textContent = `Waiting for sign...`;
      gestureHoldProgress.style.color = "var(--text-dim)";
    }

    if (sign_text === "No Hand Detected") {
      state.noHandFrames++;

      // User finished signing and lowered hands -> Automatically speak full sentence!
      if (
        state.noHandFrames >= state.NO_HAND_TRIGGER_FRAMES &&
        state.tokens.length > 0 &&
        !state.isSynthesizingSentence
      ) {
        autoSpeakFinalSentence();
      }
    }
  }
}

// Automatically Synthesize & Speak Full Sentence
async function autoSpeakFinalSentence() {
  if (state.tokens.length === 0 || state.isSynthesizingSentence) return;

  state.isSynthesizingSentence = true;
  const sentenceTokens = [...state.tokens]; // copy tokens

  if (autoStatusIndicator) {
    autoStatusIndicator.textContent = "● SPEAKING FULL SENTENCE...";
    autoStatusIndicator.style.color = "#ec4899";
  }

  try {
    const response = await fetch("process_sentence", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tokens: sentenceTokens,
        target_language: state.selectedLanguage
      })
    });

    if (!response.ok) throw new Error("Sentence synthesis failed.");
    const data = await response.json();

    const elOriginal = document.getElementById("sentence-original-text");
    const elTrans = document.getElementById("sentence-translated-text");

    if (elOriginal) elOriginal.textContent = `"${data.original}"`;
    if (elTrans) elTrans.textContent = data.translated;

    // Automatically speak the final sentence audio
    if (data.audio_url) {
      state.lastSentenceAudioUrl = data.audio_url;
      playAudio(data.audio_url);
    }

    // Clear tokens for the next sentence after speaking
    state.tokens = [];
    renderTokens();

    setTimeout(() => {
      state.isSynthesizingSentence = false;
      state.noHandFrames = 0;
      if (autoStatusIndicator) {
        autoStatusIndicator.textContent = "● AUTO-FLOW READY";
        autoStatusIndicator.style.color = "var(--accent-emerald)";
      }
    }, 2000);

  } catch (err) {
    console.error("Auto sentence error:", err);
    state.isSynthesizingSentence = false;
  }
}

function resetSentenceBuffer() {
  state.tokens = [];
  state.candidateStreak = 0;
  state.noHandFrames = 0;
  renderTokens();

  const elOriginal = document.getElementById("sentence-original-text");
  const elTrans = document.getElementById("sentence-translated-text");
  if (elOriginal) elOriginal.textContent = "Tokens cleared. Start signing gestures in sequence.";
  if (elTrans) elTrans.textContent = "...";

  if (autoStatusIndicator) {
    autoStatusIndicator.textContent = "● BUFFER RESET";
    autoStatusIndicator.style.color = "var(--accent-cyan)";
  }
}

function renderTokens() {
  const container = document.getElementById("token-container");
  if (!container) return;

  if (state.tokens.length === 0) {
    container.innerHTML = '<span class="token-placeholder">Perform gestures steadily to automatically add words here...</span>';
    return;
  }

  container.innerHTML = "";
  state.tokens.forEach((token, idx) => {
    const chip = document.createElement("div");
    chip.className = "token-chip";
    chip.innerHTML = `
      <span>${token}</span>
      <span class="token-chip-remove" onclick="removeToken(${idx})">✕</span>
    `;
    container.appendChild(chip);
  });
}

function removeToken(index) {
  state.tokens.splice(index, 1);
  renderTokens();
}

// MediaPipe Landmark Rendering
const HAND_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],       // Thumb
  [0, 5], [5, 6], [6, 7], [7, 8],       // Index
  [0, 9], [9, 10], [10, 11], [11, 12],  // Middle
  [0, 13], [13, 14], [14, 15], [15, 16],// Ring
  [0, 17], [17, 18], [18, 19], [19, 20],// Pinky
  [5, 9], [9, 13], [13, 17]             // Palm base
];

function drawHandLandmarks(landmarks) {
  if (!ctx || !canvas) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const w = canvas.width;
  const h = canvas.height;

  ctx.lineWidth = 2.5;
  ctx.strokeStyle = "rgba(6, 182, 212, 0.85)";
  ctx.shadowColor = "#06b6d4";
  ctx.shadowBlur = 8;

  for (const [startIdx, endIdx] of HAND_CONNECTIONS) {
    const p1 = landmarks[startIdx];
    const p2 = landmarks[endIdx];
    if (p1 && p2) {
      ctx.beginPath();
      ctx.moveTo(p1.x * w, p1.y * h);
      ctx.lineTo(p2.x * w, p2.y * h);
      ctx.stroke();
    }
  }

  ctx.shadowBlur = 10;
  for (let i = 0; i < landmarks.length; i++) {
    const pt = landmarks[i];
    const x = pt.x * w;
    const y = pt.y * h;

    ctx.beginPath();
    ctx.arc(x, y, i === 4 || i === 8 || i === 12 || i === 16 || i === 20 ? 5 : 3.5, 0, 2 * Math.PI);
    ctx.fillStyle = i % 4 === 0 ? "#ec4899" : "#a855f7";
    ctx.shadowColor = "#ec4899";
    ctx.fill();
  }
}

function clearCanvas() {
  if (ctx && canvas) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
}

// Audio Player & Visualizer
function playAudio(url) {
  if (!url) return;
  const cleanUrl = url.startsWith("/") ? url.slice(1) : url;
  audioPlayer.src = cleanUrl;
  audioPlayer.play().catch((err) => {
    console.warn("Audio autoplay blocked by browser policy:", err);
  });
}

function setAudioVisualizer(isPlaying) {
  const visualizers = document.querySelectorAll(".audio-bars");
  visualizers.forEach((viz) => {
    if (isPlaying) {
      viz.classList.add("audio-playing");
    } else {
      viz.classList.remove("audio-playing");
    }
  });
}

// Gesture Emojis
function getSignEmoji(sign) {
  const map = {
    Hello: "👋",
    Yes: "👍",
    No: "👎",
    "2": "✌️",
    Victory: "✌️",
    "1": "☝️",
    "3": "🤟",
    "4": "🖖",
    "5": "✋",
    "I Love You": "🤟",
    Help: "🤙",
    OK: "👌",
    Rock: "🤘",
    Fist: "✊",
    L: "🇱",
    Y: "🇾"
  };
  return map[sign] || "✨";
}

function updateStatus(text) {
  const statusEl = document.getElementById("system-status-text");
  if (statusEl) statusEl.textContent = text;
}

async function loadSupportedData() {
  try {
    const res = await fetch("api/supported");
    if (!res.ok) return;
    const data = await res.json();

    if (guideGrid && data.signs) {
      guideGrid.innerHTML = data.signs
        .map(
          (s) => `
        <div class="gesture-card">
          <div class="gesture-icon-large">${s.icon}</div>
          <div class="gesture-name">${s.sign}</div>
          <div class="gesture-desc">${s.description}</div>
        </div>
      `
        )
        .join("");
    }
  } catch (err) {
    console.warn("Could not load supported info:", err);
  }
}
