const promptField = document.getElementById("prompt");
const button = document.getElementById("generate");
const storyboardList = document.getElementById("storyboard");
const errorField = document.getElementById("error");
const canvas = document.getElementById("preview");
const ctx = canvas.getContext("2d");

let plan = null;
let animationStart = null;

async function generatePlan() {
  errorField.textContent = "";
  storyboardList.innerHTML = "";
  button.disabled = true;
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
  if (!plan) {
    requestAnimationFrame(drawFrame);
    return;
  }
  const totalDuration = 120000; // ms for 2 minutes
  const elapsed = (timestamp - animationStart) % totalDuration;
  const segmentDuration = 6000;
  const index = Math.floor(elapsed / segmentDuration);
  const segment = plan.render_segments[index];
  if (!segment) {
    requestAnimationFrame(drawFrame);
    return;
  }
  const palette = segment.palette;
  const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  gradient.addColorStop(0, `rgb(${palette.red}, ${palette.green}, ${palette.blue})`);
  gradient.addColorStop(1, `rgb(${palette.accent}, ${palette.blue}, ${palette.red})`);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
  ctx.fillRect(20, canvas.height - 120, canvas.width - 40, 100);
  ctx.fillStyle = "#e2e8f0";
  ctx.font = "20px system-ui";
  ctx.fillText(`Segment ${segment.index + 1} / ${plan.render_segments.length}`, 40, canvas.height - 90);
  wrapText(segment.caption, 40, canvas.height - 60, canvas.width - 80, 22);

  requestAnimationFrame(drawFrame);
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
requestAnimationFrame(drawFrame);
