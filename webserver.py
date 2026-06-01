from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import shutil

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
SEGMENT_FOLDER = "segments"
CLIP_FOLDER = "clips"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SEGMENT_FOLDER, exist_ok=True)
os.makedirs(CLIP_FOLDER, exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["video"]
    filepath = os.path.join(UPLOAD_FOLDER, "input.mp4")
    file.save(filepath)

    # Clear old data
    shutil.rmtree(SEGMENT_FOLDER, ignore_errors=True)
    shutil.rmtree(CLIP_FOLDER, ignore_errors=True)
    os.makedirs(SEGMENT_FOLDER)
    os.makedirs(CLIP_FOLDER)

    # Split video into segments
    subprocess.run([
        "ffmpeg", "-i", filepath,
        "-c", "copy", "-map", "0",
        "-segment_time", "10",
        "-f", "segment",
        f"{SEGMENT_FOLDER}/seg_%03d.mp4"
    ])

    # Run highlight generation
    subprocess.run(["python", "main.py"])

    return {"message": "Video processed successfully"}


@app.route("/api/clips")
def list_clips():
    files = [f for f in os.listdir(CLIP_FOLDER) if f.endswith(".mp4")]
    return {"clips": files}


@app.route("/clips/<path:filename>")
def serve_clip(filename):
    return send_from_directory(CLIP_FOLDER, filename)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
