import os
import subprocess
from flask import Flask, render_template, request, send_from_directory
from demucs import separate

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded", 400
        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # 使用 demucs 处理
        subprocess.run([
            "demucs", "--two-stems=vocals", "--out", OUTPUT_FOLDER, filepath
        ])

        # demucs 输出路径
        filename = os.path.splitext(file.filename)[0]
        vocal_path = os.path.join(OUTPUT_FOLDER, "separated/htdemucs", filename, "vocals.wav")
        cleaned_path = os.path.join(OUTPUT_FOLDER, f"{filename}_denoised.wav")

        # 用 ffmpeg 重采样到 16kHz, mono
        subprocess.run([
            "ffmpeg", "-y", "-i", vocal_path, "-ar", "16000", "-ac", "1", cleaned_path
        ])

        return f'<h3>✅ 处理完成: <a href="/download/{os.path.basename(cleaned_path)}">下载音频</a></h3>'

    return render_template("index.html")

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
