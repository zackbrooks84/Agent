const promptField = document.getElementById("prompt");
const button = document.getElementById("generate");
const renderButton = document.getElementById("render");
const renderStatus = document.getElementById("render-status");
const storyboardList = document.getElementById("storyboard");
const errorField = document.getElementById("error");
const canvas = document.getElementById("preview");
const ctx = canvas.getContext("2d");

const TOTAL_DURATION_MS = 120000;
const SEGMENT_DURATION_MS = 6000;
const FPS = 30;
const FRAME_INTERVAL_MS = 1000 / FPS;
const FRAMES_PER_SEGMENT = Math.round(SEGMENT_DURATION_MS / FRAME_INTERVAL_MS);

let plan = null;
let animationStart = null;
let isRenderingVideo = false;

async function generatePlan() {
  errorField.textContent = "";
  storyboardList.innerHTML = "";
  button.disabled = true;
  renderButton.disabled = true;
  renderStatus.textContent = "";
  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: promptField.value })
    });
    if (!response.ok) {
      const payload = await response.json();
      throw new Error(payload.error || "Failed to generate plan");
    }
    plan = await response.json();
    animationStart = performance.now();
    populateStoryboard(plan.storyboard);
    renderButton.disabled = false;
  } catch (error) {
    errorField.textContent = error.message;
    plan = null;
  } finally {
    button.disabled = false;
  }
}

function populateStoryboard(storyboard) {
  storyboard.forEach((segment) => {
    const item = document.createElement("li");
    item.innerHTML = `<strong>${segment.title}</strong><br />${segment.description}`;
    storyboardList.appendChild(item);
  });
}

function drawFrame(timestamp) {
  ctx.fillStyle = "#020617";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  if (!plan || isRenderingVideo) {
    requestAnimationFrame(drawFrame);
    return;
  }
  if (animationStart === null) {
    animationStart = timestamp;
  }
  const elapsed = (timestamp - animationStart) % TOTAL_DURATION_MS;
  const index = Math.floor(elapsed / SEGMENT_DURATION_MS);
  const segment = plan.render_segments[index];
  const segmentElapsed = elapsed - index * SEGMENT_DURATION_MS;
  const progress = Math.max(0, Math.min(1, segmentElapsed / SEGMENT_DURATION_MS));
  drawSegmentFrame(segment, progress);
  requestAnimationFrame(drawFrame);
}

function drawSegmentFrame(segment, progress) {
  if (!segment) {
    return;
  }
  ctx.fillStyle = "#020617";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  const palette = segment.palette;
  const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  const drift = Math.sin(progress * Math.PI);
  const offsetX = canvas.width * 0.02 * drift;
  const offsetY = canvas.height * 0.02 * drift;
  gradient.addColorStop(0, `rgb(${palette.red}, ${palette.green}, ${palette.blue})`);
  gradient.addColorStop(1, `rgb(${palette.accent}, ${palette.blue}, ${palette.red})`);
  ctx.save();
  ctx.translate(offsetX, offsetY);
  ctx.fillStyle = gradient;
  ctx.fillRect(-offsetX, -offsetY, canvas.width, canvas.height);
  ctx.restore();

  ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
  ctx.fillRect(20, canvas.height - 120, canvas.width - 40, 100);
  ctx.fillStyle = "#e2e8f0";
  ctx.font = "20px system-ui";
  ctx.fillText(`Segment ${segment.index + 1} / ${plan.render_segments.length}`, 40, canvas.height - 90);
  wrapText(segment.caption, 40, canvas.height - 60, canvas.width - 80, 22);
}

function wrapText(text, x, y, maxWidth, lineHeight) {
  const words = text.split(" ");
  let line = "";
  words.forEach((word) => {
    const testLine = `${line}${word} `;
    const metrics = ctx.measureText(testLine);
    if (metrics.width > maxWidth && line !== "") {
      ctx.fillText(line, x, y);
      line = `${word} `;
      y += lineHeight;
    } else {
      line = testLine;
    }
  });
  ctx.fillText(line.trim(), x, y);
}

button.addEventListener("click", generatePlan);
renderButton.addEventListener("click", renderVideo);
requestAnimationFrame(drawFrame);

function selectMediaRecorder(stream) {
  const mimeTypes = [
    "video/webm;codecs=vp9",
    "video/webm;codecs=vp8",
    "video/webm"
  ];
  if (typeof MediaRecorder === "undefined") {
    throw new Error("MediaRecorder API is unavailable in this browser");
  }
  for (const mimeType of mimeTypes) {
    if (!MediaRecorder.isTypeSupported || MediaRecorder.isTypeSupported(mimeType)) {
      try {
        return new MediaRecorder(stream, { mimeType });
      } catch (error) {
        continue;
      }
    }
  }
  return new MediaRecorder(stream);
}

async function renderVideo() {
  if (!plan) {
    renderStatus.textContent = "Generate a plan before exporting the video.";
    return;
  }
  if (!canvas.captureStream) {
    renderStatus.textContent = "Canvas captureStream is unavailable in this browser.";
    return;
  }
  if (isRenderingVideo) {
    renderStatus.textContent = "Rendering already in progress.";
    return;
  }

  isRenderingVideo = true;
  renderButton.disabled = true;
  renderStatus.textContent = "Rendering deterministic WebM...";
  animationStart = performance.now();

  let stream = null;
  let track = null;
  let stopRecording = () => {};

  try {
    stream = canvas.captureStream(0);
    track = stream.getVideoTracks()[0] || null;
    let manualFrameSupport = Boolean(track && typeof track.requestFrame === "function");
    if (!manualFrameSupport && track) {
      track.stop();
    }
    if (!manualFrameSupport) {
      stream = canvas.captureStream(FPS);
      track = stream.getVideoTracks()[0] || null;
    }
    if (!track) {
      throw new Error("Unable to access a video track for capture.");
    }

    const recorder = selectMediaRecorder(stream);
    const chunks = [];
    let stopCalled = false;

    const recordingPromise = new Promise((resolve, reject) => {
      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      recorder.onerror = (event) => {
        stopCalled = true;
        recorder.stop();
        reject(new Error(`Recording failed: ${event.error?.message || "unknown error"}`));
      };
      recorder.onstop = () => {
        if (!chunks.length) {
          reject(new Error("No video data was captured."));
          return;
        }
        resolve(new Blob(chunks, { type: recorder.mimeType || "video/webm" }));
      };
    });

    stopRecording = () => {
      if (!stopCalled) {
        stopCalled = true;
        recorder.stop();
      }
    };

    recorder.start();

    if (manualFrameSupport && track) {
      await renderWithManualFrames(track);
    } else {
      await renderWithTimedFrames();
    }

    stopRecording();
    const blob = await recordingPromise;
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "aal-deterministic-video.webm";
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
    renderStatus.textContent = "Download ready: aal-deterministic-video.webm";
  } catch (error) {
    stopRecording();
    renderStatus.textContent = error.message;
  } finally {
    if (track) {
      track.stop();
    }
    renderButton.disabled = false;
    animationStart = performance.now();
    isRenderingVideo = false;
  }
}

async function renderWithManualFrames(track) {
  const totalSegments = plan.render_segments.length;
  const totalFrames = totalSegments * FRAMES_PER_SEGMENT;
  let renderedFrames = 0;
  updateRenderStatus(0, totalFrames);

  for (const segment of plan.render_segments) {
    for (let frameIndex = 0; frameIndex < FRAMES_PER_SEGMENT; frameIndex += 1) {
      const progress = frameIndex / FRAMES_PER_SEGMENT;
      drawSegmentFrame(segment, progress);
      track.requestFrame();
      renderedFrames += 1;
      if (renderedFrames % FPS === 0) {
        updateRenderStatus(renderedFrames, totalFrames);
        await yieldToBrowser();
      }
    }
  }
  drawSegmentFrame(plan.render_segments[plan.render_segments.length - 1], 1);
  track.requestFrame();
  updateRenderStatus(totalFrames, totalFrames);
}

async function renderWithTimedFrames() {
  const totalSegments = plan.render_segments.length;
  const totalFrames = totalSegments * FRAMES_PER_SEGMENT;
  let renderedFrames = 0;
  updateRenderStatus(0, totalFrames);

  for (const segment of plan.render_segments) {
    for (let frameIndex = 0; frameIndex < FRAMES_PER_SEGMENT; frameIndex += 1) {
      const progress = frameIndex / FRAMES_PER_SEGMENT;
      drawSegmentFrame(segment, progress);
      renderedFrames += 1;
      if (renderedFrames % FPS === 0) {
        updateRenderStatus(renderedFrames, totalFrames);
      }
      await waitForInterval(FRAME_INTERVAL_MS);
    }
  }
  drawSegmentFrame(plan.render_segments[plan.render_segments.length - 1], 1);
  updateRenderStatus(totalFrames, totalFrames);
}

function updateRenderStatus(progress, total) {
  const safeTotal = Math.max(total, 1);
  const percentage = Math.min(100, Math.round((progress / safeTotal) * 100));
  renderStatus.textContent = `Rendering deterministic WebM... ${percentage}%`;
}

function yieldToBrowser() {
  return new Promise((resolve) => {
    window.requestAnimationFrame(() => resolve());
  });
}

function waitForInterval(durationMs) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, Math.max(1, Math.round(durationMs)));
  });
}
