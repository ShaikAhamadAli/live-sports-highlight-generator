# main.py
import os
import time
from detector.audio_detector import detect_audio_spike
from detector.scoreboard_detector import scoreboard_changed
import subprocess

SEG_DIR = "segments"
CLIP_DIR = "clips"
os.makedirs(CLIP_DIR, exist_ok=True)

def ffmpeg_trim(source_file, start_sec, duration_sec, out_file):
    """
    Use ffmpeg CLI to trim - lightweight and fast.
    """
    cmd = [
        "ffmpeg", "-y", "-ss", str(start_sec), "-i", source_file,
        "-t", str(duration_sec), "-c", "copy", out_file
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def process_once():
    files = sorted([f for f in os.listdir(SEG_DIR) if f.endswith(".mp4")])
    for i in range(1, len(files)):
        prev_seg = os.path.join(SEG_DIR, files[i-1])
        curr_seg = os.path.join(SEG_DIR, files[i])

        audio_hit, audio_ratio = detect_audio_spike(curr_seg)
        score_hit, diff_count = scoreboard_changed(prev_seg, curr_seg)

        print(f"[{files[i]}] audio={audio_hit}({audio_ratio:.2f}) score_change={score_hit}({diff_count:.0f})")

        # Fusion rule: either audio spike OR scoreboard change (use OR for fewer misses)
        if audio_hit or score_hit:
            out_name = f"highlight_{files[i]}"
            out_path = os.path.join(CLIP_DIR, out_name)
            # trim the current segment (start at 0) for 12 seconds; you can combine prev+curr later
            ffmpeg_trim(curr_seg, start_sec=0, duration_sec=12, out_file=out_path)
            print("Created highlight:", out_path)

if __name__ == "__main__":
    # Poll the segments directory until user stops the script
    print("Starting processor. Press Ctrl+C to stop.")
    seen = set()
    try:
        while True:
            process_once()
            time.sleep(2)
    except KeyboardInterrupt:
        print("Stopped.")
