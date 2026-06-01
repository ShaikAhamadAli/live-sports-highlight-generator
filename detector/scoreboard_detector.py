# detector/scoreboard_detector.py
import cv2
import numpy as np

def read_sample_frame(video_path, t=0.5):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, int(t * 1000))
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    return frame

def scoreboard_changed(prev_path, curr_path, roi=(0,0,300,80), diff_threshold=1000):
    """
    roi: (x, y, w, h) - tune this to your broadcast scoreboard area.
    Returns True if pixel-difference in ROI exceeds threshold.
    """
    f1 = read_sample_frame(prev_path)
    f2 = read_sample_frame(curr_path)
    if f1 is None or f2 is None:
        return False, 0.0

    x, y, w, h = roi
    h1 = cv2.cvtColor(f1[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
    h2 = cv2.cvtColor(f2[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)

    # Resize to same size (safety)
    h1 = cv2.resize(h1, (w, h))
    h2 = cv2.resize(h2, (w, h))

    diff = cv2.absdiff(h1, h2)
    _, diffb = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    diff_count = int(np.sum(diffb) / 255)
    return (diff_count > diff_threshold), float(diff_count)
