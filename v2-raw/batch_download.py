#!/usr/bin/env python3
"""Download S02E02 raw-asset videos per raw-assets-index.json; verify SHA-256."""
import sys, os, json, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
BIN = os.path.expanduser("~/workspace/skills/drive-link-kit/bin")

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    only = sys.argv[1:]  # optional path substrings to filter
    index = json.load(open(os.path.join(HERE, "raw-assets-index.json")))
    files = index["files"]
    vids = [f for f in files if f["path"].lower().endswith(".mp4")]
    extra = [f for f in files if f["path"].endswith("IWA-S02E02-Supplied-Transcript.txt")]
    targets = vids + extra
    if only:
        targets = [f for f in targets if any(s in f["path"] for s in only)]
    # small first
    targets.sort(key=lambda f: f["size_bytes"])
    ok, fail = [], []
    for f in targets:
        out = os.path.join(ASSETS, f["path"])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if os.path.exists(out) and os.path.getsize(out) == f["size_bytes"]:
            if sha256_of(out) == f["sha256"]:
                print(f"SKIP verified {f['path']}", flush=True); ok.append(f["path"]); continue
            print(f"re-downloading (hash mismatch) {f['path']}", flush=True)
        gname = f["path"].replace("/", "_").replace(".", "_")
        print(f"DL {f['path']} ({f['size_bytes']} bytes)", flush=True)
        r = subprocess.run([sys.executable, os.path.join(HERE, "dl_drive.py"),
                            f["file_id"], out, gname])
        if r.returncode != 0 or not os.path.exists(out):
            print(f"FAILED download {f['path']}", flush=True); fail.append(f["path"]); continue
        got = sha256_of(out)
        if got != f["sha256"]:
            print(f"HASH MISMATCH {f['path']}", flush=True); fail.append(f["path"]); continue
        print(f"OK {f['path']}", flush=True); ok.append(f["path"])
    print(f"done: {len(ok)} ok, {len(fail)} failed", flush=True)
    if fail:
        print("FAILED:", fail, flush=True); sys.exit(1)

if __name__ == "__main__":
    main()
