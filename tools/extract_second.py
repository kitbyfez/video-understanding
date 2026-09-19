#!/usr/bin/env python3
"""Precision frame extraction: dump every native-rate frame for one second.

Usage: extract_second.py <video> <second> [out_dir]
  <second>  integer second, e.g. 20  -> extracts [20.0, 21.0)
Writes PNG frames at native fps/resolution to out_dir (default ./second-<n>/).
"""
import os, sys, subprocess

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    video, second = sys.argv[1], int(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else f"./second-{second}"
    os.makedirs(out, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", str(second), "-t", "1", "-i", video,
        "-vsync", "0", f"{out}/frame-%03d.png",
    ], check=True)
    n = len([f for f in os.listdir(out) if f.endswith(".png")])
    print(f"{n} native-rate frames -> {out}/")

if __name__ == "__main__":
    main()
