/* ── State ─────────────────────────────────────────────────────────── */
const state = {
  images: [],           // ordered list of filenames
  transition: "fade",
  music: "",
  duration_per_image: 3.5,
  transition_duration: 1.0,
  resolution: "1920x1080",
  crf: 18,
  preset: "slow",
  fps: 30,
};

/* ── DOM refs ─────────────────────────────────────────────────────── */
const $ = (s) => document.querySelector(s);
const dropZone      = $("#drop-zone");
const fileInput     = $("#file-input");
const imageList     = $("#image-list");
const imageCount    = $("#image-count");
const btnClear      = $("#btn-clear");
const btnGenerate   = $("#btn-generate");
const progress      = $("#progress");
const progressText  = $("#progress-text");
const btnDownload   = $("#btn-download");
const estDuration   = $("#est-duration");
const videoPreview  = $("#video-preview");
const previewPlaceholder = $("#preview-placeholder");
const transitionGrid = $("#transition-grid");
const musicSelect   = $("#music-select");

/* ── Init ─────────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  loadExistingImages();
  loadTransitions();
  loadMusic();
  bindSettings();
  bindUpload();
  bindGenerate();
  bindClear();
});

/* ── Upload ───────────────────────────────────────────────────────── */
function bindUpload() {
  dropZone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", () => { uploadFiles(fileInput.files); fileInput.value = ""; });

  dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    uploadFiles(e.dataTransfer.files);
  });
}

async function uploadFiles(fileList) {
  const form = new FormData();
  for (const f of fileList) form.append("files", f);
  const res = await fetch("/api/upload", { method: "POST", body: form });
  const data = await res.json();
  if (data.images) {
    state.images.push(...data.images);
    renderImages();
    updateUI();
  }
}

async function loadExistingImages() {
  const res = await fetch("/api/images");
  const data = await res.json();
  state.images = data.images || [];
  renderImages();
  updateUI();
}

/* ── Image List (drag-reorder) ────────────────────────────────────── */
let dragIdx = null;

function renderImages() {
  imageList.innerHTML = "";
  state.images.forEach((name, i) => {
    const li = document.createElement("li");
    li.draggable = true;
    li.dataset.index = i;
    li.innerHTML = `
      <span class="drag-handle">&#9776;</span>
      <img src="/api/images/${encodeURIComponent(name)}" alt="">
      <span class="name" title="${name}">${displayName(name)}</span>
      <button class="btn-remove" data-name="${name}">&times;</button>
    `;
    li.addEventListener("dragstart", onDragStart);
    li.addEventListener("dragover", onDragOver);
    li.addEventListener("drop", onDrop);
    li.addEventListener("dragend", onDragEnd);
    li.querySelector(".btn-remove").addEventListener("click", () => removeImage(name));
    imageList.appendChild(li);
  });
  imageCount.textContent = `${state.images.length} image${state.images.length !== 1 ? "s" : ""}`;
}

function displayName(name) {
  // Strip the uuid prefix we added on upload
  return name.replace(/^[a-f0-9]{8}_/, "");
}

function onDragStart(e) {
  dragIdx = +e.currentTarget.dataset.index;
  e.currentTarget.classList.add("dragging");
}
function onDragOver(e) { e.preventDefault(); }
function onDrop(e) {
  e.preventDefault();
  const targetIdx = +e.currentTarget.dataset.index;
  if (dragIdx === null || dragIdx === targetIdx) return;
  const [moved] = state.images.splice(dragIdx, 1);
  state.images.splice(targetIdx, 0, moved);
  renderImages();
  updateUI();
}
function onDragEnd(e) { e.currentTarget.classList.remove("dragging"); dragIdx = null; }

async function removeImage(name) {
  await fetch(`/api/images/${encodeURIComponent(name)}`, { method: "DELETE" });
  state.images = state.images.filter((n) => n !== name);
  renderImages();
  updateUI();
}

/* ── Clear All ────────────────────────────────────────────────────── */
function bindClear() {
  btnClear.addEventListener("click", async () => {
    await fetch("/api/images/clear", { method: "POST" });
    state.images = [];
    renderImages();
    updateUI();
  });
}

/* ── Transitions ──────────────────────────────────────────────────── */
async function loadTransitions() {
  const res = await fetch("/api/transitions");
  const data = await res.json();
  transitionGrid.innerHTML = "";
  for (const [cat, items] of Object.entries(data.categories)) {
    const label = document.createElement("div");
    label.className = "cat-label";
    label.textContent = cat;
    transitionGrid.appendChild(label);

    const group = document.createElement("div");
    group.className = "cat-group";
    items.forEach((t) => {
      const btn = document.createElement("div");
      btn.className = "t-btn" + (t === state.transition ? " selected" : "");
      btn.textContent = t;
      btn.addEventListener("click", () => selectTransition(t));
      group.appendChild(btn);
    });
    transitionGrid.appendChild(group);
  }
}

function selectTransition(t) {
  state.transition = t;
  transitionGrid.querySelectorAll(".t-btn").forEach((b) => {
    b.classList.toggle("selected", b.textContent === t);
  });
}

/* ── Music ────────────────────────────────────────────────────────── */
async function loadMusic() {
  const res = await fetch("/api/music");
  const data = await res.json();
  (data.music || []).forEach((name) => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    musicSelect.appendChild(opt);
  });
  // Auto-select first music file if available
  if (data.music && data.music.length > 0) {
    musicSelect.value = data.music[0];
    state.music = data.music[0];
  }
  musicSelect.addEventListener("change", () => { state.music = musicSelect.value; });
}

/* ── Settings Bindings ────────────────────────────────────────────── */
function bindSettings() {
  bindSlider("set-duration", "val-duration", "duration_per_image", (v) => v + "s");
  bindSlider("set-transition-dur", "val-transition-dur", "transition_duration", (v) => v + "s");
  bindSlider("set-crf", "val-crf", "crf", (v) => v);

  bindSelect("set-resolution", "resolution");
  bindSelect("set-preset", "preset");
  bindSelect("set-fps", "fps");
}

function bindSlider(inputId, labelId, key, fmt) {
  const input = document.getElementById(inputId);
  const label = document.getElementById(labelId);
  input.addEventListener("input", () => {
    const v = parseFloat(input.value);
    state[key] = v;
    label.textContent = fmt(v);
    updateUI();
  });
}

function bindSelect(selectId, key) {
  const el = document.getElementById(selectId);
  el.addEventListener("change", () => {
    state[key] = el.value;
    updateUI();
  });
}

/* ── Generate ─────────────────────────────────────────────────────── */
function bindGenerate() {
  btnGenerate.addEventListener("click", startGeneration);
}

async function startGeneration() {
  // Validate
  if (state.transition_duration >= state.duration_per_image) {
    showError("Transition duration must be less than duration per image.");
    return;
  }

  btnGenerate.disabled = true;
  progress.classList.remove("hidden");
  progressText.textContent = "Starting...";
  btnDownload.classList.add("hidden");
  videoPreview.classList.remove("visible");
  previewPlaceholder.style.display = "flex";

  const body = {
    images: state.images,
    transition: state.transition,
    music: state.music,
    duration_per_image: state.duration_per_image,
    transition_duration: state.transition_duration,
    resolution: state.resolution,
    crf: state.crf,
    preset: state.preset,
    fps: state.fps,
  };

  const res = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (data.error) {
    showError(data.error);
    btnGenerate.disabled = false;
    progress.classList.add("hidden");
    return;
  }

  pollJob(data.job_id);
}

function pollJob(jobId) {
  progressText.textContent = "Generating video...";
  const interval = setInterval(async () => {
    const res = await fetch(`/api/jobs/${jobId}`);
    const data = await res.json();

    if (data.status === "done") {
      clearInterval(interval);
      progress.classList.add("hidden");
      btnGenerate.disabled = false;

      const url = `/api/download/${jobId}`;
      videoPreview.src = url;
      videoPreview.classList.add("visible");
      previewPlaceholder.style.display = "none";

      btnDownload.href = url;
      btnDownload.classList.remove("hidden");
    } else if (data.status === "error") {
      clearInterval(interval);
      progress.classList.add("hidden");
      btnGenerate.disabled = false;
      showError(data.error || "Generation failed.");
    }
  }, 1000);
}

/* ── UI helpers ───────────────────────────────────────────────────── */
function updateUI() {
  const n = state.images.length;
  btnGenerate.disabled = n < 2;
  if (n >= 2) {
    const dur = (n * state.duration_per_image) - ((n - 1) * state.transition_duration);
    estDuration.textContent = dur.toFixed(1) + "s";
  } else {
    estDuration.textContent = "--";
  }
}

function showError(msg) {
  const el = document.createElement("div");
  el.className = "error-toast";
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}
