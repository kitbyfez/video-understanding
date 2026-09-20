#!/usr/bin/env python3
"""Run `vu ingest` for each downloaded raw-asset video into v2-raw/<slug>/."""
import sys, os, json, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
VU = os.path.expanduser("~/workspace/video-understanding/vu")

def slugify(path):
    s = path.lower().replace("interaction videos/videos/", "iv-") \
                    .replace("branding/", "branding-") \
                    .replace("iwa-s02e02-original-recording-2026-09-16.mp4", "original-recording") \
                    .replace(".mp4", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def main():
    only = sys.argv[1:]
    index = json.load(open(os.path.join(HERE, "raw-assets-index.json")))
    vids = [f for f in index["files"] if f["path"].lower().endswith(".mp4")]
    vids.sort(key=lambda f: f["size_bytes"])
    for f in vids:
        slug = slugify(f["path"])
        if only and not any(s in slug or s in f["path"] for s in only):
            continue
        src = os.path.join(ASSETS, f["path"])
        if not os.path.exists(src):
            print(f"SKIP (not downloaded) {slug}", flush=True); continue
        out = os.path.join(HERE, slug)
        cat = os.path.join(out, "catalog.json")
        if os.path.exists(cat):
            print(f"SKIP (exists) {slug}", flush=True); continue
        print(f"INGEST {slug} <- {f['path']}", flush=True)
        r = subprocess.run([VU, "ingest", src, "-o", out, "--id", slug],
                           capture_output=True, text=True, timeout=12 * 3600)
        print(r.stdout[-800:], flush=True)
        if r.returncode != 0:
            print(f"INGEST FAILED {slug}: {r.stderr[-800:]}", flush=True)
        else:
            print(f"INGEST OK {slug}", flush=True)

if __name__ == "__main__":
    main()
