/**
 * Sign2Voice - Frontend Client Controller
 * Handles live webcam streaming, canvas landmark rendering, real-time API pipeline,
 * Edge-TTS audio playback, and sentence synthesis.
 */

// State Management
const state = {
  streaming: false,
  stream: null,
  fps: 5,
  timerId: null,
  isProcessing: false,
  selectedLanguage: "English",
  tokens: [],
  autoSpeak: true,
  lastSpokenText: "",
  audioCooldown: false,
  currentAudioUrl: ""
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
const btnAddToken = document.getElementById("btn-add-token");
const btnSynthesize = document.getElementById("btn-synthesize");
const btnClearTokens = document.getElementById("btn-clear-tokens");
const btnPlayAudio = document.getElementById("btn-play-audio");
const btnPlaySentenceAudio = document.getElementById("btn-play-sentence-audio");
const btnGuide = document.getElementById("btn-guide");
const btnCloseGuide = document.getElementById("btn-close-guide");
const modalGuide = document.getElementById("modal-guide");
const guideGrid = document.getElementById("guide-grid");

// Audio Elements
const audioPlayer = new Audio();
let sentenceAudioUrl = "";

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

  btnAddToken?.addEventListener("click", () => {
    const currentSign = document.getElementById("live-sign-name")?.textContent;
    if (currentSign && !["No Hand", "Unknown", "Ready"].includes(currentSign)) {
      addToken(currentSign);
    }
  });

  btnSynthesize?.addEventListener("click", synthesizeSentence);
  btnClearTokens?.addEventListener("click", clearTokens);

  btnPlayAudio?.addEventListener("click", () => {
    if (state.currentAudioUrl) {
      playAudio(state.currentAudioUrl);
    }
  });

  btnPlaySentenceAudio?.addEventListener("click", () => {
    if (sentenceAudioUrl) {
      playAudio(sentenceAudioUrl);
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

  // Audio Playback Events
  audioPlayer.addEventListener("play", () => setAudioVisualizer(true));
  audioPlayer.addEventListener("ended", () => setAudioVisualizer(false));
  audioPlayer.addEventListener("error", () => setAudioVisualizer(false));
}

// Media & Camera Pipeline
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
    updateStatus("Camera Active ● Scanning");

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

// Frame Capture & API Invocation
async function captureAndProcessFrame() {
  if (!state.streaming || state.isProcessing || !webcam.videoWidth) return;

  state.isProcessing = true;
  const startTime = performance.now();

  try {
    // Render frame to offscreen canvas
    const offscreen = document.createElement("canvas");
    offscreen.width = webcam.videoWidth;
    offscreen.height = webcam.videoHeight;
    const offCtx = offscreen.getContext("2d");
    offCtx.drawImage(webcam, 0, 0, offscreen.width, offscreen.height);

    // Convert to Blob
    const blob = await new Promise((resolve) => offscreen.toBlob(resolve, "image/jpeg", 0.75));
    if (!blob) return;

    // Build FormData
    const formData = new FormData();
    formData.append("image", blob, "frame.jpg");
    formData.append("target_language", state.selectedLanguage);

    const response = await fetch("/process_frame", {
      method: "POST",
      body: formData
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();

    const latency = Math.round(performance.now() - startTime);
    renderResults(data, latency);
  } catch (err) {
    console.warn("Frame processing glitch:", err);
  } finally {
    state.isProcessing = false;
  }
}

// Render Results & Overlay
function renderResults(data, latencyMs) {
  const { sign_text, translated_text, audio_url, debug_info } = data;

  // Latency telemetry
  const elLatency = document.getElementById("telemetry-latency");
  if (elLatency) elLatency.textContent = `${latencyMs}ms`;

  // Draw Landmarks if present
  if (debug_info && debug_info.landmarks && debug_info.landmarks.length > 0) {
    drawHandLandmarks(debug_info.landmarks);
  } else {
    clearCanvas();
  }

  // Update Gesture Text & Emoji
  const elSign = document.getElementById("live-sign-name");
  const elIcon = document.getElementById("live-sign-icon");
  const elDebug = document.getElementById("live-debug-info");

  if (elSign) elSign.textContent = sign_text || "Ready";
  if (elIcon) elIcon.textContent = getSignEmoji(sign_text);
  if (elDebug) elDebug.textContent = (debug_info && debug_info.text) || "Detecting...";

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

  // Translated output
  const elTrans = document.getElementById("live-translated-text");
  if (elTrans) {
    elTrans.textContent = translated_text || "...";
  }

  // Play Audio if new and valid
  if (
    audio_url &&
    sign_text &&
    !["No Hand Detected", "Unknown Sign"].includes(sign_text) &&
    state.autoSpeak &&
    sign_text !== state.lastSpokenText &&
    !state.audioCooldown
  ) {
    state.lastSpokenText = sign_text;
    state.currentAudioUrl = audio_url;
    playAudio(audio_url);

    // Audio cooldown (prevents rapid repetitive firing)
    state.audioCooldown = true;
    setTimeout(() => {
      state.audioCooldown = false;
    }, 1800);
  } else if (audio_url) {
    state.currentAudioUrl = audio_url;
  }
}

// Landmark Drawing Routine
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

  // Draw connections
  ctx.lineWidth = 2.5;
  ctx.strokeStyle = "rgba(6, 182, 212, 0.85)"; // Neon Cyan
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

  // Draw joints
  ctx.shadowBlur = 10;
  for (let i = 0; i < landmarks.length; i++) {
    const pt = landmarks[i];
    const x = pt.x * w;
    const y = pt.y * h;

    ctx.beginPath();
    ctx.arc(x, y, i === 4 || i === 8 || i === 12 || i === 16 || i === 20 ? 5 : 3.5, 0, 2 * Math.PI);
    ctx.fillStyle = i % 4 === 0 ? "#ec4899" : "#a855f7"; // Neon Pink/Purple joints
    ctx.shadowColor = "#ec4899";
    ctx.fill();
  }
}

function clearCanvas() {
  if (ctx && canvas) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
}

// Token & Sentence Builder
function addToken(sign) {
  if (!sign || ["No Hand Detected", "Unknown Sign", "Ready"].includes(sign)) return;
  state.tokens.push(sign);
  renderTokens();
}

function removeToken(index) {
  state.tokens.splice(index, 1);
  renderTokens();
}

function clearTokens() {
  state.tokens = [];
  renderTokens();
  const elOriginal = document.getElementById("sentence-original-text");
  const elTrans = document.getElementById("sentence-translated-text");
  if (elOriginal) elOriginal.textContent = "Tokens cleared.";
  if (elTrans) elTrans.textContent = "...";
  sentenceAudioUrl = "";
}

function renderTokens() {
  const container = document.getElementById("token-container");
  if (!container) return;

  if (state.tokens.length === 0) {
    container.innerHTML = '<span class="token-placeholder">Detected tokens will appear here (e.g. Hello, Yes)...</span>';
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

async function synthesizeSentence() {
  if (state.tokens.length === 0) {
    alert("Please add at least one sign token to form a sentence.");
    return;
  }

  try {
    const response = await fetch("/process_sentence", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tokens: state.tokens,
        target_language: state.selectedLanguage
      })
    });

    if (!response.ok) throw new Error("Sentence generation failed.");
    const data = await response.json();

    const elOriginal = document.getElementById("sentence-original-text");
    const elTrans = document.getElementById("sentence-translated-text");

    if (elOriginal) elOriginal.textContent = `"${data.original}"`;
    if (elTrans) elTrans.textContent = data.translated;

    if (data.audio_url) {
      sentenceAudioUrl = data.audio_url;
      playAudio(data.audio_url);
    }
  } catch (err) {
    console.error("Sentence synthesis error:", err);
  }
}

// Audio Player & Visualizer
function playAudio(url) {
  if (!url) return;
  audioPlayer.src = url;
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

// Helpers
function getSignEmoji(sign) {
  const map = {
    Hello: "👋",
    Yes: "👍",
    No: "👎",
    Victory: "✌️",
    "2": "✌️",
    "1": "☝️",
    "3": "🤟",
    "4": "🖖",
    "5": "✋",
    "I Love You": "🤟",
    Help: "🤙",
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
    const res = await fetch("/api/supported");
    if (!res.ok) return;
    const data = await res.json();

    // Populate Guide
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
