# detector/audio_detector.py
import numpy as np
import librosa

def detect_audio_spike(video_path, threshold=2.0):
    """
    Returns (bool, ratio). True if a loud spike (cheer) appears in the segment.
    """
    try:
        y, sr = librosa.load(video_path, sr=None, mono=True)
    except Exception as e:
        print("audio load error:", e)
        return False, 0.0

    frame_len, hop_len = 2048, 512
    if len(y) < frame_len:
        return False, 0.0

    energy = np.array([
        np.sum(np.abs(y[i:i+frame_len])**2)
        for i in range(0, len(y) - frame_len, hop_len)
    ])
    avg_energy = np.mean(energy) + 1e-9
    peak = np.max(energy)
    ratio = peak / avg_energy
    return (ratio > threshold), float(ratio)
