import os, subprocess
from celery import Celery

celery = Celery(__name__, broker=os.getenv("CELERY_BROKER_URL"), backend=os.getenv("CELERY_RESULT_BACKEND"))

@celery.task(bind=True)
def denoise_task(self, filename):
    uploads_dir = "uploads"
    output_dir = "output"

    filepath = os.path.join(uploads_dir, filename)
    self.update_state(state='PROGRESS', meta={'msg': 'Running Demucs...'})

    subprocess.run(["demucs", "--two-stems=vocals", "--out", output_dir, filepath])

    base = os.path.splitext(filename)[0]
    vocal_path = os.path.join(output_dir, "separated/htdemucs", base, "vocals.wav")
    cleaned_path = os.path.join(output_dir, f"{base}_denoised.wav")

    self.update_state(state='PROGRESS', meta={'msg': 'Running ffmpeg (resample)...'})
    subprocess.run(["ffmpeg", "-y", "-i", vocal_path, "-ar", "16000", "-ac", "1", cleaned_path])

    return {"status": "done", "output_file": cleaned_path}
