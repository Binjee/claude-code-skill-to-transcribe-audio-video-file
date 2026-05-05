import os
import subprocess
import glob
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "change-me-in-production"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ANALYSIS_BASE = os.path.join(os.path.dirname(__file__), ".video-input")
ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm", "mp3", "wav", "m4a"}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

SCRIPT_PATH = os.path.expanduser("~/.claude/skills/video-input/analyze-video.sh")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_latest_analysis():
    """Return the path of the most recent completed analysis directory."""
    pattern = os.path.join(ANALYSIS_BASE, "analysis_*", ".completed")
    completed = sorted(glob.glob(pattern), reverse=True)
    if completed:
        return os.path.dirname(completed[0])
    return None


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("No file selected.")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash(f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    fps = request.form.get("fps", "1")
    model = request.form.get("model", "base")

    env = os.environ.copy()
    env["PATH"] = "/opt/homebrew/bin:" + env.get("PATH", "")
    env["CLAUDE_PROJECT_DIR"] = os.path.dirname(__file__)

    result = subprocess.run(
        [SCRIPT_PATH, filepath, fps, model],
        capture_output=True,
        text=True,
        env=env,
    )

    if result.returncode != 0:
        flash(f"Analysis failed: {result.stderr[-500:]}")
        return redirect(url_for("index"))

    analysis_dir = get_latest_analysis()
    if not analysis_dir:
        flash("Analysis completed but output not found.")
        return redirect(url_for("index"))

    # Read outputs
    transcription = ""
    analysis = ""

    srt_path = os.path.join(analysis_dir, "transcription.srt")
    if os.path.exists(srt_path):
        with open(srt_path) as f:
            transcription = f.read()

    analysis_path = os.path.join(analysis_dir, "analysis.md")
    if os.path.exists(analysis_path):
        with open(analysis_path) as f:
            analysis = f.read()

    # Store paths in session via query param (simple approach)
    return render_template(
        "result.html",
        filename=filename,
        transcription=transcription,
        analysis=analysis,
        analysis_dir=analysis_dir,
    )


@app.route("/download")
def download():
    analysis_dir = request.args.get("dir")
    file_type = request.args.get("type", "analysis")

    if not analysis_dir or not os.path.abspath(analysis_dir).startswith(os.path.abspath(ANALYSIS_BASE)):
        flash("Invalid download path.")
        return redirect(url_for("index"))

    if file_type == "transcription":
        path = os.path.join(analysis_dir, "transcription.srt")
        download_name = "transcription.srt"
    else:
        path = os.path.join(analysis_dir, "analysis.md")
        download_name = "analysis.md"

    if not os.path.exists(path):
        flash("File not found.")
        return redirect(url_for("index"))

    return send_file(path, as_attachment=True, download_name=download_name)


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)
