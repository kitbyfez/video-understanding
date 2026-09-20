# Video-Understanding Format v1

A machine-readable catalog of a video, designed for agent use. The catalog is
the **index**: one record per second of video, each describing what is visible,
what is said, and how the two relate. It is not a summary — it is a lookup
structure. Precision work (frame-exact cuts) resolves a second through this
index first, then examines full-rate frames only inside that second.

The only consumer of this format is an agent. It is optimized for grep,
`jq`, and programmatic lookup — not for human reading. Human-readable
renderings (timelines, Pages demos) are derived views, never the source of truth.

## File layout per video

```
<catalog-id>/
  catalog.json        # the index (this spec)
  transcript.json     # word-level transcript (also embedded in catalog.json)
  frames/
    f001.jpg          # 1 fps reference frames, second-aligned (f001 = 0.0-1.0s)
    ...
  precision/
    <t0>-<t1>/        # on-demand full-rate frame dumps for precision cuts
```

## catalog.json

```jsonc
{
  "format": "video-understanding/1",
  "video": {
    "id": "iwa-s02e01-trailer-v2",       // stable catalog id
    "source_file": "IWA-S02E01-Trailer-v2.mp4",
    "sha256": "…",                        // of the analyzed file
    "duration_s": 37.512,
    "fps": 30,                            // native frame rate
    "width": 1350,
    "height": 1350,
    "analyzed_at": "2026-09-19"
  },
  "transcript": {
    "engine": "faster-whisper/base",
    "words": [
      { "w": "Hey,", "start": 0.0, "end": 0.7 }
      // …one entry per word, time in seconds
    ]
  },
  "seconds": [
    {
      "t": 0,                             // integer second; covers [t, t+1)
      "frame": "frames/f001.jpg",          // 1fps reference frame
      "visual": {
        "summary": "…",                   // 1-2 sentences, concrete
        "subjects": ["…"],                // named entities visible
        "setting": "…",                   // where / what kind of shot
        "on_screen_text": ["…"],          // literal text visible, else []
        "transition": "none|cut|fade|dissolve|wipe|unknown",
        "camera": "static|pan|tilt|zoom|moving|unknown"
      },
      "narration": ["Hey,"],              // words overlapping [t, t+1)
      "match": "…"                        // does the visual illustrate the narration?
    }
    // …one entry per second, t = 0 .. ceil(duration)-1
  ]
}
```

## Rules

1. **One record per second, no gaps.** Every integer second in
   `[0, ceil(duration_s))` has a record, even silence / stills.
2. **Describe, don't interpret.** `visual.summary` names concrete visible
   things. No marketing language, no inferred intent.
3. **Narration is derived from word times**, not re-typed. Words overlapping
   `[t, t+1)` go in `narration`, in order.
4. **Corrections beat transcription.** If the STT engine mishears a proper
   noun the agent knows (e.g. "Bila" for "Bela"), the catalog stores the
   corrected word. Note corrections in `transcript.corrections`.
5. **Frames are evidence, not decoration.** `frames/fNNN.jpg` is the exact
   frame the description was written from. Keep them; they are the audit
   trail.
6. **Precision cuts never scan.** To cut at frame precision: look up the
   second in `seconds`, then dump full-rate frames for that second into
   `precision/<t0>-<t1>/` and pick the frame there. The catalog is the
   dictionary; full-rate frames are the magnifying glass.

## Versioning

Breaking changes bump the number after `video-understanding/`. v1 readers
must tolerate unknown fields (additive changes don't bump).

## Ledger (additive, v1-compatible)

`vu` tracks workflow state per record. v1 readers tolerate unknown fields, so
these do not bump the format version:

- `described: bool`, `described_by`, `described_at`
- `annotated: bool`, `annotation` (free-text review notes), `annotated_by`,
  `annotated_at`

`narration` is always derived from transcript word overlap at write time,
never accepted from the writer.
