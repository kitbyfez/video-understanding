# video-understanding

Machine-readable video understanding for agents. One mandatory 1fps catalog
pass per video produces a per-second index of what's visible and what's said;
frame-precision cuts resolve through that index instead of re-scanning.

The format is designed for the agent, not for people. People get derived
views — like the [timeline demo](https://kitbyfez.github.io/video-understanding/)
built from the example catalog.

- [`spec/FORMAT.md`](spec/FORMAT.md) — the catalog data format (v1)
- [`workflow/WORKFLOW.md`](workflow/WORKFLOW.md) — the mandatory pass + precision procedure
- [`examples/`](examples/) — real catalogs; each is a complete worked example

## Example

[`examples/iwa-s02e01-trailer-v2/`](examples/iwa-s02e01-trailer-v2/) is the
first catalog: a 37.5s trailer, 38 per-second records, word-level transcript,
reference frames. Rendered as a timeline
[here](https://kitbyfez.github.io/video-understanding/).

## CLI

[`vu`](./vu) is the command-line interface and the **only writer** of
`catalog.json`. Agents and humans change the catalog exclusively through `vu`,
so every write is schema-validated, narration is derived deterministically
from transcript word overlap, and writes are atomic (flock + temp + rename).

- `vu ingest VIDEO [-o DIR]` — probe, sha256, faster-whisper word-level
  transcript, 1fps frames, catalog skeleton with derived narration
- `vu status [DIR]` — describe/annotate completeness + missing ranges
  (`--json` for agents)
- `vu record describe --second N ...` / `--batch FILE` — validated write of
  visual + match for one second (or many); skips already-described unless
  `--force`
- `vu record annotate --second N --notes ...` — attach review notes
- `vu frame --second N` / `vu sheet --range A-B --cols 4` — PNG evidence,
  generated on demand (never pre-baked)
- `vu validate` / `vu migrate`

Python 3, stdlib-only (Pillow needed only for contact sheets). Requires
`ffmpeg`/`ffprobe`; transcription uses faster-whisper (auto-detects
`~/workspace/whisper-env`, else `--whisper-python`).
