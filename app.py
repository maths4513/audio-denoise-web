import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from tasks import denoise_task, celery

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    task = denoise_task.delay(file.filename)
    return jsonify({"task_id": task.id, "raw_file": file.filename})

@app.route("/status/<task_id>")
def task_status(task_id):
    task = denoise_task.AsyncResult(task_id)
    if task.state == "PENDING":
        return jsonify({"state": "pending"})
    elif task.state == "PROGRESS":
        return jsonify({"state": "progress", "meta": task.info})
    elif task.state == "SUCCESS":
        result = task.result
        return jsonify({
            "state": "done",
            "file": os.path.basename(result["output_file"]),
            "wave_images": result["wave_images"]
        })
    else:
        return jsonify({"state": task.state, "meta": str(task.info)})

@app.route("/download/<filename>")
def download(filename):
    # 自动选择 uploads 和 output 目录
    if os.path.exists(os.path.join(OUTPUT_FOLDER, filename)):
        return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=False)
    elif os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)
    else:
        return "File not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
