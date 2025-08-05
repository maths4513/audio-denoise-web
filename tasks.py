import os
import subprocess
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from celery import Celery

celery = Celery(__name__, broker=os.getenv("CELERY_BROKER_URL"), backend=os.getenv("CELERY_RESULT_BACKEND"))

def plot_waveform_and_spectrogram(audio_path, output_prefix):
    """生成波形图和频谱图并保存为 PNG 文件"""
    y, sr = librosa.load(audio_path, sr=None)

    # 1. 波形图
    plt.figure(figsize=(10, 3))
    librosa.display.waveshow(y, sr=sr)
    plt.title(f"Waveform: {os.path.basename(audio_path)}")
    plt.tight_layout()
    wave_path = f"{output_prefix}_wave.png"
    plt.savefig(wave_path)
    plt.close()

    # 2. 频谱图 (Mel Spectrogram)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    S_dB = librosa.power_to_db(S, ref=np.max)
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel', fmax=8000)
    plt.colorbar(format="%+2.0f dB")
    plt.title("Mel Spectrogram")
    plt.tight_layout()
    spec_path = f"{output_prefix}_spec.png"
    plt.savefig(spec_path)
    plt.close()

    return wave_path, spec_path

@celery.task(bind=True)
def denoise_task(self, filename):
    uploads_dir = "uploads"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(uploads_dir, filename)

    # 1️⃣ 原始音频的波形和频谱
    raw_wave, raw_spec = plot_waveform_and_spectrogram(filepath, os.path.join(output_dir, f"{filename}_raw"))

    # 2️⃣ Demucs 去噪
    self.update_state(state='PROGRESS', meta={'msg': 'Running Demucs...'})
    subprocess.run(["demucs", "--two-stems=vocals", "--out", output_dir, filepath], check=True)

    base = os.path.splitext(filename)[0]
    vocal_path = os.path.join(output_dir, "separated/htdemucs", base, "vocals.wav")
    cleaned_path = os.path.join(output_dir, f"{base}_denoised.wav")

    # 3️⃣ ffmpeg 重采样到 16kHz mono
    self.update_state(state='PROGRESS', meta={'msg': 'Running ffmpeg...'})
    subprocess.run(["ffmpeg", "-y", "-i", vocal_path, "-ar", "16000", "-ac", "1", cleaned_path], check=True)

    # 4️⃣ 降噪后音频的波形和频谱
    denoise_wave, denoise_spec = plot_waveform_and_spectrogram(cleaned_path, os.path.join(output_dir, f"{filename}_denoised"))

    return {
        "status": "done",
        "output_file": cleaned_path,
        "wave_images": {
            "raw_wave": os.path.basename(raw_wave),
            "raw_spec": os.path.basename(raw_spec),
            "denoise_wave": os.path.basename(denoise_wave),
            "denoise_spec": os.path.basename(denoise_spec)
        }
    }
