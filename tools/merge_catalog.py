#!/usr/bin/env python3
"""Merge worker T-section outputs into catalog.json (video-understanding/1)."""
import json, re, sys, hashlib, os

UNDER = os.path.expanduser("~/workspace/iwa-trailer/understanding")
REPO_EX = os.path.expanduser("~/workspace/video-understanding/examples/iwa-s02e01-trailer-v2")

def parse_worker(text):
    """Parse ## T{n} sections -> {t: {visual, narration, match}}."""
    out = {}
    # split on ## T headers
    parts = re.split(r"^##\s+T(\d+).*$", text, flags=re.M)
    # parts[0] = preamble, then alternating t, body
    for i in range(1, len(parts), 2):
        t = int(parts[i])
        body = parts[i + 1]
        def field(name):
            m = re.search(rf"^-\s*{name}:\s*(.+?)(?=^-\s*\w+:|\Z)", body, flags=re.M | re.S)
            return m.group(1).strip().replace("\n", " ") if m else ""
        out[t] = {
            "visual": field("Visual"),
            "narration": field("Narration"),
            "match": field("Match"),
        }
    return out

def main(worker_files):
    merged = {}
    for f in worker_files:
        merged.update(parse_worker(open(f).read()))

    words = json.load(open(f"{UNDER}/trailer-words.json"))
    # words: [start, end, word] — apply known STT corrections
    corrections = {"Bila": "Bela"}
    words = [[s, e, corrections.get(w, w)] for s, e, w in words]
    transcript_corrections = [
        {"from": k, "to": v, "reason": "proper noun per recorded script"}
        for k, v in corrections.items()
    ]
    transcript_words = [{"w": w, "start": s, "end": e} for s, e, w in words]

    seconds = []
    import math
    duration = 37.512
    for t in range(math.ceil(duration)):
        desc = merged.get(t, {"visual": "", "narration": "", "match": ""})
        narr = [w for s, e, w in words if s < t + 1 and e > t]
        # naive visual structuring: keep free text in summary; fields best-effort
        seconds.append({
            "t": t,
            "frame": f"frames/f{t+1:03d}.jpg",
            "visual": {
                "summary": desc["visual"],
                "subjects": [],
                "setting": "",
                "on_screen_text": [],
                "transition": "unknown",
                "camera": "unknown",
            },
            "narration": narr,
            "match": desc["match"],
        })

    video_path = os.path.expanduser("~/workspace/iwa-trailer/IWA-S02E01-Trailer-v2.mp4")
    h = hashlib.sha256()
    with open(video_path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)

    catalog = {
        "format": "video-understanding/1",
        "video": {
            "id": "iwa-s02e01-trailer-v2",
            "source_file": "IWA-S02E01-Trailer-v2.mp4",
            "sha256": h.hexdigest(),
            "duration_s": duration,
            "fps": 30,
            "width": 1350,
            "height": 1350,
            "analyzed_at": "2026-09-19",
        },
        "transcript": {
            "engine": "faster-whisper/base",
            "corrections": transcript_corrections,
            "words": transcript_words,
        },
        "seconds": seconds,
    }
    os.makedirs(REPO_EX, exist_ok=True)
    json.dump(catalog, open(f"{REPO_EX}/catalog.json", "w"), indent=1)
    # copy frames into example
    import shutil
    fdest = f"{REPO_EX}/frames"
    os.makedirs(fdest, exist_ok=True)
    for t in range(math.ceil(duration)):
        src = f"{UNDER}/frames/f{t+1:03d}.jpg"
        if os.path.exists(src):
            shutil.copy(src, f"{fdest}/f{t+1:03d}.jpg")
    print(f"catalog: {len(seconds)} seconds -> {REPO_EX}/catalog.json")

if __name__ == "__main__":
    main(sys.argv[1:])
