#!/usr/bin/env python3
"""Download one Drive file via drive-link-kit: begin_download -> grant (0600) -> stream -> delete grant."""
import sys, os, json, subprocess, tempfile

BIN = os.path.expanduser("~/workspace/skills/drive-link-kit/bin")
GRANT_DIR = os.path.expanduser("~/workspace/video-understanding/v2-raw/grants")
sys.path.insert(0, BIN)
import dlkit

def main():
    file_id, output, gname = sys.argv[1], sys.argv[2], sys.argv[3]
    grant_path = os.path.join(GRANT_DIR, gname + ".grant.json")
    sid = dlkit.mcp_initialize_pat()
    res = dlkit.mcp_call_pat("begin_download", {"file_id": file_id}, session_id=sid)
    text = res.get("content", [{}])[0].get("text", "{}")
    grant = json.loads(text)
    # atomic 0600 write
    fd, tmp = tempfile.mkstemp(dir=GRANT_DIR, prefix=".tmp-")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(grant, f)
        os.chmod(tmp, 0o600)
        os.replace(tmp, grant_path)
    finally:
        try: os.unlink(tmp)
        except OSError: pass
    print("grant saved", flush=True)
    try:
        r = subprocess.run(
            [os.path.join(BIN, "drive_transfer.py"), "--grant-file", grant_path,
             "download", "--output", output],
            timeout=6 * 3600)
        print("transfer exit:", r.returncode, flush=True)
        return r.returncode
    finally:
        try: os.unlink(grant_path)
        except OSError: pass

if __name__ == "__main__":
    sys.exit(main())
