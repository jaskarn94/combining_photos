import os
import uuid
import shutil
import threading
from flask import Flask, request, jsonify, send_from_directory, render_template

from create_video import (
    create_multi_image_video,
    get_audio_duration,
    VALID_TRANSITIONS,
)

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png"}
ALLOWED_AUDIO_EXT = {".mp3", ".wav", ".aac", ".ogg", ".flac", ".m4a"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# In-memory job tracker
jobs: dict = {}

TRANSITION_CATEGORIES = {
    "Professional & Subtle": ["fade", "fadeblack", "fadewhite", "dissolve", "fadegrays"],
    "Wipes": ["wipeleft", "wiperight", "wipeup", "wipedown", "wipetl", "wipetr", "wipebl", "wipebr"],
    "Slides": ["slideleft", "slideright", "slideup", "slidedown"],
    "Covers": ["coverleft", "coverright", "coverup", "coverdown"],
    "Reveals": ["revealleft", "revealright", "revealup", "revealdown"],
    "Geometric": ["circlecrop", "rectcrop", "radial"],
    "Open/Close": ["circleopen", "circleclose", "vertopen", "vertclose", "horzopen", "horzclose"],
    "Slices": ["hlslice", "hrslice", "vuslice", "vdslice"],
    "Smooth": ["smoothleft", "smoothright", "smoothup", "smoothdown"],
    "Diagonal": ["diagtl", "diagtr", "diagbl", "diagbr"],
    "Special Effects": ["pixelize", "distance", "hblur", "squeezeh", "squeezev", "zoomin"],
    "Wind": ["hlwind", "hrwind", "vuwind", "vdwind"],
}


# ── Routes ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Image endpoints ─────────────────────────────────────────────────────

@app.route("/api/upload", methods=["POST"])
def upload_images():
    if "files" not in request.files:
        return jsonify(error="No files provided"), 400

    saved = []
    for f in request.files.getlist("files"):
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in ALLOWED_IMAGE_EXT:
            continue
        # Prefix with uuid to avoid name collisions while keeping original name
        safe_name = f"{uuid.uuid4().hex[:8]}_{f.filename}"
        dest = os.path.join(UPLOAD_DIR, safe_name)
        f.save(dest)
        saved.append(safe_name)

    return jsonify(images=saved)


@app.route("/api/images")
def list_images():
    files = []
    for name in sorted(os.listdir(UPLOAD_DIR)):
        ext = os.path.splitext(name)[1].lower()
        if ext in ALLOWED_IMAGE_EXT:
            files.append(name)
    return jsonify(images=files)


@app.route("/api/images/<filename>")
def serve_image(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/api/images/<filename>", methods=["DELETE"])
def delete_image(filename):
    path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
        return jsonify(ok=True)
    return jsonify(error="Not found"), 404


@app.route("/api/images/clear", methods=["POST"])
def clear_images():
    for name in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR, name)
        if os.path.isfile(path):
            os.remove(path)
    return jsonify(ok=True)


# ── Transitions ─────────────────────────────────────────────────────────

@app.route("/api/transitions")
def list_transitions():
    return jsonify(categories=TRANSITION_CATEGORIES, all=VALID_TRANSITIONS)


# ── Music ───────────────────────────────────────────────────────────────

@app.route("/api/music")
def list_music():
    files = []
    for name in sorted(os.listdir(BASE_DIR)):
        ext = os.path.splitext(name)[1].lower()
        if ext in ALLOWED_AUDIO_EXT:
            files.append(name)
    return jsonify(music=files)


# ── Generate ────────────────────────────────────────────────────────────

def _run_generation(job_id, config):
    """Background worker that creates the video."""
    job = jobs[job_id]
    job_dir = os.path.join(OUTPUT_DIR, f"job_{job_id}")
    images_dir = os.path.join(job_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    try:
        job["status"] = "running"

        # Copy images in user-specified order with numeric prefixes
        image_order = config["images"]
        for i, filename in enumerate(image_order):
            src = os.path.join(UPLOAD_DIR, filename)
            ext = os.path.splitext(filename)[1]
            dst = os.path.join(images_dir, f"{i:04d}{ext}")
            shutil.copy2(src, dst)

        output_path = os.path.join(job_dir, "video.mp4")

        # Resolve audio path
        audio_path = config.get("music", "background_music.mp3")
        if audio_path and not os.path.isabs(audio_path):
            audio_path = os.path.join(BASE_DIR, audio_path)

        # Parse resolution
        res = config.get("resolution", "1920x1080")
        try:
            w, h = map(int, res.lower().split("x"))
        except ValueError:
            w, h = 1920, 1080

        create_multi_image_video(
            image_directory=images_dir,
            audio_path=audio_path,
            output_path=output_path,
            duration_per_image=float(config.get("duration_per_image", 3.5)),
            transition_duration=float(config.get("transition_duration", 1.0)),
            transition_type=config.get("transition", "fade"),
            resolution=(w, h),
            fps=int(config.get("fps", 30)),
            crf=int(config.get("crf", 18)),
            preset=config.get("preset", "slow"),
        )

        job["status"] = "done"
        job["output"] = output_path

    except Exception as exc:
        job["status"] = "error"
        job["error"] = str(exc)


@app.route("/api/generate", methods=["POST"])
def generate_video():
    data = request.get_json(force=True)
    images = data.get("images", [])
    if len(images) < 2:
        return jsonify(error="At least 2 images are required"), 400

    job_id = uuid.uuid4().hex[:12]
    jobs[job_id] = {"status": "pending"}

    thread = threading.Thread(target=_run_generation, args=(job_id, data), daemon=True)
    thread.start()

    return jsonify(job_id=job_id)


@app.route("/api/jobs/<job_id>")
def job_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify(error="Job not found"), 404
    return jsonify(
        status=job["status"],
        error=job.get("error"),
    )


@app.route("/api/download/<job_id>")
def download_video(job_id):
    job = jobs.get(job_id)
    if not job or job["status"] != "done":
        return jsonify(error="Video not ready"), 404
    directory = os.path.dirname(job["output"])
    filename = os.path.basename(job["output"])
    return send_from_directory(directory, filename, mimetype="video/mp4")


# ── Main ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Starting Slideshow Editor on http://localhost:8080")
    app.run(host="0.0.0.0", port=8080, debug=True)
